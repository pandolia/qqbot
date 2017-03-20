# -*- coding: utf-8 -*-

from qqbot import QQBot, RunBot

class MyQQBot(QQBot):
    def onQQMessage(self, contact, member, content):
        if content == '-hello':
            self.SendTo(contact, '你好，我是QQ机器人')
        elif content == '-stop':
            self.SendTo(contact, 'QQ机器人已关闭')
            self.Stop()

RunBot(MyQQBot)
