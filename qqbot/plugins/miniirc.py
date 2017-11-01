# -*- coding: utf-8 -*-

version = '1.0.1'

import sys, os.path as op
p = op.dirname(op.dirname(op.dirname(op.abspath(__file__))))
if p not in sys.path:
    sys.path.insert(0, p)
    
import re, time, socket

from qqbot.mysocketserver import MySocketServer
from qqbot.common import STR2BYTES, BYTES2STR, StartDaemonThread
from qqbot.utf8logger import ERROR, DEBUG
from qqbot.mainloop import Put

def onPlug(bot):
    host = '127.0.0.1'
    port = bot.conf.pluginsConf.get(__name__, 6667)
    server = IRCServer(host, port, bot)
    StartDaemonThread(server.Run)

def onUnplug(bot):
    ERROR('本插件（%s）不支持 unplug ，QQBot将停止运行', __name__)
    bot.Stop()

class IRCServer(MySocketServer):
    def __init__(self, ip, port, bot):
        MySocketServer.__init__(self, ip, port, 'QQBot-IRC-SERVER')
        self.createtime = time.asctime(time.localtime())
        self.bot = bot
    
    # child thread 01
    def onAccept(self, sock, addr):
        Put(Client, sock, addr, self)

class Client(object):
    def __init__(self, sock, addr, server):
        self.sock = sock
        self.addr = addr
        self.name = 'IRC-CLIENT<%s/%s>' % addr
        self.server = server
        self.bot = server.bot
        self.servername = self.server.name
        self.handler = self.waitNick
        self.sock.settimeout(5)
        StartDaemonThread(self.recvLoop)
        DEBUG('%s connected', self.name)

    # child thread 02
    def recvLoop(self):
        buf = b''
        while True:
            try:
                data = self.sock.recv(8192)
            except socket.timeout:
                if self.handler is None:
                    DEBUG('END IRC-CLIENT\'S RECV LOOP')
                    break
            except Exception as e:
                ERROR('在接收来自 %s 的数据时发送错误，%s', self.name, e)
                if self.handler:
                    Put(self.close)
                break
            else:
                if data:
                    lines = (buf + data).split(b'\n')
                    buf = lines.pop()
                    if lines:
                        Put(self.parseLines, lines)
                else:
                    Put(self.close)
                    break

    def parseLines(self, lines):
        if self.handler is None:
            return

        for line in lines:
            line = line.rstrip(b'\r').lstrip()

            if not line:
                continue

            try:
                line = BYTES2STR(line)
            except Exception as e:
                DEBUG('%r\n%r', e, line)
                continue

            head, sep, tail = line.partition(' :')
            params = head.rstrip().split()
            command, params = params[0].upper(), params[1:]
            DEBUG('%s <== %s: %r', self.servername, self.name, line)
            DEBUG('%r, %r, %r', command, params, tail)
            self.handler(command, params, tail)
        
    # ==> NICK hcj
    # <== :*!*@hidden NICK :hcj
    def waitNick(self, command, params, tail):
        if command != 'NICK' or not params:
            return
        self.send('*!*@hidden', 'NICK', [], params[0])
        self.nick = params[0]
        self.handler = self.waitUser
    
    # ==> USER hcj 0 * :hcj
    # <== :qqbot-irc-server 001 hcj :Welcome to QQBOT IRC Server hcj!hcj@hidden
    # <== :qqbot-irc-server 002 hcj :Your host is qqbot-irc-server, running version 1.1.1
    # <== :qqbot-irc-server 003 hcj :This server was created Fri Jun 23 17 at 23:53:34 GMT
    # <== :qqbot-irc-server 004 hcj :qqbot-irc-server 1.1.1 * *
    # <== :hcj!hcj@hidden NICK :realnick
    def waitUser(self, command, params, tail):
        if command != 'USER' or (not params):
            return
        self.user = params[0]
        self.realname = tail
        prefix = '%s!%s@hidden' % (self.nick, self.user)
        self.send(
            self.servername, '001', [self.nick],
            'Welcome to QQBOT IRC Server %s' % prefix
        )
        self.send(
            self.servername, '002', [self.nick],
            'Your host is %s, running version %s' % (self.servername, version)
        )
        self.send(
            self.servername, '003', [self.nick],
            'This server was created %s' % self.server.createtime
        )
        self.send(
            self.servername, '004', [self.nick],
            '%s %s * *' % (self.servername, version)
        )    
        self.realnick = '$' + removeSpecial(self.bot.session.nick)
        self.send(prefix, 'NICK', [], self.realnick)
        self.nick = self.realnick
        self.prefix = '%s!%s@hidden' % (self.nick, self.user)
        # self.bot.Update('group')
        # self.bot.Update('buddy')
        self.channels = ContactList(self.bot.List('group'), self.bot.List('discuss'))
        self.buddies = ContactList(self.bot.List('buddy'))
        self.bot.AddSlot(self.onQQMessage)
        self.handler = self.onCommand

    def onCommand(self, command, params, tail):
        func = getattr(self, 'on'+command.lower().title(), None)
        if func:
            func(params, tail)
    
    # ==> QUIT :WeeChat 1.0.1
    def onQuit(self, params, tail):
        self.close()
    
    # ==> PING 127.0.0.1
    # <== :qqbot-irc-server PONG qqbot-irc-server :127.0.0.1
    def onPing(self, params, tail):
        self.send(self.servername, 'PONG', [self.servername], self.server.host)
    
    # ==> LIST
    # <== :qqbot-irc-server 322 hcj #myclass 1 :欢迎来到 #myclass
    # <== :qqbot-irc-server 322 hcj #mygroup 1 :欢迎来到 #mygroup
    # <== :qqbot-irc-server 323 hcj :End of LIST
    def onList(self, params, tail):
        for nick in self.channels.nicknames:
            self.send(self.servername, '322', [self.nick, nick, '1'], '欢迎来到 '+nick)
        self.send(self.servername, '323', [self.nick], 'End of LIST')

    # ==> JOIN connie                                          ..
    # <== :hcj!hcj@hidden JOIN :#connie
    # <== :qqbot-irc-server 332 hcj #connie :欢迎来到 #connie
    # <== :qqbot-irc-server 353 hcj = #connie :Eva hcj
    # <== :qqbot-irc-server 366 hcj #connie :End of NAMES list
    def onJoin(self, params, tail):
        if not params:
            self.notEnoughParams('JOIN')
            return

        nick = params[0] if params[0].startswith('#') else ('#'+params[0])
        channel = self.channels.get(nick)
        if channel is None:
            self.send(self.servername, '403', [nick], 'No such channel')
            return
        self.join(channel)

    def join(self, channel):
        nick = channel.nick
        channel.membNicks.add(self.nick)
        self.send(self.prefix, 'JOIN', [], nick)
        self.send(self.servername, '332', [self.nick, nick], '欢迎来到 '+nick)
        membNicks = list(channel.membNicks)
        step = 5
        for i in range(0, len(membNicks), step):               
            s = ' '.join(membNicks[i:i+step])
            self.send(self.servername, '353', [self.nick, '=', nick], s)
        self.send(self.servername, '366', [self.nick, nick], 'End of NAMES list')
    
    # ==> PART #connie :WeeChat 1.0.1
    # <== :hcj!hcj@hidden PART #connie :WeeChat 1.0.1
    def onPart(self, params, tail):
        if not params:
            self.notEnoughParams('PART')
            return
 
        nick = params[0] if params[0].startswith('#') else ('#'+params)
        channel = self.channels.get(nick)
        if (channel is None) or (self.nick not in channel.membNicks):
            self.send(self.servername, '403', [nick], 'No such channel')
            return
        self.part(channel, tail)
    
    def part(self, channel, tail='x'):
        channel.membNicks.remove(self.nick)
        self.send(self.prefix, 'PART', [channel.nick], tail)
    
    # ==> PRIVMSG Eva :nihao
    def onPrivmsg(self, params, tail):
        if not params or not tail:
            self.notEnoughParams('PRIVMSG')
            return
        
        nick, msg = params[0], tail
        if nick.startswith('#'):
            tar = self.channels.get(nick)
        else:
            tar = self.buddies.get(nick)
        if tar is None:
            self.send(self.servername, '401', [nick], 'No such nick/channel')
            return
        self.bot.SendTo(tar, msg)
    
    def onQQMessage(self, bot, contact, member, content):
        if self.handler is None:
            return

        if bot.isMe(contact, member):
            return

        content = content.replace('\r', '').replace('\n', ' ')

        if contact.ctype == 'buddy':
            buddy = self.buddies.get(uin=contact.uin)
            if buddy is None:
                self.buddies.add(contact)
                buddy = contact
            # <== :Eva!2571046716@qqbot PRIVMSG hcj :ghhhhh
            prefix = '%s!%s@qqbot' % (buddy.nick, buddy.uin)
            self.send(prefix, 'PRIVMSG', [self.nick], content)

        elif contact.ctype in ('group', 'discuss'):
            channel = self.channels.get(uin=contact.uin)
            if channel is None:
                self.channels.add(contact)
                channel = contact
            if self.nick not in channel.membNicks:
                self.join(channel)
            nick = removeSpecial(member.name)
            prefix = '%s!%s@qqbot' % (nick, member.uin)
            if nick not in channel.membNicks:                
                channel.membNicks.add(nick)
                # <== :Eva!1921001770@qqbot JOIN :#connie
                self.send(prefix, 'JOIN', [], channel.nick)
    
            # <== :Eva!2571046716@qqbot PRIVMSG #connie :ghjjgg
            self.send(prefix, 'PRIVMSG', [channel.nick], content)

    def notEnoughParams(self, command):
        self.send(self.servername, '461', [command], 'Not enough parameters')
        
    def send(self, prefix, command, params, tail):        
        words = [':'+prefix, command.upper()] + params + [':'+tail]
        msg = ' '.join(words)
        try:
            self.sock.sendall(STR2BYTES(msg)+b'\r\n')
        except socket.timeout:
            ERROR('在向 %s 发送数据时出现 %s', self.name, 'SOCKET-TIMEOUT')
        except socket.error:
            ERROR('在向 %s 发送数据时出现 %s', self.name, 'SOCKET-ERROR')
            self.close()
        else:            
            DEBUG('%s ==> %s: %r', self.servername, self.name, msg)
    
    def close(self):
        if self.handler is None:
            return

        self.handler = None
        self.sock.close()
        DEBUG('%s disconnected', self.name)

