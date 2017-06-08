# -*- coding: utf-8 -*-

from qqbot import QQBotSched as qqbotsched
from qqbot.utf8logger import INFO

# 每天 7:30 重启（需要手工扫码）
@qqbotsched(hour='7', minute='30')
def schedRestart(bot):
    bot.FreshRestart()

def onPlug(bot):
    INFO('已创建计划任务：每天 7：30 重启（需要手工扫码）')

def onUnplug(bot):
    INFO('已删除计划任务：每天 7：30 重启（需要手工扫码）')

# 其他定时参数型式：
# @qqbotsched(second='5-55/5')
# @qqbotsched(hour='22', minute='0-58/1')
