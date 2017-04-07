#!/usr/bin/python
# QQbot Loader for JetBrains PyCharm
#
# 作者     : SuperMarioSF
# 上次更新 : 2017-04-07 (QQbot v2.1.13)
#
# 本文将用于在JetBrains PyCharm IDE环境下测试和运行QQbot。
# 要开始调试或运行，在调整好下方的相关参数后，直接调试或运行本文件即可。
# 此文件也可作为实现自己的机器人的功能模板。

from qqbot import QQBotSlot as qqbotslot
from qqbot import QQBotSched as qqbotsched, RunBot
from qqbot.utf8logger import INFO, CRITICAL, ERROR, DEBUG
import sys

#
# =================================================================
#
# (1) 参数配置
# 所有启动时使用的参数可以在这里调整。
# 注意：在这里提供的参数配置仅用于调试目的。
# 为了能够正常使用QQbot，请优先考虑使用配置文件来调整参数。
#
# 根据顺序，在上方指定的参数的优先级将高于下方指定的参数的优先级。
#
# 快速启动: 指定QQ号即可启动（并载入已有的自动登录数据）。
# 在不需要其他参数时，使用这个是最快的。
# 填写None表示不使用此参数。请填写此字段为为字符串。例如 qq = '12345678'
qq = None

# 方法1. 指定命令行启动参数。
# 指定为一个列表，列表项的数据类型为字符串。
# 需要注意的是，每一个在命令行中的用空格分隔的参数都需要单独一个字符串按顺序指定。以下为示例:
# customArgs = [
#   '--qq',
#   '12345678'
#   '--nodebug'
#   '-p',
#   '8190'     # 注意最后一个参数后没有逗号
# ]
# 上面的参数等价为: qqbot --qq 12345678 --nodebug -p 8190
# 如果不指定任何参数，请留空这个列表。
customArgs = [
    # 填写所需的参数。如果不指定命令行选项，请留空。

]

# 方法2. 从配置文件中加载。
# 配置文件存储位置请参考文档中的说明。
# 参数 user: 字符串: 配置文件中的配置项的名称。例如 user = 'somebody'
#                   填写None表示不使用此参数。

user = None

#
# =================================================================
#
# (2) QQbot功能接口
#
# 可以在下方增加自己的测试代码。也可以下断点来验证这些接口的功能。
# 以下的内容来自QQbot文档。
# 在此处可以查看最新版本的文档: https://github.com/pandolia/qqbot/blob/master/README.MD
#
# 可以使用 INFO(), CRITICAL(), ERROR(), DEBUG() 显示与QQbot输出消息格式一致的信息。

@qqbotslot
def onQQMessage(bot, contact, member, content):
    # 当收到 QQ 消息时被调用
    # bot     : QQBot 对象，提供 List/SendTo/Stop/Restart 四个接口，详见文档第五节
    # contact : QContact 对象，消息的发送者，具有 ctype/qq/uin/name/nick/mark/card 属性，这些属性都是 str 对象
    # member  : QContact 对象，仅当本消息为 群或讨论组 消息时有效，代表实际发消息的成员
    # content : str 对象，消息内容
        if contact.ctype != 'buddy':
        DEBUG("onQQMessage: ctype=" + contact.ctype + "  member=(qq=" + member.qq + ", uin=" + str(member.uin) + ", name=" + member.name + ')  uin=' + contact.uin + '  qq=' + contact.qq + '   name=' + contact.name)
    else:
        DEBUG("onQQMessage: ctype=" + contact.ctype + 'uin=' + contact.uin + '  qq=' + contact.qq + '  name=' + contact.name)

    pass

@qqbotslot
def onNewContact(bot, contact, owner):
    # 当新增 好友/群/讨论组/群成员/讨论组成员 时被调用
    # bot     : QQBot 对象
    # contact : QContact 对象，代表新增的联系人
    # owner   : QContact 对象，仅在新增 群成员/讨论组成员 时有效，代表新增成员所在的 群/讨论组
    pass

@qqbotslot
def onLostContact(bot, contact, owner):
    # 当失去 好友/群/讨论组/群成员/讨论组成员 时被调用
    # bot     : QQBot 对象
    # contact : QContact 对象，代表失去的联系人
    # owner   : QContact 对象，仅在失去 群成员/讨论组成员 时有效，代表失去成员所在的 群/讨论组
    pass

@qqbotslot
def onInterval(bot):
    # 每隔 5 分钟被调用
    # bot : QQBot 对象
    pass

@qqbotslot
def onStartupComplete(bot):
    # 启动工作全部完成时被调用（此时已登录成功，且已开始监听消息和 qterm 客户端命令）
    # bot : QQBot 对象
    pass

@qqbotslot
def onFetchComplete(bot):
    # 完成一轮联系人列表刷新时被调用
    # bot : QQBot 对象
    pass

# QQbot定时任务功能
# 本段函数可以多次出现。
# 关于此功能的详细说明请参见：https://github.com/pandolia/qqbot#定制定时任务

@qqbotsched(minute='*/1', second='0')
def mytask(bot):
    # 本段示例: 每分钟执行一次的任务。（在0秒时）
    # bot : QQBot 对象
    import time
    DEBUG('1min passed: '+time.asctime())

@qqbotsched(hour='*/1',minute='0',  second='0')
def mytask(bot):
    # 本段示例: 每小时执行一次的任务。（在0分0秒时）
    # bot : QQBot 对象
    import time
    DEBUG('1hour passed: '+time.asctime())

@qqbotsched(hour='0',minute='0',  second='0')
def mytask(bot):
    # 本段示例: 凌晨0点0分0秒时执行任务。
    # bot : QQBot 对象
    import time
    DEBUG('MidNight passed: '+time.asctime())

#
# =================================================================
#
# (3) QQbot初始化
#
# 初始化QQbot的启动参数。
for argItems in customArgs:
    sys.argv.append(str(argItems)) # 确保传入的数据的正确性。

# 避免自动增加引起错误的sys.argv中的参数。
# 由于PyCharm调试器的一些特性，需要增加这个参数来绕过qqbotcls.py中的runBot()中的增加参数的过程。
# 如果不绕过那个增加参数的过程，QQbot启动之后会被增加两个无效的参数，这会导致QQbot异常退出。
sys.argv.append('--subprocessCall')

# 正式启动QQbot。
RunBot(user=user, qq=qq)
# 注意: 此函数将永远不会有机会返回，因此在这一行之后的代码都不会被执行。