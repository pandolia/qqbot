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

在 Python 2.7/3.4/3.5 下使用，用 pip 安装：

    pip install qqbot

原 2.0 版的用户请先到 [issue74](https://github.com/pandolia/qqbot/issues/74) 查看 2.1 版的升级和改动。

三、使用方法
-------------

##### 1. 启动 QQBot

在命令行输入： **qqbot** 。启动过程中会自动弹出二维码图片，需要用手机 QQ 客户端扫码并授权登录。启动成功后，会将本次登录信息保存到本地文件中，下次启动时，可以输入： **qqbot -q qq号码** ，先尝试从本地文件中恢复登录信息（不需要手动扫码），只有恢复不成功或登录信息已过期时才会需要手动扫码登录。一般来说，保存的登录信息将在 2 天之后过期。

注意： Linux 下，需要系统中有 gvfs-open 或者 shotwell 命令才能自动弹出二维码图片（一般安装有 GNOME 虚拟文件系统 gvfs 的系统中都会含这两个命令之一）。 Windows10 下，需要系统中已设置了 png 图片文件的默认打开程序才能自动弹出二维码图片。

若系统无法自动弹出二维码图片，可以手动打开图片文件进行扫码，也可以将二维码显示模式设置为邮箱模式或服务器模式进行远程扫码，详见本文档的第七节。

##### 2. 操作 QQBot

QQBot 启动后，在另一个控制台窗口使用 qq 命令来操作 QQBot ，目前提供以下命令：

    1） 帮助、停机和重启命令
        qq help|stop|restart

    2） 联系人查询命令
        qq list buddy|group|discuss|group-member|discuss-member [oqq|oname|okey=oval] [qq|name|key=val]

    3） 消息发送命令
        qq send buddy|group|discuss qq|name|key=val message

list 命令提供强大的联系人查询功能，用法示例如下：

    # 列出所有好友
    list buddy

    # 列出 QQ 为 123456 的群
    list group 123456

    # 列出备注名为 jack 的好友
    list buddy mark=jack

    # 列出 群“456班” 的所有成员
    list group-member 456班

    # 列出 群“456班” 中名片为 “mike” 的成员
    list group-member 456班 card=mike

    # 列出 讨论组“XX小组” 中名为 jack 的好友
    list discuss-member XX小组 jack

其中第三、四个参数如果是 key=val 的格式，则应为 name=xx|nick=xx|mark=xx|card=xx|qq=xx|uin=xx 的格式，如果不是 key=val 的格式，则按以下原则进行处理：若是一串数字，则按 QQ 号进行查询，否则，按名称进行查询。

如果存在重名现象，会列出所有重名的联系人。如：

    list group 机器人测试

将列出所有名为 “机器人测试” 的群。

send 命令中第三个参数和 list 命令中的第三、四个参数格式一致。要注意，如果有重名现象，会给所有重名的联系人发信息。 另外要注意，第二个参数只能是 buddy/group/discuss ，不可以为 group-member/discuss-member 。

另外，QQBot 启动后，用另外一个 QQ 向本 QQ 发送 “--version” ，则 QQBot 会自动回复： “QQBot-v2.x.x” 。

四、实现你自己的 QQ 机器人
---------------------------

实现自己的 QQ 机器人非常简单，只需要注册一个自己的消息响应函数。示例代码：

    from qqbot import QQBotSlot as qqbotslot, RunBot
    
    @qqbotslot
    def onQQMessage(bot, contact, member, content):
        if content == '-hello':
            bot.SendTo(contact, '你好，我是QQ机器人')
        elif content == '-stop':
            bot.SendTo(contact, 'QQ机器人已关闭')
            bot.Stop()
    
    RunBot()

注意，上面注册的响应函数的函数名必须为 “onQQMessage” ，函数参数也必须和上面的一致。

将以上代码另存为 sample.py 并运行后，用另外一个 QQ 向本 QQ 发送消息 **“-hello”**，则会自动回复 **“你好，我是 QQ 机器人”**，发送消息 **“-stop”** 则会关闭 QQ 机器人。

QQBot 开始运行后，每收到一条 QQ 消息，会将消息来源、消息内容以及一个 QQBot 对象传递给上面注册的消息响应函数。其中：

    bot     : QQBot 对象，提供 List/SendTo/Stop/Restart 四个接口，详见本文档第五节
    contact : QContact 对象，消息的发送者，具有 ctype/qq/uin/name/nick/mark/card 属性，这些属性都是 str 对象
    member  : QContact 对象，仅当本消息为 群或讨论组 消息时有效，代表实际发消息的成员
    content : str 对象，消息内容

QContact 对象的 ctype 属性可以为 'buddy'/'group'/'discuss'/'group-member'/'discuss-member' ，代表 好友/群/讨论组/群成员/讨论组成员。

可以调用 QQBot 对象的 SendTo 接口向 QContact 对象发送消息，但要注意：**不可以向 群成员/讨论组成员 发送消息** 。

对于不习惯用 decorator 的朋友，也可以采用继承的方式来实现 QQ 机器人，只需要继承 QQBot 并重写 onQQMessage 方法，示例：

    from qqbot import QQBot, RunBot
    
    class MyQQBot(QQBot):
        def onQQMessage(self, contact, member, content):
            if content == '-hello':
                self.SendTo(contact, '你好，我是QQ机器人')
            elif content == '-stop':
                self.SendTo(contact, 'QQ机器人已关闭')
                self.Stop()
    
    RunBot(MyQQBot)

以上代码和前面的示例效果是一样的。

五、 QQBot 对象的接口
-----------------------

QQBot 对象提供 List/SendTo/Stop/Restart 四个公开接口，一般情况下，请勿 调用/存取 此对象的其他 方法/属性 。以下介绍 List/SendTo 接口。

#### （1） bot.List(tinfo, [cinfo]) --> [contact0, contact1, ..., ]

对应上面的 list 命令。返回一个联系人对象（ QContact 对象）列表。

List 接口第一个参数 tinfo 可以为 'buddy'/'group'/'discuss' ，第二个参数是可选的（和 list 命令的第三个参数格式一致）。示例：

    # 返回所有好友的列表：
    >>> bot.List('buddy')

    # 返回名为 “机器人测试” 的群的列表：
    >>> bot.List('group', '机器人测试')

List 接口的第一个参数 tinfo 也可以是一个 ctype 等于 'group'/'discuss' 的 QContact 对象，此时，返回的是该 群/讨论组 的成员列表，如以下第二句和第三句分别返回 群“456班” 的成员列表和该群中名片为 “jack” 的成员列表：

    >>> g = bot.List('group', "456班")[0]
    >>> bot.List(g)
    >>> bot.List(g, 'card=jack')

注意上面第三句不允许是 bot.List(g, card='jack') 的格式。

#### （2） bot.SendTo(contact, content) --> '向 xx 发消息成功'/'错误：...'

向联系人发送消息。第一个参数为 QContact 对象，第二个参数为消息内容。再次提醒： **不允许给 群成员/讨论组成员 发消息** 。


六、 可注册的响应函数
-----------------------------------

除了上面提到的 onQQMessage 响应函数，还可以注册 onNewContact/onLostContact/onInterval 三种事件的响应函数，所有事件以及函数参数格式、含义如下：

    @qqbotslot
    def onQQMessage(bot, contact, member, content):
        # 当收到 QQ 消息时被调用
        # bot     : QQBot 对象，提供 List/SendTo/Stop/Restart 四个接口，详见文档第五节
        # contact : QContact 对象，消息的发送者，具有 ctype/qq/uin/name/nick/mark/card 属性，这些属性都是 str 对象
        # member  : QContact 对象，仅当本消息为 群或讨论组 消息时有效，代表实际发消息的成员
        # content : str 对象，消息内容
        if content == '--version':
            bot.SendTo(contact, 'QQbot-' + bot.conf.version)

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

再次提醒：**注册的响应函数的函数名以及函数参数必须和上面一致，不允许注册其他名称的函数** 。

以上三个响应函数也可以使用继承并重写方式来实现，参见本文档第四节。

**被群内其他成员 @ 的通知**： QQBot 收到群消息时，会先根据消息内容判断是否有人 @ 自己。如果是，则在消息内容的开头加一个 '[@ME] ' 的标记，再传递给 onQQMessage 函数；否则，将消息内容中的所有 '@ME' 替换成 '@Me' 再传给 onQQMessage 。因此，在 onQQMessage 函数内，只需要判断 content 内是否含有 '@ME' 就知道自己是否被消息发送者 @ 了。例如：

    @qqbotslot
    def onQQMessage(bot, contact, member, content):
        if '@ME' in content:
            bot.SendTo(contact, '%s， 又在想我了吧？' % member.name)

七、二维码管理器、QQBot 配置、掉线后自动重启、命令行参数
------------------------------------------------

SmartQQ 登录时需要用手机 QQ 扫描二维码图片，在 QQBot 中，二维码图片可以通过以下三种模式显示：

* GUI模式： 在 GUI 界面中自动弹出二维码图片
* 邮箱模式： 将二维码图片发送到指定的邮箱
* 服务器模式： 在一个 HTTP 服务器中显示二维码图片

GUI 模式是默认的模式，只适用于个人电脑。邮箱模式可以适用于个人电脑和远程服务器。服务器模式一般只在有公网ip的系统中使用。最方便的是使用 QQ 邮箱的邮箱模式，当发送二维码图片后，手机 QQ 客户端一般会立即收到通知，在手机 QQ 客户端上打开邮件，再长按二维码就可以扫描了。

注意：当开启了邮箱模式或服务器模式时， GUI 模式是关闭的，登陆时不会自动弹出二维码图片。

每次登录时会创建一个二维码管理器 （QrcodeManager 对象） ，二维码管理器会根据配置文件及命令行参数来选择二维码图片的显示方式。

配置文件为 **~/.qqbot-tmp/v2.x.conf** ，第一次运行 QQBot 后就会自动创建这个配置文件，其中内容如下：
    
    {
        # QQBot 的配置文件
        
        # 用户 somebody 的配置
        "somebody" : {
            
            # QQBot-term 服务器端口号
            "termServerPort" : 8188,
            
            # http 服务器 ip，请设置为空字符串或公网 ip
            "httpServerIP" : "127.0.0.1",
            
            # http 服务器端口号
            "httpServerPort" : 8189,
            
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
            "httpServerIP" : "",
            "httpServerPort" : 8189,
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

如果需要使用服务器模式，可以配置 httpServerIP 和 httpServerPort 项，一般来说应该设置为公网 ip 。服务器模式开启后，可以通过 http://httpServerIP:httpServerPort/qqbot/qrcode 来访问二维码图片。

当邮箱模式和服务器模式同时开启时，发邮件时不会发送真正的图片，只会将图片地址发到邮箱中去，而且只发送一次，二维码过期时刷新一下邮件就可以了。如果只开启邮箱模式，则发邮件时会发送真正的图片，当二维码过期时，需要手动将邮件删除，删除之后才会发送最新的二维码图片。

配置文件中每个用户都有 qq 这一项，如果在某用户（如 somebody ）下设置了此项，则在命令行中输入 qqbot -u somebody 启动后，会先使用此 QQ 号上次登录保存的登录信息来自动登录。

如果配置文件中将 restartOnOffline 项设置为 True ，则当 QQBot 掉线或出错终止时，会自动重新启动 QQBot 。

配置文件中的所有选项都有对应的命令行参数，在命令行参数中输入的选项优先级比配置文件高。输入 qqbot -h 可查看所有命令行参数格式。

如果配置的 QQBot-term 服务器端口号不是默认的 8188 ，那么在运行 qq 命令时，需要在第一个参数中指定端口号，如：

    $ qq 8100 send buddy jack hello
    $ qq 8100 list group-member chatbot

八、 smartqq 协议支持及限制
-------------------------

#### smartqq 协议支持、本项目已实现的功能
+ 消息收/发
+ 联系人（包括 好友/群/讨论组/群成员/讨论组成员）资料获取和查询（包括 QQ号/昵称/名称/备注名/群名片）
+ 联系人资料动态更新，新增和丢失 好友/群/讨论组/群成员/讨论组成员 事件的通知（滞后约3~5分钟）
+ 被群内其他成员 @ 的通知

#### 其他功能
+ 调用系统默认图片浏览器显示登录二维码、将登录二维码发送至邮箱、开启一个 http 服务器用来显示登录二维码
+ 用 qq 命令行工具发消息和查询联系人
+ 掉线后自动重启功能（有时需要手工扫码）
+ 定时执行任务（通过注册 onInterval 函数实现）

#### 因 smartqq 协议的限制，以下问题无解决办法

+ 无法长时间保持在线状态，每次登录成功后的 cookie 会每在 1 ~ 2 天后失效，将被腾讯服务器强制下线，此时 **必须** 手工扫码重新登录。可以将二维码显示模式设置为邮箱模式并打开自动重启模式，在被下线时自动重启并将二维码发送到邮箱，实现远程扫码
+ 无法发送图片和 xml 卡片消息
+ 无法获取到自己通过其他客户端（手机 QQ 、PC QQ）发送的消息，只能接收到别人发过来的消息
+ 无法在群内 @ 其他成员，即便用本程序在群里发送了 “@jack xxx” 这样的消息， jack 也只能收到这个纯文本，收不到“有人@我”的提醒。
+ 无法向 群/讨论组 内的其他非好友成员发消息，也无法收到非好友成员发过来的临时会话消息
+ 在非常少的情况下，发消息时会重复发送多次，也可能对方已收到消息但返回发送失败的结果

#### smartqq 协议支持、但尚未实现的功能

+ 群成员禁言、踢除群成员等群管理功能
+ 发送表情

九、其他
-------------

- [常见问题](https://github.com/pandolia/qqbot/blob/master/faq.md)
- [更新日志](https://github.com/pandolia/qqbot/blob/master/changes)

十、参考资料
-------------

QQBot 参考了以下开源项目：

- [ScienJus/qqbot](https://github.com/ScienJus/qqbot) (ruby)
- [floatinghotpot/qqbot](https://github.com/floatinghotpot/qqbot) (node.js)
- [sjdy521/Mojo-Webqq](https://github.com/sjdy521/Mojo-Webqq) (perl)

在此感谢以上三位作者的无私分享，特别是感谢 ScienJus 对 SmartQQ 协议所做出的深入细致的分析。

十一、反馈
---------

有任何问题或建议可以发邮件给我 <pandolia@yeah.net> ，或者直接提 issue 。
