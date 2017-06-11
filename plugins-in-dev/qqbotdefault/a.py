# -*- coding: utf-8 -*-

from qqbot.utf8logger import DEBUG
from qqbot import QQBotSched as qqbotsched

def onInit(bot):
    DEBUG('%s.ON-INIT', __name__)

def onQrcode(bot, pngPath, pngContent):
    DEBUG('%s.ON-QRCODE: %s (%d bytes)', __name__, pngPath, len(pngContent))

def onQQMessage(bot, contact, member, content):
    DEBUG('%s.ON-QQ-MESSAGE: %s, %s, %s', __name__, contact, member, content)

def onInterval(bot):
    DEBUG('%s.ON-INTERVAL', __name__)

def onStartupComplete(bot):
    DEBUG('%s.ON-START-UP-COMPLETE', __name__)

def onUpdate(bot, tinfo):
    DEBUG('%s.ON-UPDATE: %s', __name__, tinfo)

def onPlug(bot):
    DEBUG('%s.ON-PLUG', __name__)

def onUnplug(bot):
    DEBUG('%s.ON-UNPLUG', __name__)

def onExpire(bot):
    DEBUG('%s.ON-EXPIRE', __name__)

@qqbotsched(minute='0-59')
def schedTask(bot):
    DEBUG('%s.SCHED-TASK', __name__)
