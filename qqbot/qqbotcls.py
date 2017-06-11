#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
QQBot   -- A conversation robot base on Tencent's SmartQQ
Website -- https://github.com/pandolia/qqbot/
Author  -- pandolia@yeah.net
"""

import sys, os
p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if p not in sys.path:
    sys.path.insert(0, p)

import sys, subprocess, time
from apscheduler.schedulers.background import BackgroundScheduler
from collections import defaultdict

from qqbot.qconf import QConf
from qqbot.utf8logger import INFO, CRITICAL, ERROR, WARN
from qqbot.qsession import QLogin, RequestError
from qqbot.exitcode import RESTART, POLL_ERROR, FRESH_RESTART
from qqbot.common import StartDaemonThread, Import
from qqbot.qterm import QTermServer
from qqbot.mainloop import MainLoop, Put
from qqbot.groupmanager import GroupManager
from qqbot.termbot import TermBot

def runBot(argv):
    if sys.argv[-1] == '--subprocessCall':
        sys.argv.pop()
        try:
            bot = QQBot._bot
            bot.Login(argv)
            bot.Run()
        finally:
            if hasattr(bot, 'conf'):
                bot.conf.StoreQQ()
    else:
        conf = QConf()

        if sys.argv[0].endswith('py') or sys.argv[0].endswith('pyc'):
            args = [sys.executable] + sys.argv
        else:
            args = sys.argv

        args = args + ['--mailAuthCode', conf.mailAuthCode]
        args = args + ['--qq', conf.qq]
        args = args + ['--subprocessCall']

        while True:
            p = subprocess.Popen(args)
            code = p.wait()
            if code == 0:
                INFO('QQBot 正常停止')
                sys.exit(code)
            elif code == RESTART:
                args[-2] = conf.LoadQQ()
                INFO('5 秒后重新启动 QQBot （自动登陆，qq=%s）', args[-2])
                time.sleep(5)
            elif code == FRESH_RESTART:
                args[-2] = ''
                INFO('5 秒后重新启动 QQBot （手工登陆）')
                time.sleep(5)
            else:
                CRITICAL('QQBOT 异常停止（code=%s）', code)
                if conf.restartOnOffline:
                    args[-2] = conf.LoadQQ()
                    INFO('15秒后重新启动 QQBot （自动登陆，qq=%s）', args[-2])
                    time.sleep(15)
                else:
                    sys.exit(code)

def RunBot(argv=None):
    try:
        runBot(argv)
    except KeyboardInterrupt:
        sys.exit(1)

def _call(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except Exception as e:
        ERROR('', exc_info=True)
        ERROR('执行 %s.%s 时出错，%s', func.__module__, func.__name__, e)

class QQBot(GroupManager, TermBot):

    def Login(self, argv=None):
        self.init(argv)
        session, contactdb = QLogin(self.conf)

        # main thread
        self.SendTo = session.Copy().SendTo
        self.groupKick = session.GroupKick
        self.groupSetAdmin = session.GroupSetAdmin
        self.groupShut = session.GroupShut
        self.groupSetCard = session.GroupSetCard
        
        # main thread
        self.List = contactdb.List
        self.Update = contactdb.Update
        self.StrOfList = contactdb.StrOfList
        self.ObjOfList = contactdb.ObjOfList
        self.findSender = contactdb.FindSender
        self.firstFetch = contactdb.FirstFetch
        self.Delete = contactdb.db.Delete
        self.Modify = contactdb.db.Modify
        
        # child thread 1
        self.poll = session.Copy().Poll

    def Run(self):
        if self.conf.startAfterFetch:
            self.firstFetch()

        self.onPlug()
        self.onStartupComplete()
        
        # child thread 1~4
        StartDaemonThread(self.pollForever)
        StartDaemonThread(self.intervalForever)
        StartDaemonThread(QTermServer(self.conf.termServerPort, self.onTermCommand).Run)
        self.scheduler.start()

        self.started = True
        MainLoop()
    
    def Stop(self):
        sys.exit(0)
    
    def Restart(self):
        sys.exit(RESTART)
    
    def FreshRestart(self):
        sys.exit(FRESH_RESTART)
    
    # child thread 1
    def pollForever(self):
        while True:
            try:
                result = self.poll()
            except RequestError:
                Put(self.onExpire)
                Put(sys.exit, POLL_ERROR)
                break
            except:
                ERROR('qsession.Poll 方法出错', exc_info=True)
            else:
                Put(self.onPollComplete, *result)

    def onPollComplete(self, ctype, fromUin, membUin, content):
        if ctype == 'timeout':
            return

        contact, member, nameInGroup = \
            self.findSender(ctype, fromUin, membUin, self.conf.qq, content)
        
        if contact.ctype == 'group' and member == 'SYSTEM-MESSAGE':
            INFO('来自 %s 的系统消息： "%s"', contact, content)
            return

        if self.detectAtMe(nameInGroup, content):
            INFO('有人 @ 我：%s[%s]' % (contact, member))
            content = '[@ME] ' + content.replace('@'+nameInGroup, '')
        else:
            content = content.replace('@ME', '@Me')
                
        if ctype == 'buddy':
            INFO('来自 %s 的消息: "%s"' % (contact, content))
        else:
            INFO('来自 %s[%s] 的消息: "%s"' % (contact, member, content))

        self.onQQMessage(contact, member, content)
    
    def detectAtMe(self, nameInGroup, content):
        return nameInGroup and ('@'+nameInGroup) in content

    # child thread 2
    def intervalForever(self):
        while True:
            time.sleep(300)
            Put(self.onInterval)
    
    def __init__(self):        
        self.scheduler = BackgroundScheduler(daemon=True)
        self.schedTable = defaultdict(list)
        self.slotsTable = {
            'onInit': [],
            'onQrcode': [],
            'onStartupComplete': [],
            'onQQMessage': [],
            'onInterval': [],
            'onUpdate': [],
            'onPlug': [],
            'onUnplug': [],
            'onExpire': [],
        }
        self.started = False
        self.plugins = {}
    
    def init(self, argv):
        for name, slots in self.slotsTable.items():
            setattr(self, name, self.wrap(slots))

        self.conf = QConf(argv)
        self.conf.Display()

        for pluginName in self.conf.plugins:
            self.Plug(pluginName)
        
        self.onInit()       
    
    def wrap(self, slots):
        def func(*args, **kwargs):
            for f in slots:
                _call(f, self, *args, **kwargs)
        return func
    
    def AddSlot(self, func):
        self.slotsTable[func.__name__].append(func)
        return func

    def AddSched(self, **triggerArgs):
        def wrapper(func):
            job = lambda: Put(_call, func, self)
            job.__name__ = func.__name__
            j = self.scheduler.add_job(job, 'cron', **triggerArgs)
            self.schedTable[func.__module__].append(j)
            return func
        return wrapper
    
    def unplug(self, moduleName, removeJob=True):
        for slots in self.slotsTable.values():
            i = 0
            while i < len(slots):
                if slots[i].__module__ == moduleName:
                    slots[i] = slots[-1]
                    slots.pop()
                else:
                    i += 1

        if removeJob:
            for job in self.schedTable.pop(moduleName, []):
                job.remove()
            self.plugins.pop(moduleName, None)
    
    def Plug(self, moduleName):
        self.unplug(moduleName)
        try:
            module = Import(moduleName)
        except Exception as e:
            result = '错误：无法加载插件 %s ，%s: %s' % (moduleName, type(e), e)
            ERROR('', exc_info=True)
            ERROR(result)
            self.unplug(moduleName)
        else:
            self.unplug(moduleName, removeJob=False)

            names = []
            for slotName in self.slotsTable.keys():
                if hasattr(module, slotName):
                    self.slotsTable[slotName].append(getattr(module, slotName))
                    names.append(slotName)

            if (not names) and (moduleName not in self.schedTable):
                result = '警告：插件 %s 中没有定义回调函数或定时任务' % moduleName
                WARN(result)
            else:
                self.plugins[moduleName] = module
                    
                jobs = self.schedTable.get(moduleName, [])
                jobNames = [f.func.__name__ for f in jobs]
                result = '成功：加载插件 %s（回调函数%s、定时任务%s）' % \
                         (moduleName, names, jobNames)
                INFO(result)

                if self.started and hasattr(module, 'onPlug'):
                    _call(module.onPlug, self)

        return result
    
    def Unplug(self, moduleName):
        if moduleName not in self.plugins:
            result = '警告：试图卸载未安装的插件 %s' % moduleName
            WARN(result)
            return result
        else:
            module = self.plugins[moduleName]
            self.unplug(moduleName)
            if hasattr(module, 'onUnplug'):
                _call(module.onUnplug, self)
            result = '成功：卸载插件 %s' % moduleName
            INFO(result)
            return result
    
    def Plugins(self):
        return list(self.plugins.keys())

_bot = QQBot()
QQBot._bot = _bot
QQBotSlot = _bot.AddSlot
QQBotSched = _bot.AddSched
QQBot.__init__ = None

if __name__ == '__main__':
    # 不知道为什么这里直接运行 _bot.Login() 会出问题：
    # AttributeError: 'QQBot' object has no attribute 'scheduler'
    # _bot.Login()

    # 一定要先运行一下 from qqbot import _bot as bot
    from qqbot import _bot as bot
    bot.Login()
    gl = bot.List('group')
    ml = bot.List(gl[0])
    m = ml[0]
