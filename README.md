一、介绍
---------

QQBot 是一个用 python 实现的、基于腾讯 SmartQQ 协议的简单 QQ 机器人，可运行在 Linux 、 Windows 和 Mac OSX 平台下，所有代码均集成在一个 [qqbot.py][code] 文件中，代码量仅 500 余行（不包括注释）。程序采用双线程的方式运行，且尽可能的减少了网络和登录错误（特别是所谓的 103 error ）发生的概率。

[code]: https://raw.githubusercontent.com/pandolia/qqbot/master/qqbot.py

本项目 github 地址： <https://github.com/pandolia/qqbot/>

你可以通过扩展 QQBot 来实现：

* 监控、收集 QQ 消息
* 自动消息推送
* 聊天机器人
* 通过 QQ 远程控制电脑、智能家电


二、安装方法
-------------

在 Python 2.7 下使用，用 pip 安装，安装命令：

    $ pip install qqbot

也可以直接下载 [qqbot.py][code] 运行，但需先安装 [requests](https://pypi.python.org/pypi/requests) 库。

三、使用方法
-------------

##### 1. 启动 QQBot

在命令行输入： **qqbot** ，或直接运行 [qqbot.py][code] ： **python qqbot.py** 。启动过程中会自动弹出二维码图片（Linux下需安装有 gvfs ，否则需要手动打开图片），需要用手机 QQ 客户端扫码并授权登录。启动成功后，会将本次登录信息保存到本地文件中，下次启动时，可以输入： **qqbot qq号码**，或：**python qqbot.py qq号码** ，先尝试从本地文件中恢复登录信息（不需要手动扫码），只有恢复不成功或登录信息已过期时才会需要手动扫码登录。

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

    4） 重新获取 好友/群/讨论组 列表：
        -refetch
    
    5） 停止 QQBot ：
        -stop

四、实现你自己的 QQ 机器人
---------------------------

实现自己的 QQ 机器人非常简单，只需要继承 [qqbot.py][code] 中提供的 **QQBot** 类并重新实现此类中的消息响应方法 **onPullComplete** 。示例代码：

    from qqbot import QQBot
    
    class MyQQBot(QQBot):
        def onPollComplete(self, msgType, from_uin, buddy_uin, message):
            if message == '-hello':
                self.send(msgType, from_uin, '你好，我是QQ机器人')
            elif message == '-stop':
                self.stopped = True
                self.send(msgType, from_uin, 'QQ机器人已关闭')
    
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

构造方法生成一个 QQBot 实例，其实没做任何工作。全部的登录、获取 好友/群/讨论组 列表的工作在 **Login** 方法中完成。Login 方法会检查命令行参数 sys.argv 中是否提供了 qq 号码。若没有提供 qq 号码，则需要手动扫码登录。登录后会将登录信息保存在本地。若提供了 qq 号码，则会先尝试从本地恢复会话信息（不需要手动扫码），只有恢复不成功或登录信息已过期时才会需要手动扫码登录。

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
    向buddy45789321发送消息成功

**poll** 方法向 QQ 服务器查询消息，如果有未读消息则会立即返回，返回值为一个四元 tuple ：

    (msgType, from_uin, buddy_uin, message)

其中 **msgType** 可以为 **'buddy'** 、 **'group'** 或 **'discuss'**，分别表示这是一个 **好友消息** 、**群消息** 或 **讨论组消息** ； **from_uin** 和 **buddy_uin** 代表消息发送者的 **uin** ，可以通过 uin 向发送者回复消息，如果这是一个好友消息，则 from_uin 和 buddy_uin 相同，均为好友的 uin ，如果是群消息或讨论组消息，则 from_uin 为该群或讨论组的 uin ， buddy_uin 为消息发送人的 uin ； **message** 为消息内容，是一个 **utf8** 编码的 string 。

如果没有未读消息，则 **poll** 方法会一直等待两分钟，若期间没有其他人发消息过来，则返回一个只含空值的四元 tuple ：

    ('', 0, 0, '')

**send** 方法的三个参数为 **msgType** 、 **to_uin** 和 **message** ，分别代表 **消息类型** 、**接收者的 uin** 以及 **消息内容** ，消息内容必须是一个 **utf8** 编码的 string 。

请注意：这里说的 **uin** 不是 好友/群/讨论组 的 **qq 号码** ，而是每次登录成功后给该 好友/群/讨论组 分配的的一个 **临时 id** 。用以下语句可以通过 **uin** 获得好友 **qq 号码**：

    self.buddiesDictU[uin]['qq']

用以下语句可以通过 **qq 号码** 获得好友的 **uin**：

    self.buddiesDictQ[qq]['uin']

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

六、参考资料
-------------

QQBot 参考了以下开源项目：

- [ScienJus/qqbot](https://github.com/ScienJus/qqbot) （ruby）
- [floatinghotpot/qqbot](https://github.com/floatinghotpot/qqbot) （node.js）

在此感谢以上两位作者的无私分享，特别是感谢 ScienJus 对 SmartQQ 协议所做出的深入细致的分析。

七、反馈
---------

有任何问题或建议可以发邮件给我，邮箱： <pandolia@yeah.net> 。
