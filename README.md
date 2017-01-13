一、介绍
---------

QQBot 是一个用 python 实现的、基于腾讯 SmartQQ 协议的简单 QQ 机器人，可运行在 Linux 、 Windows 和 Mac OSX 平台下。

本项目 github 地址： <https://github.com/pandolia/qqbot>

你可以通过扩展 QQBot 来实现：

* 监控、收集 QQ 消息
* 自动消息推送
* 聊天机器人
* 通过 QQ 远程控制你的设备

二、安装方法
-------------

在 Python 2.7 下使用，用 pip 安装，安装命令：

    $ pip install qqbot

三、使用方法
-------------

##### 1. 启动 QQBot

在命令行输入： **qqbot** 。启动过程中会自动弹出二维码图片，需要用手机 QQ 客户端扫码并授权登录。启动成功后，会将本次登录信息保存到本地文件中，下次启动时，可以输入： **qqbot -q qq号码** ，先尝试从本地文件中恢复登录信息（不需要手动扫码），只有恢复不成功或登录信息已过期时才会需要手动扫码登录。一般来说，保存的登录信息将在 2 ~ 3 天之后过期。

##### 2. 操作 QQBot

QQ 机器人启动后，会自动弹出一个控制台窗口（ qterm 客户端）用来输入操作 QQBot 的命令，目前提供以下命令：

    1） 帮助
        help

    2） 列出所有 好友/群/讨论组
        list buddy|group|discuss

    3） 向 好友/群/讨论组 发送消息
        send buddy|group|discuss x|uin=x|qq=x|name=x message

    4） 获取 好友/群/讨论组 的信息
        get buddy|group|discuss x|uin=x|qq=x|name=x
    
    5) 获取 群/讨论组 的成员
        member group|discuss x|uin=x|qq=x|name=x

    5） 停止 QQBot
        stop

在 send/get/member 命令中，第三个参数可以是 好友/群/讨论组 的 昵称、 QQ 号码 或者 uin 。

也可以用另外一个 QQ 向本 QQ 发消息来操作 QQBot ，但需要在以上命令前加 “-” ，如 “-send buddy jack hello” 。

注意：如果系统中没有图形界面，则不会自动弹出控制台窗口，需要手动在另外的控制台中输入 “qterm” 命令来打开 qterm 客户端。

四、实现你自己的 QQ 机器人
---------------------------

实现自己的 QQ 机器人非常简单，只需要生成一个 **QQBot** 对象并为其注册一个消息响应函数。示例代码：

    from qqbot import QQBot
    
    myqqbot = QQBot()
    
    @myqqbot.On('qqmessage')
    def handler(bot, message):
        if message.content == '-hello':
            bot.SendTo(message.contact, '你好，我是QQ机器人')
        elif message.content == '-stop':
            bot.SendTo(message.contact, 'QQ机器人已关闭')
            bot.Stop()
    
    myqqbot.Login()
    myqqbot.Run()

以上代码运行后，用另外一个 QQ 向本 QQ 发送消息 **“-hello”**，则会自动回复 **“你好，我是 QQ 机器人”**，发送消息 **“-stop”** 则会关闭 QQ 机器人。

QQBot 对象收到一条 QQ 消息时，会新建一个 QQMessage 对象，之后将这个 QQMessage 对象以及自身传递给消息响应函数。

消息响应函数中的第一个参数为传递来的 QQBot 对象，也就是 myqqbot ，第二个参数是传递来的 QQMessage 对象，该对象主要有以下四个属性：

    message.contact    ： 消息发送者（QContact对象）
    message.memberUin  ： str 对象，消息发送成员的 uin，仅在该消息为 群/讨论组 消息时有效
    message.memberName ： str 对象，消息发送成员的昵称，仅在该消息为 群/讨论组 消息时有效
    message.content    ： str 对象，消息内容

