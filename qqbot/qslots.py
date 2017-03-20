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
    if content == '--version':
        bot.SendTo(contact, 'QQbot-' + bot.conf.version)

@qqbotslot
def onNewContact(bot, contact, owner):
    pass

@qqbotslot
def onLostContact(bot, contact, owner):
    pass

@qqbotslot
def onInterval(bot):
    INFO('Interval')
    pass

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

def cmd_list(bot, args):
    '''2 list ctype [oinfo] [cinfo]'''
    
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
    '''3 send ctype [oinfo] cinfo content'''
    
    if args[0] in ('buddy', 'group', 'discuss') and len(args) >= 3:
        # send buddy jack hello
        result = []
        for c in bot.List(args[0], args[1]):
            result.append(bot.SendTo(c, ' '.join(args[2:])))
        if not result:
            return '%s-%s 不存在' % (args[0], args[1])
        else:
            return '\n'.join(result)
    
def cmd_stop(bot, args):
    '''4 stop'''
    if len(args) == 0:
        Put(bot.Stop)
        return 'QQBot已停止'

def cmd_restart(bot, args):
    '''5 restart'''
    if len(args) == 0:
        Put(bot.Restart)
        return 'QQBot已重启'

_thisDict, docs = globals(), []

for name, attr in _thisDict.items():
    if name.startswith('cmd_'):
        cmdFuncs[name[4:]] = attr
        docs.append(attr.__doc__)

usage['term'] = 'QQBot 命令：\n   qq ' + \
                '\n   qq '.join(doc[2:] for doc in sorted(docs))
