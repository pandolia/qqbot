# -*- coding: utf-8 -*-

# 插件加载方法：
# 1. 启动 qqbot 
# 2. 将本文件保存至 ~/.qqbot-tmp/plugins 目录 （或 c:\user\xxx\.qqbot-tmp\plugins ）
# 3. 在命令行窗口输入： qq plug sample

def onQQMessage(bot, contact, member, content):
    if content == '-hello':
        bot.SendTo(contact, '你好，我是QQ机器人')
    elif content == '-stop':
        bot.SendTo(contact, 'QQ机器人已关闭')
        bot.Stop()
