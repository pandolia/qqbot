一、问题目录
-------------

- [python初学者需注意的问题](https://github.com/pandolia/qqbot/blob/master/faq.md#python%E5%88%9D%E5%AD%A6%E8%80%85%E9%9C%80%E6%B3%A8%E6%84%8F%E7%9A%84%E9%97%AE%E9%A2%98)
- [qqbot 的配置文件放在哪里？](https://github.com/pandolia/qqbot#%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6%E7%9A%84%E4%BD%BF%E7%94%A8%E6%96%B9%E6%B3%95)
- [qqbot 的插件应保存在哪个目录？](https://github.com/pandolia/qqbot#%E5%85%AB-%E6%8F%92%E4%BB%B6)
- [如何修改配置文件和插件的保存目录？](https://github.com/pandolia/qqbot#%E5%B7%A5%E4%BD%9C%E7%9B%AE%E5%BD%95)
- [为什么修改了配置没有生效？](https://github.com/pandolia/qqbot/blob/master/faq.md#%E4%B8%BA%E4%BB%80%E4%B9%88%E4%BF%AE%E6%94%B9%E4%BA%86%E9%85%8D%E7%BD%AE%E6%B2%A1%E6%9C%89%E7%94%9F%E6%95%88)
- [onQQMessage 函数中如何获取消息发送者的 QQ 号码等信息？](https://github.com/pandolia/qqbot/blob/master/faq.md#onqqmessage-%E5%87%BD%E6%95%B0%E4%B8%AD%E5%A6%82%E4%BD%95%E8%8E%B7%E5%8F%96%E6%B6%88%E6%81%AF%E5%8F%91%E9%80%81%E8%80%85%E7%9A%84-qq-%E5%8F%B7%E7%A0%81%E7%AD%89%E4%BF%A1%E6%81%AF)
- [onQQMessage 函数中如何判断消息是好友消息还是群消息？](https://github.com/pandolia/qqbot/blob/master/faq.md#onqqmessage-%E5%87%BD%E6%95%B0%E4%B8%AD%E5%A6%82%E4%BD%95%E5%88%A4%E6%96%AD%E6%B6%88%E6%81%AF%E6%98%AF%E5%A5%BD%E5%8F%8B%E6%B6%88%E6%81%AF%E8%BF%98%E6%98%AF%E7%BE%A4%E6%B6%88%E6%81%AF)
- [为什么有时候会重复发消息，有无解决办法？](https://github.com/pandolia/qqbot#3-botsendtocontact-content-resendon1202true----%E5%90%91-xx-%E5%8F%91%E6%B6%88%E6%81%AF%E6%88%90%E5%8A%9F%E9%94%99%E8%AF%AF)
- [如何判断是否是自己发的群消息？](https://github.com/pandolia/qqbot#%E5%88%A4%E6%96%AD%E6%98%AF%E5%90%A6%E6%98%AF%E8%87%AA%E5%B7%B1%E5%8F%91%E7%9A%84%E6%B6%88%E6%81%AF)
- [onInterval 函数是否可以自己设置调用的间隔时间？](https://github.com/pandolia/qqbot/blob/master/faq.md#oninterval-%E5%87%BD%E6%95%B0%E6%98%AF%E5%90%A6%E5%8F%AF%E4%BB%A5%E8%87%AA%E5%B7%B1%E8%AE%BE%E7%BD%AE%E8%B0%83%E7%94%A8%E7%9A%84%E9%97%B4%E9%9A%94%E6%97%B6%E9%97%B4)
- [如何稳定的长期保持在线？](https://github.com/pandolia/qqbot/blob/master/faq.md#%E5%A6%82%E4%BD%95%E7%A8%B3%E5%AE%9A%E7%9A%84%E9%95%BF%E6%9C%9F%E4%BF%9D%E6%8C%81%E5%9C%A8%E7%BA%BF)
- [如何采用 virtualenv 将本项目安装至独立的运行环境？](https://github.com/pandolia/qqbot/blob/master/faq.md#%E5%A6%82%E4%BD%95%E9%87%87%E7%94%A8-virtualenv-%E5%B0%86%E6%9C%AC%E9%A1%B9%E7%9B%AE%E5%AE%89%E8%A3%85%E8%87%B3%E7%8B%AC%E7%AB%8B%E7%9A%84%E8%BF%90%E8%A1%8C%E7%8E%AF%E5%A2%83)

二、问题的回答
-------------

#### python初学者需注意的问题

- 建议先系统的学习一下 python 的语法，参考资料： [python3 教程](https://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000)
- 建议学习和使用 python3 ，建议使用 [PyCharm IDE](https://www.jetbrains.com/pycharm/)
- python 脚本的开头要加上 “# -\*- coding: utf-8 -\*-” ，并保存为 utf8 编码格式
- 不要把你的脚本文件保存为 qqbot.py 或 sys.py ，或系统中已有的库或关键字的名字；也不要在脚本中将变量、函数等命名为 qqbot/sys/time 等名字。

#### 为什么修改了配置没有生效？

请确认是在配置文件中的 somebody 项下修改的配置，并且是以 qqbot -u somebody 的方式启动。

当然，也可以自己新增一个 xxx 的项，并以 qqbot -u xxx 的方式启动。

如果你已理解配置文件中的配置优先级和命令行参数，可以修改“默认配置”，或者在命令行参数中修改配置。

#### onQQMessage 函数中如何获取消息发送者的 QQ 号码等信息？

使用该函数中第二、三个参数 contact 和 member 的 qq 等属性，如 contact.qq / contact.name 等。详见： [联系人对象的属性](https://github.com/pandolia/qqbot/blob/master/qcontact-attr.md)。

注意： member 有时侯可能为 None 。

#### onQQMessage 函数中如何判断消息是好友消息还是群消息？

contact.ctype 为 'buddy'/'group'/'discuss' 时，分别代表本消息时 好友消息/群消息/讨论组消息 。

#### onInterval 函数是否可以自己设置调用的间隔时间？

不能。建议使用 qqbotsched 装饰器，功能更加强大。

#### 如何稳定的长期保持在线？

由于 smartqq 协议的限制，每次登录成功后的 cookie 会每在 1 ~ 2 天后失效，将被腾讯服务器强制下线，此时 **必须** 手工扫码重新登录，因此无法稳定的长期保持在线。

可以打开邮箱模式和自动重启模式，并配合 qqbot.plugins.schedrestart 插件使用，每天在固定的时间扫码登录一次，基本上可以稳定的保持在线状态。建议直接使用 QQ 邮箱，这样发送二维码邮件后手机 QQ 可以马上收到通知，直接用手机 QQ 打开邮件并长按二维码图片就可以扫码了。

#### 如何采用 virtualenv 将本项目安装至独立的运行环境？

本项目依赖于 reqests 、flask 、 certifi 和 apscheduler 库，用 pip 安装本项目时会自动安装以上四个库以及它们所依赖的库。一般来说安装本项目不会与系统其他项目冲突，因此可直接安装至系统的全局 site-packages 目录。

在某些系统中可能会出现 https 请求错误，这时需要安装 certifi 库的指定版本（2015.4.28 版），可能会将系统中已有的 certifi 库升级或降级并导致会使系统中的其他项目无法使用，这时可以使用 virtualenv 将本项目安装至独立的运行环境中。

另外，Windows 下的用户有时需要使用 pyinstaller 打包自己利用 qqbot 开发的程序，此时也建议使用 virtualenv 将 qqbot 以及 pyinstaller 安装至独立的运行环境中，然后利用此环境中的 pyinstaller 进行打包。

virtualenv 基本原理和使用可参考 [廖雪峰的教程](http://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/001432712108300322c61f256c74803b43bfd65c6f8d0d0000) 。

以下脚本（Linux下）将在 ~/PyVenv/qqbot-venv 目录下创建一个独立的运行环境，并将 qqbot 及其依赖的库安装至 ~/PyVenv/qqbot-env/lib/site-packages 目录下。系统中的原有的库不会被改动，其他项目不受影响。

    sudo pip install virtualenv

    mkdir ~/PyVenv
    cd ~/PyVenv
    virtualenv --no-site-packages qqbot-venv

    source ~/PyVenv/qqbot-env/bin/activate

    pip install requests==2.7.0
    pip install certifi==2015.4.28
    pip install flask==0.12
    pip install apscheduler==3.3.1
    pip install qqbot

注意：使用本方式安装本项目后，每次使用 qqbot 和 qq 命令之前，需要先运行下面这条命令激活 qqbot-venv 下的运行环境：

    source ~/PyVenv/qqbot-env/bin/activate

Windows 下， 上述脚本改为：

    pip install virtualenv
    
    c:
    mkdir %UserProfile%\PyVenv
    cd %UserProfile%\PyVenv
    virtualenv --no-site-packages qqbot-env

    %UserProfile%\PyVenv\qqbot-env\Scripts\activate

    pip install requests==2.7.0
    pip install certifi==2015.4.28
    pip install flask==0.12
    pip install apscheduler==3.3.1
    pip install qqbot

其中 %UserProfile% 是用户主目录，Win7中为 C:\Users\xxx 目录。

Windows 下如果需要使用 pyinstaller 打包，还需要安装 pyinstaller 和 pypiwin32 ：

    pip install pyinstaller==3.2.1
    pip install pypiwin32==219

然后在 %UserProfile%\PyVenv\qqbot-env 下新建一个目录 myapp ：
    
    cd %UserProfile%\PyVenv\qqbot-env
    mkdir myapp
    cd myapp

在该目录下新建一个 main.py ，内容为：

    from qqbot import Main; Main()

再新建一个 hook-ctypes.macholib.py ，内容为：

    from PyInstaller.utils.hooks import copy_metadata
    datas = copy_metadata('apscheduler')

最后，输入以下命令将 main.py 打包为 dist\main.exe

    ..\Scripts\pyinstaller -F main.py --additional-hooks-dir=.