QQMessage 对象还提供一个 Reply 接口，可以给消息发送者回复消息，如：

    message.Reply('你好，我是QQ机器人') # 相当于 bot.SendTo(message.contact, '你好，我是QQ机器人')

message.contact 是一个 QContact 对象，该对象有以下属性：
    
    contact.ctype 	: str 对象，联系人类型，可以为 'buddy', 'group', 'discuss' ，代表 好友/群/讨论组
    contact.uin 	: str 对象，联系人的 uin ，底层发消息要使用本数值，每次登录本数值可能会改变
    contact.qq		: str 对象，联系人的 qq
    contact.name	: str 对象，联系人的网名
    contact.members	: dict 对象，成员字典，仅在该联系人为 群/讨论组 时有效

还提供一个 GetMemberName 接口，可以通过成员的 uin 查询成员的网名：

    contact.GetMemberName(memberUin) --> memberName, str object
    

五、 QQBot 对象的接口
--------------------------------

QQBot 对象调用其 Login 方法登录成功后，提供 List/Get/SendTo/Send/On 五个接口，一般来说，只需要调用这五个接口就可以了，不必关心 QQBot 的内部细节。

### bot.List(ctype) --> [contact0, contact1, ..., ]

对应上面的 list 命令，示例：

    >>> bot.List('buddy')
    >>> bot.List('group')
    >>> bot.List('discuss')
    ...

返回一个联系人对象（QContact对象）列表。

### bot.Get(ctype, \*args, \*\*kwargs) --> [contact0, contact1, ..., ]

对应上面的 get 命令，示例：

    >>> bot.Get('buddy', 'jack')
    >>> bot.Get('group', '1234556')
    >>> bot.Get('buddy', 'qq=1235778')
    >>> bot.Get('buddy', uin='1234768')
    >>> bot.Get('discuss', name='disc-name')

第二个参数可以为联系人的 QQ号/网名/uin ，注意，这里返回的是一个 QContact 对象的列表，而不是返回一个 QContact 对象。

### bot.SendTo(contact, content) --> '向 xx 发消息成功'

向联系人发送消息。第一个参数为 QContact 对象，一般通过 Get 接口得到，第二个参数为消息内容。

### bot.Send(ctype, \*args, \*\*kwargs) --> ['向 xx 发消息成功', '向 xx 发消息成功...', ..., ]

对应上面的 send 命令，示例：

    >>> bot.Send('buddy', 'jack', 'hello')
    >>> bot.Send('group', '1234556', 'hello')
    >>> bot.Send('buddy', 'qq=1235778', 'hello')
    >>> bot.Send('buddy', uin='1234768', content='hello')
    >>> bot.Send('discuss', name='disc-name', content='hello')

Send 接口的第一、二个参数和 Get 接口的一样，第三个参数为消息内容。上面的第一条语句相当于：

    result = []
    for contact in bot.Get('buddy', 'jack'):
	    result.append(bot.SendTo(contact, 'hello'))
    return result

### bot.On(mtype, callback) --> callback

注册消息响应函数。第一个参数 mtype 为需要响应的消息的类型，一般来说，只需要响应 QQ 消息和 qterm 客户端消息， mtype 分别为 'qqmessage' 和 'termmessage' 。第二个参数 callback 为消息响应函数。

当 QQBot 收到这两种消息时，会新建一个 QQMessage 对象或 TermMessage 对象，连同 QQBot 对象本身一起传递给 callback 。这两种消息对象都有 content 属性和 Reply 接口，content 代表消息内容， Reply 接口可以向消息的发送者回复消息，对于 TermMessage 对象，消息发送者就是 qterm 客户端，注意，对于所有 TermMessage ，都必须调用一次 Reply ，否则 qterm 客户端会一直等待此回复消息。

六、二维码管理器、QQBot 配置、掉线后自动重启、命令行参数
------------------------------------------------

SmartQQ 登录时需要用手机 QQ 扫描二维码图片，在 QQBot 中，二维码图片可以通过以下两种模式显示：

