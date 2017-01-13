#!/usr/bin/python
# -*- coding: utf-8 -*-

from qqbot import QQBot

myqqbot = QQBot()

@myqqbot.On('qqmessage')
def handler(bot, message):
    if message.content == '-hello':
        bot.SendTo(message.contact, '你好，我是QQ机器人')
    elif message.content == '-stop':
        bot.SendTo(message.contact, 'QQ机器人已关闭')
        bot.Stop()

myqqbot.Login()
myqqbot.Run()
