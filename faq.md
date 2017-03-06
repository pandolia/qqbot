

#### 1.采用 virtualenv 将本项目安装至独立的运行环境

本项目依赖于 reqests 、flask 和 certifi 库，用 pip 安装本项目时会自动安装以上三个库以及它们所依赖的库。一般来说安装本项目不会与系统其他项目冲突，因此可直接安装至系统的全局 site-packages 目录。

在某些系统中可能会出现 https 请求错误，这时需要安装 certifi 库的指定版本（2015.4.28 版），可能会将系统中已有的 certifi 库升级或降级，可能会使系统中的其他项目无法使用，这时可以使用 virtualenv 将本项目安装至独立的运行环境中。

virtualenv 基本原理和使用可参考 [廖雪峰的教程](http://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/001432712108300322c61f256c74803b43bfd65c6f8d0d0000) 。

以下脚本将在 ~/PyVenv/qqbot-venv 目录下创建一个独立的运行环境，并将 qqbot 及其依赖的库安装至 ~/PyVenv/qqbot-env/lib/site-packages 目录下。系统中的原有的库不会被改动，其他项目不受影响。

    sudo pip install virtualenv

    mkdir ~/PyVenv
    cd ~/PyVenv
    virtualenv --no-site-packages qqbot-venv

    source ~/PyVenv/qqbot-env/bin/activate

    pip install requests==2.7.0
    pip install certifi==2015.4.28
    pip install flask==0.12
    pip install qqbot

注意：使用本方式安装本项目后，每次使用 qqbot 和 qq 命令之前，需要先运行下面这条命令激活 qqbot-venv 下的运行环境：

    source ~/PyVenv/qqbot-env/bin/activate

#### 2. 本程序的运行方式

本程序采用 信息/响应 的方式运行，后台开启两个子线程，分别运行 pollForever 、 termServer.Run ，分别负责 **QQ 消息轮询** 和 **qterm 客户端消息监听** ，子线程收到消息时，会向主线程发信息（实际是将一个 Message 对象放入一个队列中去）。主线程不停的从信息队列中取出信息，并根据信息类型调用相应的回调函数。所有对联系人资料的查询和更新等操作均在主线程中完成，避免了多个线程对同一个数据进行操作。

pollForever 不停的调用 poll 方法向腾讯服务器查询 QQ 消息。如果有未读消息， poll 方法会立即返回该消息，此时 pollFoever 方法会根据该消息生成一个 QQMessage 对象，并将此对象放到信息队列中去，主线程取出该对象后，会调用 On('qqmessage') 注册的回调函数；如果没有未读消息， poll 方法会阻塞一分钟并返回一个空消息，此时 pollForever 方法会生成一个类型为 'polltimeout' 的 Message 对象，并将该对象放到信息队列中去，主线程取出该对象后，会调用 On('polltimeout') 注册的回调函数。


#### 3.实现定时发送消息

根据上面所描述的程序运行方式，要实现定时发消息最简单的办法是注册一个 'polltimeout' 的回调函数。示例：

    import time

    from qqbot import QQBot

    myqqbot = QQBot()

    last = time.time()

    @myqqbot.On('polltimeout')
    def handler(bot, message):
        now = time.time()
        if now - last >= 3600:
            bot.Send('buddy', qq='478568453', '这时一个定时消息')
            last = now

    myqqbot.LoginAndRun()

在没有 QQ 消息的情况下，上面注册的 handler 函数会每隔一分钟被调用一次。因此以上脚本可以实现每隔约 1 小时给指定的人发消息。