specials = re.compile(r'[!$#: ]')

def removeSpecial(s):
    return '*'.join(specials.split(s))

class ContactList(object):
    def __init__(self, contacts=None, discusses=None):
        self.nicks = {}     # nick ==> contact
        self.uins = {}      # uin ==> contact
        if contacts:
            for contact in contacts:
                self.add(contact)
        if discusses:
            for d in discusses:
                self.add(d)
    
    def add(self, contact):
        if contact.uin in self.uins:
            return
        self.uins[contact.uin] = contact
        name = removeSpecial(contact.name)
        if contact.ctype == 'group':
            name = '#' + name
        elif contact.ctype == 'discuss':
            name = '#!' + name
        nick = name
        i = 1
        while nick in self.nicks:
            nick = name + str(i)
            i += 1
        self.nicks[nick] = contact
        contact.__dict__['nick'] = nick
        if contact.ctype in ('group', 'discuss'):
            contact.__dict__['membNicks'] = set()
    
    def get(self, nick=None, uin=None):
        if nick is not None:
            return self.nicks.get(nick, None)
        else:
            return self.uins.get(uin, None)
    
    @property
    def nicknames(self):
        return list(self.nicks.keys())

if __name__ == '__main__':
    from qqbot.utf8logger import SetLogLevel; SetLogLevel('debug')
    from qqbot.mainloop import MainLoop
    StartDaemonThread(IRCServer('127.0.0.1', 6667).Run)
    MainLoop()
