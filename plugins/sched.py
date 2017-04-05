# -*- coding: utf-8 -*-
from datetime import datetime

from qqbot import QQBotSched as qqbotsched, RunBot

# from qqbot.utf8logger import INFO

#@qqbotsched(second='5-55/5')
#def mytask(bot):
#    INFO('SCHEDULED')

@qqbotsched(hour='22', minute='0-58/1')
def mytask(bot):
    cl = bot.List('buddy', '3497303033')
    if cl:
        bot.SendTo(cl[0], datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == '__main__':
    RunBot()
