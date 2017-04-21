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

def runBot(botCls, qq, user):
    if sys.argv[-1] == '--subprocessCall':
        isSubprocessCall = True
        sys.argv.pop()
    else:
        isSubprocessCall = False

    if isSubprocessCall:
        bot = botCls()
        bot.Login(qq, user)
        bot.Run()
    else:
        conf = QConf(qq, user)

        if sys.argv[0].endswith('py') or sys.argv[0].endswith('pyc'):
            args = [sys.executable] + sys.argv
        else:
            args = sys.argv

        args = args + ['--mailAuthCode', conf.mailAuthCode]
        args = args + ['--qq', conf.qq]
        args = args + ['--subprocessCall']

        while True:
            p = subprocess.Popen(args)
            pid = p.pid
            code = p.wait()
            if code == 0:
                INFO('QQBot 正常停止')
                sys.exit(code)
            elif code == RESTART:
                args[-2] = conf.LoadQQ(pid)
                INFO('5 秒后重新启动 QQBot （自动登陆）')
                time.sleep(5)
            elif code == FRESH_RESTART:
                args[-2] = ''
                INFO('5 秒后重新启动 QQBot （手工登陆）')
                time.sleep(5)
            else:
                CRITICAL('QQBOT 异常停止（code=%s）', code)
                if conf.restartOnOffline:
                    args[-2] = conf.LoadQQ(pid)
                    INFO('30秒后重新启动 QQBot （自动登陆）')
                    time.sleep(30)
                else:
                    sys.exit(code)

def RunBot(botCls=None, qq=None, user=None):
    try:
        runBot((botCls or QQBot), qq, user)
    except KeyboardInterrupt:
        sys.exit(1)

class QQBot(GroupManager):

    def Login(self, qq=None, user=None):
        session, contactdb, self.conf = QLogin(qq, user)

        # main thread
        self.SendTo = session.SendTo
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
        
        # child thread 2
        self.termForver = QTermServer(self.conf.termServerPort).Run

    def Run(self):
        QQBot.initScheduler(self)

        import qqbot.qslots as _x; _x
        
        for plugin in self.conf.plugins:
            self.Plug(plugin)

        if self.conf.startAfterFetch:
            self.firstFetch()

        self.onStartupComplete()
  
        StartDaemonThread(self.pollForever)
        StartDaemonThread(self.termForver, self.onTermCommand)
        StartDaemonThread(self.intervalForever)

        MainLoop()
    
    def Stop(self):
        sys.exit(0)
    
    def Restart(self):
        self.conf.StoreQQ()
        sys.exit(RESTART)
    
    def FreshRestart(self):
        sys.exit(FRESH_RESTART)
    
    # child thread 1
    def pollForever(self):
        while True:
            try:
                result = self.poll()
            except RequestError:
                self.conf.StoreQQ()
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
            self.findSender(ctype, fromUin, membUin, self.conf.qq)

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

    # child thread 5
    def intervalForever(self):
        while True:
            time.sleep(300)
            Put(self.onInterval)            

    slotsTable = {
        'onQQMessage': [],
        'onInterval': [],
        'onStartupComplete': []
    }
    
    plugins = set()
    
    @classmethod
    def AddSlot(cls, func):
        cls.slotsTable[func.__name__].append(func)
        return func

    @classmethod
    def unplug(cls, moduleName, removeJob=True):
        for slots in cls.slotsTable.values():
            i = 0
            while i < len(slots):
                if slots[i].__module__ == moduleName:
                    slots[i] = slots[-1]
                    slots.pop()
                else:
                    i += 1

        if removeJob:
            for job in cls.schedTable.pop(moduleName, []):
                job.remove()
        
        cls.plugins.discard(moduleName)
    
    @classmethod
    def Unplug(cls, moduleName):
        if moduleName not in cls.plugins:
            result = '警告：试图卸载未安装的插件 %s' % moduleName
            WARN(result)
        else:
            cls.unplug(moduleName)
            result = '成功：卸载插件 %s' % moduleName
            INFO(result)        
        return result

    @classmethod
    def Plug(cls, moduleName):
        cls.unplug(moduleName)
        try:
            module = Import(moduleName)
        except (Exception, SystemExit) as e:
            result = '错误：无法加载插件 %s ，%s: %s' % (moduleName, type(e), e)
            ERROR(result)
        else:
            cls.unplug(moduleName, removeJob=False)

            names = []
            for slotName in cls.slotsTable.keys():
                if hasattr(module, slotName):
                    cls.slotsTable[slotName].append(getattr(module, slotName))
                    names.append(slotName)

            if (not names) and (moduleName not in cls.schedTable):
                result = '警告：插件 %s 中没有定义回调函数或定时任务' % moduleName
                WARN(result)
            else:
                cls.plugins.add(moduleName)
                jobs = cls.schedTable.get(moduleName,[])
                jobNames = [f.func.__name__ for f in jobs]
                result = '成功：加载插件 %s（回调函数%s、定时任务%s）' % \
                         (moduleName, names, jobNames)
                INFO(result)

        return result
    
    @classmethod
    def Plugins(cls):
        return list(cls.plugins)
    
    scheduler = BackgroundScheduler(daemon=True)
    schedTable = defaultdict(list)

    @classmethod
    def initScheduler(cls, bot):
        cls._bot = bot
        cls.scheduler.start()
    
    @classmethod
    def AddSched(cls, **triggerArgs):
        def wrapper(func):
            job = lambda: Put(func, cls._bot)
            job.__name__ = func.__name__
            j = cls.scheduler.add_job(job, 'cron', **triggerArgs)
            cls.schedTable[func.__module__].append(j)
            return func
        return wrapper

def wrap(slots):
    return lambda *a,**kw: [f(*a, **kw) for f in slots]

for name, slots in QQBot.slotsTable.items():
    setattr(QQBot, name, wrap(slots))

QQBotSlot = QQBot.AddSlot
QQBotSched = QQBot.AddSched

if __name__ == '__main__':
    bot = QQBot()
    bot.Login(user='hcj')
    gl = bot.List('group')
    ml = bot.List(gl[0])
    m = ml[0]
