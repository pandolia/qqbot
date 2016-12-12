一、介绍
---------

QQBot 是一个用 python 实现的、基于腾讯 SmartQQ 协议的简单 QQ 机器人，可运行在 Linux 、 Windows 和 Mac OSX 平台下。程序采用双线程的方式运行，且尽可能的减少了网络和登录错误（特别是所谓的 103 error ）的发生概率。

本项目 github 地址： <https://github.com/pandolia/qqbot>

你可以通过扩展 QQBot 来实现：

* 监控、收集 QQ 消息
* 自动消息推送
* 聊天机器人
* 通过 QQ 远程控制电脑、智能家电

二、安装方法
-------------

在 Python 2.7 下使用，用 pip 安装，安装命令：

    $ pip install qqbot

三、使用方法
-------------

##### 1. 启动 QQBot

在命令行输入： **qqbot** 。启动过程中会自动弹出二维码图片，需要用手机 QQ 客户端扫码并授权登录。启动成功后，会将本次登录信息保存到本地文件中，下次启动时，可以输入： **qqbot qq号码** ，先尝试从本地文件中恢复登录信息（不需要手动扫码），只有恢复不成功或登录信息已过期时才会需要手动扫码登录。一般来说，保存的登录信息将在 2 ~ 3 天之后过期。

##### 2. 操作 QQBot

QQ 机器人启动后，用另外一个 QQ 向本 QQ 发送消息即可操作 QQBot 。目前提供以下命令：

    1） 帮助：
        -help

    2） 列出 好友/群/讨论组:
        -list {buddy|group|discuss}

    3） 向 好友/群/讨论组 发送消息:
        -send {buddy|group|discuss} {buddy_qq|group_qq|discuss_uin} {message}
        注意：如果向 好友/群 发消息，则第三个参数为对方的 qq 号 ；
             如果向 讨论组  发消息，则第三个参数为对方的 uin， 需要通过 -list 命令来查看讨论组的 uin 。

    4） 列出 群/讨论组 的成员：
        -member {group|discuss} {group_qq|discuss_uin}

    5） 重新获取 好友/群/讨论组 列表：
        -refetch

    6） 停止 QQBot ：
        -stop

四、实现你自己的 QQ 机器人
---------------------------

实现自己的 QQ 机器人非常简单，只需要继承 **QQBot** 类并重写此类中的消息响应方法 **onPullComplete** 。示例代码：

    from qqbot import QQBot

    class MyQQBot(QQBot):
        def onPollComplete(self, msgType, from_uin, buddy_uin, message):
            if message == '-hello':
                self.send(msgType, from_uin, '你好，我是QQ机器人')
            elif message == '-stop':
                self.send(msgType, from_uin, 'QQ机器人已关闭')
                self.stop()

    myqqbot = MyQQBot()
    myqqbot.Login()
    myqqbot.Run()

以上代码运行后，用另外一个 QQ 向本 QQ 发送消息 **“-hello”**，则会自动回复 **“你好，我是 QQ 机器人”**，发送消息 **“-stop”** 则会关闭 QQ 机器人。

五、 QQBot 类中的主要方法、属性
--------------------------------

#### 1. 构造方法、登录方法、主要属性

    >>> bot = QQBot()
    >>> bot.Login()
    ...

构造方法生成一个 QQBot 实例，读取配置和命令行参数，并创建一个二维码管理器。所有登录、获取 好友/群/讨论组 列表的工作在 **Login** 方法中完成。如果在命令行参数中或配置文件中提供了自动登录 qq 号码，则会先尝试从本地恢复登录信息（不需要手动扫码），只有恢复不成功或登录信息已过期时才会需要手动扫码登录；如果没提供，则直接进行手动扫码登录。

QQBot 登录完成后，可以进行消息收发了，且 好友/群/讨论组 的列表保存在 **buddies, buddiesDictQ, buddiesDictU, buddyStr, groups, groupsDictU, groupsDictQ, groupStr, discusses, discussesDict, discussStr** 等属性当中。

    >>> bot.buddies
    [{'qq':1880557506, 'name':'Jack', 'uin':2311151202},
     {'qq':2776164208, 'name':'Mike', 'uin':4578565512},
     ...]
    >>> print bot.buddyStr
    好友列表：
    1880557506, Jack, uin2311151202
    2776164208, Mike, uin4578565512
    ...

#### 2. 消息收发

    >>> bot.poll()
    ('buddy', 207353438, 207353438, 'hello')
    >>> bot.poll()
    ('', 0, 0, '')
    >>> bot.send('buddy', 45789321, 'hello')
    向 好友mike 发消息成功

