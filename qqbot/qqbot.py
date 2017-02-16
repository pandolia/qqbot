#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
QQBot   -- A conversation robot base on Tencent's SmartQQ
Website -- https://github.com/pandolia/qqbot/
Author  -- pandolia@yeah.net
"""

import random, time, sys, subprocess

from qconf import QConf
from utf8logger import INFO, WARN, DEBUG
from qsession import QLogin, QSession
from qterm import QTermServer
from common import Utf8Partition
from qcontacts import QContact
from messagefactory import MessageFactory, Message

class QQBot(MessageFactory):
    def __init__(self, qq=None, user=None, conf=None, ai=None):
        MessageFactory.__init__(self)
        self.conf = conf if conf else QConf(qq, user)
        self.conf.Display()
        ai = ai if ai else BasicAI()
        termServer = QTermServer(self.conf.termServerPort)

        self.On('qqmessage',   ai.OnQQMessage)          # main thread
        self.On('polltimeout', ai.OnPollTimeout)        # main thread
        self.On('termmessage', ai.OnTermMessage)        # main thread

        self.On('pollcomplete',  QQBot.onPollComplete)  # main thread
        self.On('fetchcomplete', QQBot.onFetchComplete) # main thread

        self.AddGenerator(self.pollForever)             # child thread 1 
        self.AddGenerator(self.fetchForever)            # child thread 2
        self.AddGenerator(termServer.Run)               # child thread 3
    
    def Login(self):
        session, contacts = QLogin(conf=self.conf)
        
        self.Get = contacts.Get                         # main thread
        self.List = contacts.List                       # main thread
        self.assignContacts = contacts.Assign           # main thread
        self.send = session.Send                        # main thread
        
        self.poll = session.Copy().Poll                 # child thread 1
        self.fetch = session.Copy().Fetch               # child thread 2
    
    # send buddy|group|discuss x|uin=x|qq=x|name=x content
    # Send('buddy', '1234', 'hello')
    # Send('buddy', 'uin=1234', 'hello')
    # Send('buddy', uin='1234', content='hello')
    def Send(self, ctype, *args, **kw):
        if len(args) + len(kw) != 2:
            raise TypeError('Wrong arguments!')
        
        if len(args) < 2 and 'content' not in kw:
            raise TypeError('Wrong arguments!')
        
        if len(args) == 2:
            content, args = args[1], args[:1]
        else:
            content = kw.pop('content')
        
        result = []
        if content:
            for contact in self.Get(ctype, *args, **kw):
                result.append(self.SendTo(contact, content))
        return result
    
    def SendTo(self, contact, content):
        if content:        
            content = str(content)
            result = '向 %s 发消息成功' % str(contact)
            while content:
                front, content = Utf8Partition(content, 600)
                self.send(contact.ctype, contact.uin, front)
                INFO(result)            
            return result

    def pollForever(self):
        try:
            while True:
                yield Message('pollcomplete', result=self.poll())
        finally:
            yield Message('stop', code=1)

    def fetchForever(self):
        INFO('已在后台运行 fetchForever 方法，每隔 5 分钟获取一次联系人资料')
        while True:
            time.sleep(300)
            try:
                contacts = self.fetch()
            except (QSession.Error, Exception):
                WARN(' fetchForever 方法出错')
                DEBUG('', exc_info=True)
            else:
                yield Message('fetchcomplete', contacts=contacts)
    
    def onPollComplete(self, message):
        ctype, fromUin, memberUin, content = message.result
        
        if ctype == 'timeout':
            self.Process(Message('polltimeout'))
            return

        try:
            contact = self.Get(ctype, uin=fromUin)[0]
        except IndexError:
            contact = QContact(ctype, uin=fromUin, name='##UNKNOWN', qq='')

        if ctype == 'buddy':
            memberName = ''
            INFO('来自 %s 的消息: "%s"' % (str(contact), content))
        else:
            memberName = contact.GetMemberName(memberUin)
            INFO('来自 %s[成员“%s”] 的消息: "%s"' % \
                 (str(contact), memberName, content))

        self.Process(QQMessage(
            contact, memberUin, memberName, content, self.SendTo
        ))
    
    def onFetchComplete(self, message):
        self.assignContacts(message.contacts)
    
    def onStop(self, code):
        if code == 0:
            INFO('QQBot 正常停止')
        else:
            INFO('QQBOT 异常停止')

class QQMessage(Message):
    mtype = 'qqmessage'
    
    def __init__(self, contact, memberUin, memberName, content, sendTo):
        self.contact = contact
        self.memberUin = memberUin
        self.memberName = memberName
        self.content = content
        self.sendTo = sendTo
    
    def Reply(self, reply):
        if reply:
            time.sleep(random.randint(1, 4))
            self.sendTo(self.contact, reply)

class BasicAI:
    def __init__(self):
        self.cmdFuncs = {}
        self.docs = []

        for k in dir(self):
            if k.startswith('cmd_'):
                func = getattr(self, k)
                self.cmdFuncs[k[4:]] = func
                self.docs.append(func.__doc__)
        self.docs.sort()

        self.termUsage = '欢迎使用 QQBot ，使用方法：'
        self.qqUsage = self.termUsage
        for doc in self.docs:
            self.termUsage += '\n    ' + doc[2:]
            self.qqUsage += '\n   -' + doc[2:]
        self.termUsage += '\n    quit'

    def OnPollTimeout(self, bot, msg):
        pass
    
    def OnQQMessage(self, bot, msg):
        if msg.contact.ctype == 'buddy' and msg.content == 'qqbot --version':
            msg.Reply('QQbot-' + bot.conf.version)

        # 去掉通过 qq 消息来操作 QQBot 的方式
        # if msg.content.strip().startswith('-'):
        #    msg.content = msg.content.strip()[1:]
        #    msg.Reply(self.execute(bot, msg))

    def OnTermMessage(self, bot, msg):
        msg.Reply(self.execute(bot, msg))
    
    def execute(self, bot, msg):
        argv = msg.content.strip().split()
        if argv and argv[0]:
            f = self.cmdFuncs.get(argv[0], None)
            return f and f(argv[1:], msg, bot)
    
    def cmd_help(self, args, msg, bot):
        '''1 help'''       
        if len(args) == 0:
            return (msg.mtype=='qqmessage' and self.qqUsage or self.termUsage)
    
    def cmd_list(self, args, msg, bot):
        '''2 list buddy|group|discuss'''
        if len(args) == 1:
            return '\n'.join(map(repr, bot.List(args[0])))
    
    def cmd_send(self, args, msg, bot):
        '''3 send buddy|group|discuss x|uin=x|qq=x|name=x message'''
        if len(args) >= 3:
            return '\n'.join(bot.Send(args[0], args[1], ' '.join(args[2:])))
    
    def cmd_get(self, args, msg, bot):
        '''4 get buddy|group|discuss x|uin=x|qq=x|name=x'''
        if len(args) == 2:
            return '\n'.join(map(repr, bot.Get(args[0], args[1])))
    
    def cmd_member(self, args, msg, bot):
        '''5 member group|discuss x|uin=x|qq=x|name=x'''
        if len(args) == 2 and args[0] in ('group', 'discuss'):
            result = []
            for contact in bot.Get(args[0], args[1]):
                result.append(repr(contact))
                for uin, name in contact.members.items():
                    result.append('    成员：%s，uin%s' % (name, uin))
            return '\n'.join(result)
    
    def cmd_stop(self, args, msg, bot):
        '''6 stop'''
        if len(args) == 0:
            INFO('收到 stop 命令，QQBot 即将停止')
            msg.Reply('QQBot已停止')
            bot.Stop()

def Main():
    try:
        if sys.argv[-1] == '--subprocessCall':
            isSubprocessCall = True
            sys.argv.pop()
        else:
            isSubprocessCall = False

        conf = QConf()
        if not conf.restartOnOffline or isSubprocessCall:
            bot = QQBot(conf=conf)
            bot.Login()
            sys.exit(bot.Run())
        else:
            args = ['python', __file__] + sys.argv[1:] + \
                   ['--mailAuthCode', conf.mailAuthCode, '--subprocessCall']
            while subprocess.call(args) != 0:
                INFO('重新启动 QQBot ')
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == '__main__':
    Main()
