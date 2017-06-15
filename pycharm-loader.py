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

from qqbot import _bot as bot

# 初始化
qq = None
user = None

# 配置
#qq = '12345678' # 解除注释后填写自己的QQ号码，用于快速登陆。

# 指定启动时加载的插件。
initPlugins=[

]

# 指定额外的启动参数。详细请参见qqbot命令的帮助。
customArgs = [
    '-saf',
    '--debug',
]


if __name__ == "__main__":
    loginopt=[]
    if not qq is None:
        loginopt=['-q', qq]
    elif not user is None:
        loginopt=['-u', user]
    else:
        print("注意: 没有指定任何登陆方式。")
    launchopt=[]
    launchopt.extend(op for op in loginopt)
    launchopt.extend(customArgs)
    if len(initPlugins) > 0:
        launchopt.append("-pl")
        plgnames= ""
        plgnames=initPlugins[0]
        for plg in initPlugins[1:]:
            plgnames= ',' + plg
        launchopt.append(plgnames)

    print("正在使用以下参数启动:" + str(launchopt))
    bot.Login(list(launchopt))
    bot.Run()