**poll** 方法向 QQ 服务器查询消息，如果有未读消息则会立即返回，返回值为一个四元 tuple ：

    (msgType, from_uin, buddy_uin, message)

其中 **msgType** 可以为 **'buddy'** 、 **'group'** 或 **'discuss'**，分别表示这是一个 **好友消息** 、**群消息** 或 **讨论组消息** ； **from_uin** 和 **buddy_uin** 代表消息发送者的 **uin** ，可以通过 uin 向发送者回复消息，如果这是一个好友消息，则 from_uin 和 buddy_uin 相同，均为好友的 uin ，如果是群消息或讨论组消息，则 from_uin 为该群或讨论组的 uin ， buddy_uin 为消息发送人的 uin ； **message** 为消息内容，是一个 **utf8** 编码的 string 。

如果没有未读消息，则 **poll** 方法会一直等待两分钟，若期间没有其他人发消息过来，则返回一个只含空值的四元 tuple ：

    ('', 0, 0, '')

**send** 方法的三个参数为 **msgType** 、 **to_uin** 和 **message** ，分别代表 **消息类型** 、**接收者的 uin** 以及 **消息内容** ，消息内容必须是一个 **utf8** 编码的 string 。

请注意：这里说的 **uin** 不是 好友/群/讨论组 的 **qq 号码** ，而是每次登录成功后给该 好友/群/讨论组 分配的的一个 **临时 id** 。用以下语句可以通过 **uin** 获得好友 **qq 号码**：

    self.getBuddyByUin(uin)['qq']

用以下语句可以通过 **qq 号码** 获得好友的 **uin**：

    self.getBuddyByQQ(qq)['uin']

如果发送消息的频率过快， qq 号码可能会被锁定甚至封号。因此每发送一条消息之前，会强制 sleep 3~5 秒钟，每发送 10 条消息之前，会强制 sleep 10 秒钟。

这里需要注意的是，当 poll 方法因等待消息而阻塞时，可以在另一个线程中调用同一个实例的 send 方法发送消息。但是，不要试图在多个线程中并行的调用同一个实例的 send 方法，否则可能引起一些无法预料的错误。

#### 3. 无限消息轮询

##### （1） 单线程运行方式

在 1.6.2 及以前的版本中，本程序采用单线程的方式运行：

    >>> bot.PullForever()
    ...

**PullForever** 方法会不停的调用 poll 方法，并将 poll 方法的返回值传递给 **onPullComplete** 方法，直到 stopped 属性变为 True 。如下：

    def PollForever(self):
        self.stopped = False
        while not self.stopped:
            pullResult = self.poll()
            self.onPollComplete(*pullResult)

##### （2） 双线程运行方式

在 1.7.1 及之后的版本中，程序采用双线程的方式运行，每个 QQBot 实例类维护一个消息队列：

    self.msgQueue = Queue.Queue()

在一个单独的线程中查询消息，并将查询到的消息放入消息队列中：

    def pollForever(self):
        while not self.stopped:
            pullResult = self.poll()
            self.msgQueue.put(pullResult)

主线程则不停的从 msgQueue 中取出消息，并将其传递给 onPullComplete 方法：

    def Run(self):
        self.msgQueue = Queue.Queue()
        self.stopped = False
        threading.Thread(target=self.pullForever).start()
        while not self.stopped:
            pullResult = self.msgQueue.get()
            self.onPullComplete(*pullResult)

onPollComplete 方法是 QQ 机器人的灵魂。你可以自由发挥，重写此方法，实现更智能的机器人。

六、二维码管理器、QQBot 配置、掉线后自动重启
-----------------------------------------

SmartQQ 登录时需要用手机 QQ 扫描二维码图片，在 QQBot 中，二维码图片可以通过以下三种模式显示：

* GUI模式： 在 GUI 界面中自动弹出二维码图片
* 邮箱模式： 将二维码图片发送到指定的邮箱
* 网页模式： 在一个 HTTP 服务器中显示二维码图片（用浏览器打开）

GUI 模式是默认的模式，只适用于个人电脑上，邮箱模式和网页模式可以适用于个人电脑和远程服务器。最方便的是使用 QQ 邮箱的邮箱模式，当发送二维码图片后，手机 QQ 客户端一般会立即收到通知，在手机 QQ 客户端上打开邮件，并长按二维码就可以扫描了。