* GUI模式： 在 GUI 界面中自动弹出二维码图片
* 邮箱模式： 将二维码图片发送到指定的邮箱

GUI 模式是默认的模式。邮箱模式开启时，会关闭 GUI 模式。GUI 模式只适用于个人电脑，邮箱模式可以适用于个人电脑和远程服务器。最方便的是使用 QQ 邮箱的邮箱模式，当发送二维码图片后，手机 QQ 客户端一般会立即收到通知，在手机 QQ 客户端上打开邮件，并长按二维码就可以扫描了。

每次登录时会创建一个二维码管理器 （QrcodeManager 对象） ，二维码管理器会根据配置文件及命令行参数来选择二维码图片的显示方式。

配置文件为 **~/.qqbot-tmp/v2.x.x.conf** ，第一次运行 QQBot 后就会自动创建这个配置文件，其中内容如下：
    
    {
    
        # QQBot 的配置文件
        
        # 用户 somebody 的配置
        "somebody" : {
            
            # QQBot-term 服务器端口号
            "termServerPort" : 8188,
            
            # 自动登录的 QQ 号
            "qq" : "3497303033",
            
            # 接收二维码图片的邮箱账号
            "mailAccount" : "3497303033@qq.com",
            
            # 该邮箱的 IMAP/SMTP 服务授权码
            "mailAuthCode" : "feregfgftrasdsew",
        
            # 显示/关闭调试信息
            "debug" : False,
    
            # QQBot 掉线后自动重启
            "restartOnOffline" : False,
        
        },
        
        # 请勿修改本项中的设置
        "默认配置" : {
            "termServerPort" : 8188,
            "qq" : "",
            "mailAccount" : "",
            "mailAuthCode" : "",
            "debug" : False,
            "restartOnOffline" : False,
        },
    
    }

如果需要使用邮箱模式，可以在配置文件中新增一个用户配置（如 somebody ），在该用户下的 mailAccount 和 mailAuthCode 项中分别设置邮箱帐号和授权码，启动 QQBot 时，输入 qqbot -u somebody ，开始运行后，二维码管理器会将二维码图片发送至该邮箱。

注意：授权码不是邮箱的登录密码，而是邮箱服务商提供的开通 IMAP/SMTP 服务的授权码， QQ 邮箱可以在网页版的邮箱设置里面开通此项服务，并得到授权码。如果只定义了 mailAccount 而没定义 mailAuthCode ，则程序运行的开始时会要求手工输入此授权码。

由于网易的邮箱对 IMAP 协议的支持非常有限，无法在 QQBot 中使用。 QQ 的邮箱已通过测试，其他服务商的邮箱还未测试过，因此建议还是使用 QQ 邮箱。

配置文件中每个用户都有 qq 这一项，如果在某用户（如 somebody ）下设置了此项，则在命令行中输入 qqbot -u somebody 启动后，会先使用此 QQ 号上次登录保存的登录信息来自动登录。

如果配置文件中将 restartOnOffline 项设置为 True ，则当 QQBot 掉线或出错终止时，会自动重新启动 QQBot 。

配置文件中的所有选项都有对应的命令行参数，在命令行参数中输入的选项优先级比配置文件高。输入 qqbot -h 可查看所有命令行参数格式。

七、参考资料
-------------

QQBot 参考了以下开源项目：

- [ScienJus/qqbot](https://github.com/ScienJus/qqbot) （ruby）
- [floatinghotpot/qqbot](https://github.com/floatinghotpot/qqbot) （node.js）
- [sjdy521/Mojo-Webqq](https://github.com/sjdy521/Mojo-Webqq) (perl)

在此感谢以上三位作者的无私分享，特别是感谢 ScienJus 对 SmartQQ 协议所做出的深入细致的分析。

八、反馈
---------

有任何问题或建议可以发邮件给我 <pandolia@yeah.net> 或者直接提 issue 。
