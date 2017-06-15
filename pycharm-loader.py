# -*- coding: utf-8 -*-

#!/usr/bin/python
# QQbot Loader for JetBrains PyCharm
#
# 作者     : SuperMarioSF
# 上次更新 : 2017-06-13 (QQbot v2.3.2)
#
# 由于从QQbot 2.3开始提供了用于IDE环境的启动与测试方式，
# 同时移除了相关用于非插件脚本加载函数的装饰器，
# 因此本文件现在只能作为从IDE中启动QQbot的入口。
#
# 在 qqbot/plugins 目录中提供了详细的插件开发相关的示例。
# 使用类似Pycharm这样的IDE开发时，请从本文件调试启动QQbot，
# 然后正常操作QQbot的qq命令来热插拔你正在编写的插件。


# 指定启动参数。详细请参见 qqbot 命令的帮助 （qqbot --help）。
args = [
    # 用户名
    '--user', 'username',
    
    #  QQ 号码
    '--qq', '12345678',
    
    # 插件目录
    '--pluginPath', '/my/plugin/path',
    
    # 启动时自动加载的插件
    '--plugins', 'plugin1,plugin2,plugin3',
    
    # 启动方式：慢启动（获取全部联系人之后再启动）
    '--startAfterFetch',
    
    # 打印调试信息
    '--debug',
]


if __name__ == "__main__":
    # 注意：此时重启功能无法使用
    from qqbot import _bot as bot
    bot.Login(args)
    bot.Run()
