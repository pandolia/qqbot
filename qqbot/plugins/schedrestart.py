# -*- coding: utf-8 -*-

# 本插件为默认插件，将在 qqbot 启动时自动加载。
# 如果不希望加载本插件，可以在配置文件中的 plugins 选项中删除 qqbot.plugins.schedrestart 。

# 本插件将在每天的固定时间 fresh-restart 一次，重启时间可以在配置文件中的 pluginsConf 中设置
# 示例： "pluginsConf" : {"schedRestart": "8:00"}

from qqbot import QQBotSched as qqbotsched
from qqbot.utf8logger import INFO

class g(object):
    pass

def onPlug(bot):
    g.t = bot.conf.pluginsConf.get('schedRestart', '8:00')
    g.hour, g.minute = g.t.split(':')
    
    @qqbotsched(hour=g.hour, minute=g.minute)
    def schedRestart(_bot):
        _bot.FreshRestart()

    INFO('已创建计划任务：每天 %s 重启（需要手工扫码）', g.t)

def onUnplug(bot):
    INFO('已删除计划任务：每天 %s 重启（需要手工扫码）', g.t)
