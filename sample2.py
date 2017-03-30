# -*- coding: utf-8 -*-

from qqbot import QQBot, RunBot

class MyQQBot(QQBot):
    def onQQMessage(self, contact, member, content):
        if content == '-hello':
            self.SendTo(contact, '你好，我是QQ机器人')
        elif content == '-stop':
            self.SendTo(contact, 'QQ机器人已关闭')
            self.Stop()

if __name__ == '__main__':
    # 注意： 这一行之前的代码会被执行两边
    # 进入 RunBot() 后，会重启一次程序（ subprocess.call(sys.argv + [...]) ）
    RunBot()
    # 注意: 这一行之后的代码永远都不会被执行。
