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

from qqbot.qconf import QConf
from qqbot.utf8logger import INFO, CRITICAL, ERROR, WARN
from qqbot.qsession import QLogin, RequestError
from qqbot.exitcode import RESTART, POLL_ERROR
from qqbot.common import StartDaemonThread, Import
from qqbot.qterm import QTermServer
from qqbot.qcontactdb import QContact
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
            code = subprocess.call(args)
            if code == 0:
                INFO('QQBot 正常停止')
                sys.exit(code)
            elif code == RESTART:
                args[-2] = ''
                INFO('10秒后重新启动 QQBot （手工登陆）')
                time.sleep(10)
            else:
                CRITICAL('QQBOT 异常停止（code=%s）', code)
                if conf.restartOnOffline:
                    args[-2] = conf.qq
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
        self.StrOfList = contactdb.StrOfList
        self.find = contactdb.Find
        self.deleteMember = contactdb.DeleteMember
        self.setMemberCard = contactdb.SetMemberCard
        self.firstFetch = contactdb.FirstFetch
        
        # child thread 1
        self.poll = session.Copy().Poll
        
        # child thread 2
        self.termForver = QTermServer(self.conf.termServerPort).Run
        
        # runs in main thread, but puts tasks into child thread 3
        self.updateForever = contactdb.UpdateForever
        
        # runs in main thread, but puts tasks into child thread 4
        self.monitorForever = contactdb.MonitorForever

    def Run(self):
        import qqbot.qslots as _x; _x
        
        for plugin in self.conf.plugins:
            self.Plug(plugin)

        if self.conf.startAfterFetch:
            self.firstFetch()
            self.onFetchComplete()

        self.onStartupComplete()
  
        StartDaemonThread(self.pollForever)
        StartDaemonThread(self.termForver, self.onTermCommand)
        Put(self.updateForever, bot=self)
        Put(self.monitorForever, bot=self)
        StartDaemonThread(self.intervalForever)

        MainLoop()
    
    def Stop(self):
        sys.exit(0)
    
    def Restart(self):
        sys.exit(RESTART)
    
    # child thread 1
    def pollForever(self):
        while True:
            try:
                result = self.poll()
            except RequestError:
                Put(sys.exit, POLL_ERROR)
                break
            except:
                ERROR('qsession.Poll 方法出错', exc_info=True)
            else:
                Put(self.onPollComplete, *result)

    def onPollComplete(self, ctype, fromUin, memberUin, content):
        if ctype == 'timeout':
            return

        contact = self.find(ctype, fromUin)
        member = None
        nameInGroup = None
        
        if contact is None:
            contact = QContact(ctype=ctype, uin=fromUin, name='uin'+fromUin)
            if ctype in ('group', 'discuss'):
                member = QContact(ctype=ctype+'-member',
                                  uin=memberUin, name='uin'+memberUin)
        elif ctype in ('group', 'discuss'):
            member = self.find(contact, memberUin)
            if member is None:
                member = QContact(ctype=ctype+'-member',
                                  uin=memberUin, name='uin'+memberUin)
            if ctype == 'group':
                cl = self.List(contact, self.conf.qq)
                if cl:
                    nameInGroup = cl[0].name

        if nameInGroup and ('@'+nameInGroup) in content:
            INFO('有人 @ 我：%s[%s]' % (contact, member))
            content = '[@ME] ' + content.replace('@'+nameInGroup, '')
        else:
            content = content.replace('@ME', '@Me')
                
        if ctype == 'buddy':
            INFO('来自 %s 的消息: "%s"' % (contact, content))
        else:
            INFO('来自 %s[%s] 的消息: "%s"' % (contact, member, content))

        Put(self.onQQMessage, contact, member, content)
    
    # child thread 5
    def intervalForever(self):
        while True:
            time.sleep(300)
            Put(self.onInterval)

    slotsTable = {
        'onQQMessage': [],
        'onInterval': [],
        'onNewContact': [],
        'onLostContact': [],
        'onStartupComplete': [],
        'onFetchComplete': []
    }
    
    plugins = set()
    
    @classmethod
    def AddSlot(cls, func):
        cls.slotsTable[func.__name__].append(func)
        return func

    @classmethod
    def unplug(cls, moduleName):
        for slots in cls.slotsTable.values():
            i = 0
            while i < len(slots):
                if slots[i].__module__ == moduleName:
                    slots[i] = slots[-1]
                    slots.pop()
                else:
                    i += 1
    
    @classmethod
    def Unplug(cls, moduleName):
        if moduleName not in cls.plugins:
            result = '警告：试图卸载未安装的插件 %s' % moduleName
            WARN(result)
        else:
            cls.unplug(moduleName)
            cls.plugins.remove(moduleName)
            result = '成功：卸载插件 %s' % moduleName
            INFO(result)
        
        return result

    @classmethod
    def Plug(cls, moduleName):
        try:
            module = Import(moduleName)
        except (Exception, SystemExit) as e:
            cls.unplug(moduleName)
            cls.plugins.discard(moduleName)
            result = '错误：无法加载插件 %s ，%s: %s' % (moduleName, type(e), e)
            ERROR(result)
        else:
            cls.unplug(moduleName)

            names = []
            for slotName in cls.slotsTable.keys():
                if hasattr(module, slotName):
                    cls.slotsTable[slotName].append(getattr(module, slotName))
                    names.append(slotName)

            if not names:
                INFO(module.__dict__.keys())
                result = '警告：插件 %s 中不包含任何可注册的回调函数' % moduleName
                WARN(result)
            else:
                cls.plugins.add(moduleName)
                result = '成功：加载插件 %s%s' % (moduleName, names)
                INFO(result)

        return result
    
    @classmethod
    def Plugins(cls):
        return list(cls.plugins)

def wrap(slots):
    return lambda *a,**kw: [f(*a, **kw) for f in slots]

for name, slots in QQBot.slotsTable.items():
    setattr(QQBot, name, wrap(slots))

QQBotSlot = QQBot.AddSlot
