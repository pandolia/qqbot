# -*- coding: utf-8 -*-

import sys, os
p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if p not in sys.path:
    sys.path.insert(0, p)

from qqbot.utf8logger import WARN, INFO
from qqbot.qqbotcls import QQBot
from qqbot.mainloop import Put

def qqbotslot(func):
    if not hasattr(QQBot, func.__name__):
        setattr(QQBot, func.__name__, func)
    return func

@qqbotslot
def onQQMessage(bot, contact, member, content):
    # 当收到 QQ 消息时被调用
    # bot     : QQBot 对象，提供 List/SendTo/Stop/Restart 四个接口，详见文档第五节
    # contact : QContact 对象，消息的发送者，具有 ctype/qq/uin/name/nick/mark/card 属性，这些属性都是 str 对象
    # member  : QContact 对象，仅当本消息为 群或讨论组 消息时有效，代表实际发消息的成员
    # content : str 对象，消息内容
    if content == '--version':
        bot.SendTo(contact, 'QQbot-' + bot.conf.version)

@qqbotslot
def onNewContact(bot, contact, owner):
    # 当新增 好友/群/讨论组/群成员/讨论组成员 时被调用
    # bot     : QQBot 对象
    # contact : QContact 对象，代表新增的联系人
    # owner   : QContact 对象，仅在新增 群成员/讨论组成员 时有效，代表新增成员所在的 群/讨论组
    pass

@qqbotslot
def onLostContact(bot, contact, owner):
    # 当失去 好友/群/讨论组/群成员/讨论组成员 时被调用
    # bot     : QQBot 对象
    # contact : QContact 对象，代表失去的联系人
    # owner   : QContact 对象，仅在失去 群成员/讨论组成员 时有效，代表失去成员所在的 群/讨论组
    pass

@qqbotslot
def onInterval(bot):
    # 每隔 5 分钟被调用
    # bot : QQBot 对象
    INFO('Interval')

@qqbotslot
def onTermCommand(bot, client, command):
    result = '##UNKOWNERROR'
    try:
        result = execute(bot, command) or 'QQBot 命令格式错误'
    except (Exception, SystemExit) as e:
        result = '运行命令过程中出错：' + str(type(e)) + str(e)
        WARN(result, exc_info=True)
    finally:
        client.Reply(result)

cmdFuncs, usage = {}, {}

def execute(bot, command):
    argv = command.strip().split()
    if argv and argv[0] in cmdFuncs:
        return cmdFuncs[argv[0]](bot, argv[1:])

def cmd_help(bot, args):
    '''1 help'''
    if len(args) == 0:
        return usage['term']

def cmd_stop(bot, args):
    '''1 stop'''
    if len(args) == 0:
        Put(bot.Stop)
        return 'QQBot已停止'

def cmd_restart(bot, args):
    '''1 restart'''
    if len(args) == 0:
        Put(bot.Restart)
        return 'QQBot已重启'

def cmd_list(bot, args):
    '''2 qq list buddy|group|discuss|group-member|discuss-member [oqq|oname|okey=oval] [qq|name|key=val]'''
    
    if args[0] in ('buddy', 'group', 'discuss') and len(args) in (1, 2):
        # list buddy
        # list buddy jack
        return bot.StrOfList(*args)

    elif (args[0] in ('group-member', 'discuss-member')) and \
            args[1] and (len(args) in (2, 3)):
        # list group-member xxx班
        # list group-member xxx班 yyy
        return bot.StrOfList(*args)

def cmd_send(bot, args):
    '''3 send buddy|group|discuss qq|name|key=val message'''
    
    if args[0] in ('buddy', 'group', 'discuss') and len(args) >= 3:
        # send buddy jack hello
        result = []
        for c in bot.List(args[0], args[1]):
            result.append(bot.SendTo(c, ' '.join(args[2:])))
        if not result:
            return '%s-%s 不存在' % (args[0], args[1])
        else:
            return '\n'.join(result)

for name, attr in dict(globals().items()).items():
    if name.startswith('cmd_'):
        cmdFuncs[name[4:]] = attr

usage['term'] = '''\
QQBot 命令：
1） 帮助、停机和重启命令
    qq help|stop|restart

2） 联系人查询命令
    qq list buddy|group|discuss|group-member|discuss-member [oqq|oname|okey=oval] [qq|name|key=val]

3） 消息发送命令
    qq send buddy|group|discuss qq|name|key=val message\
'''