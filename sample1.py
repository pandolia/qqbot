# -*- coding: utf-8 -*-

from qqbot import QQBotSlot as qqbotslot, RunBot

@qqbotslot
def onQQMessage(bot, contact, member, content):
    # if '@ME' in content:
    #     bot.SendTo(contact, '%s， 想我了吧？' % member.name)
    if content == '-hello':
        bot.SendTo(contact, '你好，我是QQ机器人')
    elif content == '-stop':
        bot.SendTo(contact, 'QQ机器人已关闭')
        bot.Stop()

if __name__ == '__main__':
    RunBot()
