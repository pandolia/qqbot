# -*- coding: utf-8 -*-

def onQQMessage(bot, contact, member, content):
    if content == '-hello':
        bot.SendTo(contact, '你好，我是QQ机器人')
    elif content == '-stop':
        bot.SendTo(contact, 'QQ机器人已关闭')
        bot.Stop()

def onPlug(bot):
    1/0
    print((bot, 'ON-PLUG : qqbot.qslots'))

def onUnplug(bot):
    1/0
    print((bot, 'ON-UNPLUG : qqbot.qslots'))