每个 QQBot 实例都会创建一个二维码管理器 （QrcodeManager） ，二维码管理器会根据配置文件来选择二维码图片的显示方式。配置文件为 **~/.qqbot-tmp/qqbot.conf** ，第一次运行 QQBot 后就会自动创建这个配置文件，其中内容如下：

    {
    # QQBot 的配置文件
    
    # 显示/关闭调试信息，默认为 False
    "debug" : False,
    
    # QQBot 掉线后自动重启，默认为 False
    "restartOnOffline" : False,
    
    # 服务器的 IP 或域名，默认为 ""
    "httpServerName" : "",
    
    # 服务器的端口，仅 httpServerName 不为 "" 时有效，默认为 8080
    "httpServerPort" : 8080,
    
    # 用户信息
    "userInfo" : {
    
        # 用户 DEFAULT ，默认用户
        "DEFAULT" : {
        
            # 自动登录的 QQ 号（i.e. "3497303033"），默认为 ""
            "QQ" : "",
            
            # 接收二维码图片的邮箱账号（i.e. "3497303033@qq.com"），默认为 ""
            "mailAccount" : "",
            
            # 该邮箱的 IMAP/SMTP 服务授权码（i.e. "feregfgftrasdsew"），默认为 ""
            "mailAuthCode" : "",
    
        },
    
        # 用户 somebody
        "somebody" : {
            "QQ" : "",
            "mailAccount" : "",
            "mailAuthCode" : "",
        },
    
    },
    
    }

如果需要使用网页模式，则可以在 httpServerName 项中设置服务器的 IP 或域名，在 httpServerPort 中设置服务器的端口号， QQBot 启动时，二维码管理器会在子进程中开启一个 HTTP 服务器来显示二维码图片。同一个系统中所有的 QQBot 实例都共用此服务器（不同 QQBot 实例的二维码图片的网址不相同）。

如果需要使用邮箱模式，可以在 userInfo 项中新增一个用户（如 somebody ），在该用户下的 mailAccount 和 mailAuthCode 项中分别设置邮箱帐号和授权码，启动 QQBot 时，输入 qqbot somebody ，开始运行后，二维码管理器会将二维码图片发送至该邮箱。如果在 DEFAULT 用户下设置这两项，则直接输入 qqbot 就可以了。

注意：授权码不是邮箱的登录密码，而是邮箱服务商提供的开通 IMAP/SMTP 服务的授权码， QQ 邮箱可以在网页版的邮箱设置里面开通此项服务，并得到授权码。如果只定义了 mailAccount 而没定义 mailAuthCode ，则程序运行的开始时会要求手工输入此授权码。

由于网易的邮箱对 IMAP 协议的支持非常有限，无法在 QQBot 中使用。 QQ 的邮箱已通过测试，其他服务商的邮箱还未测试过，因此建议还是使用 QQ 邮箱。

GUI 模式是默认的显示模式，但当开启了邮箱模式或网页模式中的任一项时，GUI 模式的是关闭的。当开启了邮箱模式但没有开启网页模式时，会将实际的二维码图片发送到邮箱。而当邮箱模式和网页模式同时开启时，只会将二维码的网址发送到邮箱中，为保证手机 QQ 上可以显示此图片，应保证服务器使用的是公网 IP 。

配置文件中每个用户都有 QQ 这一项，如果在某用户（如 somebody ）下设置了此项，则在命令行中输入 qqbot somebody 启动后，会先使用此 QQ 号上次登录保存的登录信息来自动登录。同样，如果在 DEFAULT 用户在设置此项，则直接输入 qqbot 就可以了。

如果配置文件中将 restartOnOffline 项设置为 True ，则当 QQBot 掉线或出错终止时，会自动重新启动 QQBot 。注意使用此模式时，在 Windows 下不能用 “qqbot” 命令运行 QQBot ，暂时只能通过 “python C:\Python27\Lib\site-packages\qqbot\qqbot.py” 的方式运行。

七、精简版的 QQBot
-------------------

本项目 1.8.7.1 及之前的版本代码量非常精简，所有代码都集成在一个 [qqbot.py][code] 文件中，代码量仅 500 余行，但已经包含了登录、好友列表和收发消息的等核心功能。如果想研究 QQBot 的核心代码、或研究SmartQQ 协议的具体细节，可以先看看这个这个版本： <https://github.com/pandolia/qqbot/tree/v1.8.7.1> 

[code]: https://raw.githubusercontent.com/pandolia/qqbot/v1.8.7.1/qqbot.py

八、参考资料
-------------

QQBot 参考了以下开源项目：

- [ScienJus/qqbot](https://github.com/ScienJus/qqbot) （ruby）
- [floatinghotpot/qqbot](https://github.com/floatinghotpot/qqbot) （node.js）

在此感谢以上两位作者的无私分享，特别是感谢 ScienJus 对 SmartQQ 协议所做出的深入细致的分析。

九、反馈
---------

有任何问题或建议可以发邮件给我 <pandolia@yeah.net> 或者直接提 issue 。
