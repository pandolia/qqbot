一、介绍
---------

qqbot 是一个用 python 实现的、基于腾讯 SmartQQ 协议的 QQ 机器人，可运行在 Linux, Windows 和 Mac OSX 平台下。

本项目 github 地址： <https://github.com/pandolia/qqbot>

你可以通过扩展 qqbot 来实现：

* 监控、收集 QQ 消息
* 自动消息推送
* 聊天机器人
* 通过 QQ 远程控制你的设备

二、安装方法
-------------

在 Python 2.7/3.4+ 下使用，用 pip 安装：

    pip install qqbot

或者下载 [源码](https://github.com/pandolia/qqbot/archive/master.zip) 解压后 cd 到该目录并运行： `pip install`.

三、使用方法
-------------

##### 1. 启动 QQBot

在命令行输入： **qqbot** ，即可启动一个 QQBot 。

启动过程中会自动弹出二维码图片，需要用手机 QQ 客户端扫码并授权登录。启动成功后，会将本次登录信息保存到本地文件中，下次启动时，可以输入： **qqbot -q qq号码** ，先尝试从本地文件中恢复登录信息（不需要手动扫码），只有恢复不成功或登录信息已过期时才会需要手动扫码登录。一般来说，保存的登录信息将在 2 天之后过期。

注意： Linux 下，需要系统中有 gvfs-open 或者 shotwell 命令才能自动弹出二维码图片（一般安装有 GNOME 虚拟文件系统 gvfs 的系统中都会含这两个命令之一）。 Windows10 下，需要系统中已设置了 png 图片文件的默认打开程序才能自动弹出二维码图片。

若系统无法自动弹出二维码图片，可以手动打开图片文件进行扫码，也可以将二维码显示模式设置为 邮箱模式 、 服务器模式 或 文本模式 进行扫码，详见本文档的第七节。

##### 2. 操作 QQBot

QQBot 启动后，在另一个控制台窗口使用 qq 命令操作 QQBot ，目前提供以下命令：

    1） 帮助、停机和重启命令

        qq help|stop|restart|fresh-restart


    2） 联系人查询、搜索命令

        qq list buddy|group|discuss [$cinfo|$clike]
        ( $cinfo --> $qq|$name|$key=$val )
        ( $clike --> :like:$qq|:like:$name|$key:like:$name )

        qq list group-member|discuss-member $oinfo|$olike [$cinfo|$clike]
        ( $oinfo --> $oqq|$oname|$okey=$oval )
        ( $cinfo --> $qq|$name|$key=$val )
        ( $olike --> :like:$oqq|:like:$oname|$okey:like:$oname )
        ( $clike --> :like:$qq|:like:$name|$key:like:$name )


    3） 联系人更新命令

        qq update buddy|group|discuss

        qq update group-member|discuss-member $ginfo


    4） 消息发送命令

        qq send buddy|group|discuss $rinfo $message


    5） 群管理命令： 设置/取消管理员 、 设置/删除群名片 、 群成员禁言 以及 踢除群成员

        qq group-set-admin $ginfo $minfo1,$minfo2,...

        qq group-unset-admin $ginfo $minfo1,$minfo2,...

        qq group-set-card $ginfo $minfo1,$minfo2,... card

        qq group-unset-card $ginfo $minfo1,$minfo2,...

        qq group-shut $ginfo $minfo1,$minfo2,... [t]

        qq group-kick $ginfo $minfo1,$minfo2,...


    6） 加载/卸载/显示插件

        qq plug/unplug myplugin

        qq plugins


list 命令提供强大的联系人查询和搜索功能，用法示例如下：

    # 列出所有好友
    qq list buddy

    # 列出 QQ 为 123456 的群
    qq list group 123456

    # 列出备注名为 jack 的好友
    qq list buddy mark=jack

    # 列出 群“456班” 的所有成员
    qq list group-member 456班

    # 列出 群“456班” 中名片为 “mike” 的成员
    qq list group-member 456班 card=mike

    # 列出 讨论组“XX小组” 中名为 jack 的好友
    qq list discuss-member XX小组 jack

其中第三、四个参数如果是 key=val 的格式，则应为 name=xx|nick=xx|mark=xx|card=xx|qq=xx 的格式，如果不是 key=val 的格式，则按以下原则进行处理：若是一串数字，则按 QQ 号进行查询，否则，按名称进行查询。

如果存在重名现象，会列出所有重名的联系人。如：

    qq list group 机器人测试

将列出所有名为 “机器人测试” 的群。

如果在 list 命令的第三、四个参数中加入 “:like:” ，则会按部分匹配的模式进行搜索，用法示例如下：

    # 列出名称中含有 “李” 的好友
    qq list buddy :like:李

    # 列出 QQ 中含有 “234” 的群
    qq list group :like:234

    # 列出备注名中含有 jack 的好友
    qq list buddy mark:like:jack

    # 列出 群“456班” 的中名称中含有 “李” 的成员
    qq list group-member 456班 :like:李

    # 列出 群“456班” 中名片中含有 “mike” 的成员
    qq list group-member 456班 card:like:mike

    # 列出的 讨论组“xx小组” 中名为 jack 的好友
    qq list discuss-member :like:小组 jack

从 v2.2.5 版开始， list 命令采用表格的形式输出联系人列表，其输出样式示例如下：

![prettytable.png](https://raw.githubusercontent.com/pandolia/qqbot/master/prettytable.png)

为保证表格在终端中的显示效果，建议将终端的输出字体设置为 consolas 、且每行可打印的最大字符数大于 120 。另外需要注意：为保证表格的显示效果，当联系人的名称、名片等属性的长度太长或含有特殊字符时，将对这些属性进行截断或过滤后再输出至终端。

update 命令更新指定的联系人列表，其参数含义和 list 命令相同，如：

    # 更新好友列表
    qq update buddy

    # 更新群列表
    qq update group

    # 更新 群“456班” 的成员列表
    qq update group-member 456班

send 命令中第三个参数和 list 命令中的第三个参数格式一致。要注意，如果有重名现象，会给所有重名的联系人发信息。 另外要注意，第二个参数只能是 buddy/group/discuss ，不能是 group-member/discuss-member 。示例：

    # 给 好友“jack” 发消息 “你好”
    qq send buddy jack 你好

    # 给 群“198班” 发消息 “大家好”
    qq send group 198班 大家好

    # 给 QQ 为 12345 的好友发消息
    qq send buddy 12345 xxx

    # 给讨论组发消息
    qq send discuss MyDiscuss hello

可以在消息内容中嵌入“/可爱”等表情关键词来向对方发送表情，详见 [facemap.py](https://github.com/pandolia/qqbot/blob/master/qqbot/facemap.py)。还可以在消息内容中使用 **\n,\t** 这两个转义字符（如： send buddy jack 第一行\n第二行）。

群管理命令中的 $ginfo 和 $minfo 和 list 命令中的第三、四个参数格式一致。例如：

    # 禁止 群“456班” 中的 jack,mike,jim 发言（ 2 分钟）
    qq group-shut 456班 jack,mike,jm 120

以上所有命令都提供对应的 HTTP API 接口，供 web 前端开发者调用，接口的 url 地址为 http://127.0.0.1:8188/{command} ，只需要将 qq 后面的命令各参数用 "/" 分隔开替换 url 中的 command 就可以了，如: http://127.0.0.1:8188/send/buddy/jack/hello ，其他示例详见 [urltestbot.md](https://github.com/pandolia/qqbot/blob/master/urltestbot.html) 。注意：如果命令中含有中文或特殊字符，需要先进行 url 编码（ utf8 ），例如，调用  http://127.0.0.1:8188/send/buddy/jack/nihao%20%E4%BD%A0%E5%A5%BD%20wohao 将发送消息 ”nihao 你好 wohao“ 。（提示：在 JavaScript 中，可以使用 encodeURIComponent 函数进行编码）。

另外， QQBot 启动后，用本 QQ 号在其他客户端（如：手机 QQ ）上向某个 群/讨论组 发消息 “--version” ，则 QQBot 会自动在该 群/讨论组 回复： “QQBot-v2.x.x” 。

四、实现你自己的 QQ 机器人
---------------------------

实现自己的 QQ 机器人非常简单，只需要定义一个自己的消息响应函数并按插件加载。示例代码：
```python
# -*- coding: utf-8 -*-

def onQQMessage(bot, contact, member, content):
    if content == '-hello':
        bot.SendTo(contact, '你好，我是QQ机器人')
    elif content == '-stop':
        bot.SendTo(contact, 'QQ机器人已关闭')
        bot.Stop()
```

注意，上面注册的响应函数的函数名必须为 “onQQMessage” ，函数参数也必须和上面的一致。

将以上代码另存为 sample.py （注意保存为 utf8 编码的文件）。放到 \~/.qqbot-tmp/plugins/ 目录下（ **\~** 代表用户主目录， win7 下为 C:\\Users\\xxx ），或系统中可以 import 到的目录下（如 python 的安装目录下的 Lib/site-packages 目录）。

之后，保持前面的 qqbot 进程运行，在另一个控制台输入 qq plug sample ，则可将此文件中的 onQQMessage 函数注册到 QQBot 的相应事件上去。此时，用另外一个 QQ 向本 QQ 发送消息 **“-hello”**，则会自动回复 **“你好，我是 QQ 机器人”**，发送消息 **“-stop”** 则会关闭 QQ 机器人。

在控制台输入 qq unplug sample 可以卸载此插件及相应的回调函数。可以同时加载多个插件，此时各插件中的相应函数会依次被调用（但调用顺序和加载次序无关）。

QQBot 开始运行后，每收到一条 QQ 消息，会将消息来源、消息内容以及一个 QQBot 对象传递给已注册的消息响应函数。其中：

    bot     : QQBot 对象，提供 List/SendTo/Stop/Restart 等接口，详见本文档第五节
    contact : QContact 对象，消息的发送者，具有 ctype/qq/uin/nick/mark/card/name 等属性
    member  : QContact 对象，仅当本消息为 群消息或讨论组消息 时有效，代表实际发消息的成员
    content : str 对象，消息内容

contact 代表消息发送者，其 ctype 属性可以为 `buddy`/`group`/`discuss` ，代表 好友/群/讨论组 对象，表示本消息是 好友消息/群消息/讨论组消息 。

member 仅当本消息为  群消息或讨论组消息 时有效，代表实际发消息的成员，它的 ctype 属性可以为 `group-member`/`discuss-member` ，代表 群成员/讨论组成员 对象。当本消息为 好友消息 时， member 等于 None 。

contact 和 member 都是 QContact 对象，不同类型的 QContact 对象所具有的属性含义见： [qcontact-attr](https://github.com/pandolia/qqbot/blob/master/qcontact-attr.md) 。注意所有 QContact 对象都是 **只读对象** ，只能读取它的属性，不能设置它的属性，也不能向它添加额外的属性。 

可以调用 QQBot 对象的 SendTo 接口向 QContact 对象发送消息，但要注意：只可以向 好友/群/讨论组 发消息， **不可以向 群成员/讨论组成员 发送消息** 。也就是说，只可以调用 bot.SendTo(contact, 'xxx') ， 不可以调用 bot.SendTo(member, 'xxx') 。

五、 QQBot 对象的公开接口和属性
--------------------------------

QQBot 对象提供 List/Update/SendTo/GroupSetAdmin/GroupSetCard/GroupShut/GroupKick/Plug/Unplug/Login/Stop/Restart/FreshRestart 共计 11 个公开接口，这些接口的第一个字母都是大写的。另外，提供一个公开属性 conf 保存全局的配置信息。

一般情况下，请勿 调用/存取 此对象的其他 方法/属性 。特别的， **请勿在子线程中调用这些接口** 。 以下介绍前 7 个接口和 conf 属性。

如果需要在 IDE 或 python-shell 中运行或测试以上接口，需要先关闭 qqbot 进程，并在 IDE 或 python-shell 中运行以下代码进行登录：

    >>> from qqbot import _bot as bot
    >>> bot.Login(['-q', '1234'])

#### （1） bot.List(tinfo, [cinfo]) --> [contact0, contact1, ..., ]/[]/None

对应本文档第三节的 list 命令。返回联系人对象（ QContact 对象）列表或者 None 。第一个参数 tinfo 是联系人列表的代号，第二个参数是可选的（和 list 命令的第三个参数格式一致）。

参数 tinfo 用来代表某个联系人列表，**该参数在联系人的查询中非常重要，请务必理解以下两种情况** ：

**tinfo 的含义（情况1）：** tinfo 可以为 `buddy`/`group`/`discuss` ，分别代表 好友列表/群列表/讨论组列表 。示例：

    # 返回 好友列表：
    >>> bot.List('buddy')

    # 返回名为 'jack' 的好友的列表：
    >>> bot.List('buddy', 'jack')

    # 返回 群列表：
    >>> bot.List('group')

    # 返回名为 “机器人测试” 的群的列表：
    >>> bot.List('group', '机器人测试')

**tinfo 的含义（情况2）：** tinfo 也可以是一个 ctype 等于 `group`/`discuss` 的 QContact 对象，代表该 群/讨论组 的成员列表。如以下第二句和第三句分别返回 群“456班” 的成员列表和该群中名片为 “jack” 的成员列表：

    >>> g = bot.List('group', "456班")[0]   # g 是一个 Group 对象（群“456班”）
    >>> bot.List(g)                         # 返回 群“456班” 的成员列表
    >>> bot.List(g, 'card=jack')            # 返回 群“456班” 中名片为 “jack” 的成员列表

注意上面第三句不允许是 bot.List(g, card='jack') 的格式。

**List 接口的内部执行顺序：** 首先在 QQBot 的联系人数据库内查找 tinfo 所代表的联系人列表；若数据库内已有此列表，则在此列表内进行搜索，并返回一个包含 “此列表中所有和 cinfo 匹配的联系人” 的列表；若数据库内没有此列表，则向 QQ 服务器请求数据获取联系人列表，获取成功后将联系人列表保存到数据库内，然后再进行搜索并返回一个包含 “此列表中所有和 cinfo 匹配的联系人” 的列表；如果在向 QQ 服务器请求数据的过程中出错了，则打印相关的失败信息，并返回 None 。

**List 接口返回值的含义：** 返回一个非空列表表示 tinfo 所指定的联系人列表内所有和 cinfo 匹配的联系人；返回一个空列表表示该联系人列表内没有和 cinfo 匹配的联系人；返回 None 表示向 QQ 服务器请求联系人列表和资料失败，不知道是否有相匹配的联系人。

调用 List 接口后， **务必** 先根据以上三种情况对返回值进行判断，然后再执行后续代码。

**注意： 当 List 接口返回非空列表时，列表内的元素是 QContact 对象，而不是 str 对象：**

    >>> g = bot.List('group')[0]   				# g 是一个 Group 对象
    >>> print([g, type(g), g.qq, g.name, g.uin, g.mark])	# 打印 g 的各项属性

不同类型的 QContact 对象所具有的属性含义见： [qcontact-attr](https://github.com/pandolia/qqbot/blob/master/qcontact-attr.md) 。 

#### （2） bot.Update(tinfo) --> True/False

Update 接口的参数 tinfo 和 List 接口中的参数含义相同，调用此接口会立即向 QQ 服务器请求相应的联系人列表并更新联系人数据库，并一直阻塞至更新成功。更新最慢的是好友列表，若好友较多可能会阻塞 5 ~ 10 秒。成员列表更新的较快，即便是 2000 人的大群，更新时间仅 1 ~ 2 秒。

若更新成功，返回 True ，否则，返回 False 。

示例：

    # 更新 好友列表 ：
    >>> bot.Update('buddy')

    # 更新 群列表 ：
    >>> bot.Update('group')

    # 更新 某个群的成员列表 ：
    >>> gl = bot.List('group', "456班")
    >>> if gl:
    >>>     g = gl[0]
    >>>     bot.Update(g)

#### （3） bot.SendTo(contact, content, resendOn1202=True) --> '向 xx 发消息成功'/'错误：...'

向联系人发送消息。第一个参数为 QContact 对象，第二个参数为消息内容。再次提醒： 只可以向 好友/群/讨论组 发消息， **不允许向 群成员/讨论组成员 发消息** 。

可以在消息内容中嵌入“/微笑”等表情关键词来向对方发送表情，详见 [facemap.py](https://github.com/pandolia/qqbot/blob/master/qqbot/facemap.py) 。

若发送成功，返回字符串（`向 xx 发消息成功`）。否则，返回含错误原因的字符串（`错误：...`）。

发消息时可能会重复发消息，这是因为 QQ 服务器返回代码 1202 的原因。v2.1.17版已针对此问题在 bot.SendTo 接口中增加了一个参数： resendOn1202 ，若此参数为 True （默认值），则发消息时如果 QQ 服务器返回代码 1202 （表明发消息可能失败），还会继续发送 3 次，直至返回代码 0 ， 若此参数为 False ，则不会尝试重发。

设为 True 在绝大部分情况下能保证消息一定能发出去，但缺点是有时一条消息会重复发送。设为 False 则相反，消息不会重复发送，但有时消息发送不出去。

总之因为这个 1202 代码的不确定性，没有完美的解决办法。请根据各自的实际情况选择 resendOn1202 的值。

第一个参数 contact 必须是通过 bot.List 返回的 QContact 对象、或回调函数 onQQMessage 传递进来的第一个参数。示例：

    # 向 QQ 为 12345 的好友发消息
    >>> bl = bot.List('buddy', '12345')
    >>> if bl:
    >>>     b = bl[0]
    >>>     bot.SendTo(b, 'hello')

#### （4） bot.GroupXXX(group, membs[, arg]) --> ['成功：...', '成功：...', '错误：...']

对应第三节的群管理命令，共四个接口：

- 设置/取消管理员： bot.GroupSetAdmin(group, membs, admin=True)
- 设置/取消群成员名片： bot.GroupSetCard(group, membs, card)
- 禁止群成员发言： bot.GroupShut(group, membs, t=60)
- 踢除群成员： bot.GroupKick(group, membs)

其中第一个参数 group 为 群对象（ ctype 等于 `group` 的 QContact 对象），第二个参数 membs 为被操作的成员列表。返回值为 membs 中各成员的操作信息。示例代码：

    # 禁止 群“456班” 中名称为 jack 的成员发言（120秒）
    gl = bot.List('group', '456班')
    if gl:
        group = gl[0]
        membs = bot.List(group, 'jack')
        if membs:
            bot.GroupShut(group, membs, 120)

注意： 1） 第二个参数 membs 是一个 list 对象（如： [memb0,memb1,...] ），而不是一个 QContact 对象； 2） 若 membs 中的某个成员是管理员，则除 SetCard 外的其他接口可能对其无效，尽管此时返回成功信息。 3） 使用这四个接口时，请自行保证登录的用户是该群的管理员，且 membs 中的各成员均属于该群。
 
#### （5） bot.conf

bot.conf 中保存全局的配置信息，各项配置详见本文档第七节。如 bot.conf.termServerPort 保存 QQBot 命令行服务器的端口号， bot.conf.qq 保存本次登录的 QQ 号码。

注意： bot.conf 中保存的配置信息是只读的，请勿修改这些配置信息。


六、 注册回调函数、被他人 @ 的通知、判断是否是自己发的消息、定制定时任务
-------------------------------------------------------------

#### 注册回调函数

除了上面提到的 onQQMessage 响应函数，还可以注册 onInit/onQrcode/onStartupComplete/onInterval/onUpdate/onPlug/onUnplug/onExit 共计九种事件的回调函数，所有事件的回调函数参数格式、含义及示例详见 [sampleslots.py](https://github.com/pandolia/qqbot/blob/master/qqbot/plugins/sampleslots.py) 。

程序的运行流程以及各回调函数的调用时机如下：

![main.png](https://github.com/pandolia/qqbot/raw/master/doc-data/main.png)

再次提醒：**注册的回调函数的函数名以及函数参数（数量和名称）都不得更改** 。

#### 被群内其他成员 @ 的通知

 QQBot 收到群消息时，会先根据消息内容判断是否有人 @ 自己。如果是，则在消息内容的开头加一个 `[@ME] ` 的标记，再传递给 onQQMessage 函数；否则，将消息内容中的所有 `@ME` 替换成 `@Me` 再传给 onQQMessage 。因此，在 onQQMessage 函数内，只需要判断 content 内是否含有 `@ME` 就知道自己是否被消息发送者 @ 了。例如：

```python
def onQQMessage(bot, contact, member, content):
    if '@ME' in content:
        bot.SendTo(contact, member.name+'，艾特我干嘛呢？')
```

请注意，若群内有另一个成员的名字和自己的名字的开头部分相同（如：自己的名字是 ab ，另一个成员的名字是 abc ），那么当有人 @abc 时，也会误报成 @ME ，在这种情况下，需要修改自己的群名片，以免误报。

#### 判断是否是自己发的消息

当本 QQ 发消息时， QQBot 也会收到一条同样的消息， bot 对象提供一个 isMe 方法来判断是否是自己发的消息：

```python
def onQQMessage(bot, contact, member, content):
    if bot.isMe(contact, member):
    print('This is me')
```

#### 定制定时任务

从 2.1.13 起， qqbot 提供一个功能强大的函数装饰器 -- `qqbotsched` 来定制定时任务，示例代码：


```python
from qqbot import qqbotsched

@qqbotsched(hour='11,17', minute='55')
def mytask(bot):
    gl = bot.List('group', '456班')
    if gl is not None:
        for group in gl:
            bot.SendTo(group, '同志们：开饭啦啦啦啦啦啦！！！')
```
以上代码以插件形式加载后，每到 11:55 和 17:55 ，都会自动向 群“456班” 发送消息：“同志们：开饭啦啦啦啦啦啦！！！” 。

qqbotsched 装饰器接受 year, month, day, week, day_of_week, hour, minute, second, start_date, end_date, timezone 共计 11 个关键字参数，每个参数表示任务的定制时间的分量所应匹配的值。例如： hour='11,17' 表示应在 11:xx 或 17:xx 执行任务， minute='55' 表示应在 xx:55 执行任务， minute='0-55/5' 表示应在 xx:00, xx:05, xx:10, ..., xx:55 执行任务， day_of_week='mon-fri' （或 '0-4' ） 表示应在 星期一 ~ 星期五 执行任务。

qqbotsched 是对 Python 的定时任务框架 apscheduler 的简单封装，其各项参数应采用 Unix 系统中的 crontab 格式输入。有关 crontab 以及 Python 的定时任务框架 apscheduler 的内容可参见以下参考资料：

- https://code.tutsplus.com/tutorials/scheduling-tasks-with-cron-jobs--net-8800/
- http://apscheduler.readthedocs.io/en/latest/userguide.html
- [https://lz5z.com/Python定时任务的实现方式/](https://lz5z.com/Python%E5%AE%9A%E6%97%B6%E4%BB%BB%E5%8A%A1%E7%9A%84%E5%AE%9E%E7%8E%B0%E6%96%B9%E5%BC%8F/)
- http://debugo.com/apscheduler/

crontab 各项参数格式说明详见：

- http://apscheduler.readthedocs.io/en/latest/modules/triggers/cron.html

#### 注册回调函数和定制定时任务的注意事项

注册回调函数和定制定时任务是对 QQBot 进行扩展的唯一方式，在编写这些函数时，请注意以下事项：

- 回调函数的函数名、参数名、参数数量、参数顺序都不得更改
- 定时任务的函数名可以自己定义，但参数有且只有一个，参数名必须为 bot ，为一个 QQBot 对象。
- 所有回调函数和定时任务都将在主线程中被依次调用，因此不必担心全局变量的线程安全问题。
- 回调函数和定时任务的运行时间应尽量短，尽量不要再这些函数中进行阻塞式的操作，否则会阻塞整个程序的运行。一般来说，每个函数的运行时间在 5 秒以内是可以接受的。
- **绝对不要** 在回调函数、定时任务或 qqbot 主线程的内部调用 os.system 执行 **本 QQ 号对应的 qq 命令** （ 如 os.system('qq send buddy jack hello') ）或请求 **本 QQ 号对应的 HTTP-API 接口** ，否则整个程序会形成死锁（因为 os.system 要等 qq 命令执行完成后才返回、而 qq 命令要等 os.system 返回后才会被执行）。请直接使用 bot 的 SendTo/List/GroupXXX 等接口。

七、二维码管理器、QQBot 配置、命令行参数以及工作目录
--------------------------------------------

#### 二维码的显示模式

WebQQ 登录时需要用手机 QQ 扫描二维码图片，在 QQBot 中，二维码图片可以通过以下四种模式显示：

* GUI模式： 在 GUI 界面中自动弹出二维码图片
* 邮箱模式： 将二维码图片发送到指定的邮箱
* 服务器模式： 在一个 HTTP 服务器中显示二维码图片
* 文本模式： 在 Term 中以文本形式展示二维码(需要自行安装 pillow 和 wcwidth 库)

GUI 模式是默认的模式，只适用于个人电脑。邮箱模式可以适用于个人电脑和远程服务器。服务器模式一般只在有公网 ip 的系统中使用。如果使用 QQ 邮箱来接收二维码，则发送二维码图片之后，手机 QQ 客户端会立即收到通知，在手机 QQ 客户端上打开邮件，再长按二维码就可以扫描了。文本模式方便在开发过程或者服务器部署时使用，为开发者提供快捷方式登陆 QQ 。

注意：当开启了 邮箱模式/服务器模式/文本模式 时， GUI 模式是关闭的，登陆时不会自动弹出二维码图片。

每次登录时会创建一个二维码管理器 （ QrcodeManager 对象） ，二维码管理器会根据配置文件及命令行参数来选择二维码图片的显示方式。

#### 配置文件的使用方法

配置文件为 **~/.qqbot-tmp/v2.x.conf** （ **\~** 代表用户主目录， win7 下为 C:\\Users\\xxx ， linux 下为 /home/xxx ），第一次运行 QQBot 后就会自动创建这个配置文件，其中内容如下：
    
    {
    
        # QQBot 的配置文件
        # 使用 qqbot -u somebody 启动程序时，依次加载：
        #     根配置 -> 默认配置 -> 用户 somebody 的配置 -> 命令行参数配置
        # 使用 qqbot 启动程序时，依次加载：
        #     根配置 -> 默认配置 -> 命令行参数配置
        
        # 用户 somebody 的配置
        "somebody" : {
            
            # QQBot-term （HTTP-API） 服务器端口号（该服务器监听 IP 为 127.0.0.1 ）
            # 设置为 0 则不会开启本服务器（此时 qq 命令和 HTTP-API 接口都无法使用）。
            "termServerPort" : 8188,
            
            # 二维码 http 服务器 ip，请设置为公网 ip 或空字符串
            "httpServerIP" : "",
            
            # 二维码 http 服务器端口号
            "httpServerPort" : 8189,
            
            # 自动登录的 QQ 号
            "qq" : "3497303033",
            
            # 接收二维码图片的邮箱账号
            "mailAccount" : "3497303033@qq.com",
            
            # 该邮箱的 IMAP/SMTP 服务授权码
            "mailAuthCode" : "feregfgftrasdsew",
            
            # 是否以文本模式显示二维码
            "cmdQrcode" : False,
        
            # 显示/关闭调试信息
            "debug" : False,
    
            # QQBot 掉线后自动重启
            "restartOnOffline" : False,
            
            # 在后台运行 qqbot ( daemon 模式)
            "daemon": False,
            
            # 完成全部联系人列表获取之后才启动 QQBot 
            "startAfterFetch" : False,
            
            # 插件目录
            "pluginPath" : ".",
            
            # 启动时需加载的插件
            "plugins" : [],
            
            # 插件的配置（由用户自定义）
            "pluginsConf" : {},
        
        },
        
        # 可以在 默认配置 中配置所有用户都通用的设置
        "默认配置" : {
            "qq" : "",
            "pluginPath" : "",
            "plugins" : [
                'qqbot.plugins.sampleslots',
                'qqbot.plugins.schedrestart',
            ],
            "pluginsConf" : {
                'qqbot.plugins.schedrestart': '8:00',
            }
        },
        
        # # 注意：根配置是固定的，用户无法修改（在本文件中修改根配置不会生效）
        # "根配置" : {
        #     "termServerPort" : 8188,
        #     "httpServerIP" : "",
        #     "httpServerPort" : 8189,
        #     "qq" : "",
        #     "mailAccount" : "",
        #     "mailAuthCode" : "",
        #     "cmdQrcode" : False,
        #     "debug" : False,
        #     "restartOnOffline" : False,
        #     "daemon" : False,
        #     "startAfterFetch" : False,
        #     "pluginPath" : "",
        #     "plugins" : [],
        #     "pluginsConf" : {}
        # },
    
    }

可以在配置文件中添加自己的用户配置（即在该文件的字典中新增一个 item ，此 item 的 key 就代表一个用户），例如，该文件中已有的 somebody 项目就代表名为 somebody 的用户，运行 QQBot 时，输入 **qqbot -u somebody** ，则会加载 somebody 项目下的各项配置。

下面介绍配置文件中各项配置的功能，以下内容均假定已修改了 somebody 下的配置，且以 **qqbot -u somebody** 的方式运行。

#### 邮箱模式的配置（ mailAccount 和 mailAuthCode ）

如果需要使用邮箱模式显示二维码，可以将 mailAccount 和 mailAuthCode 项中分别设置为邮箱帐号和授权码，运行后，二维码管理器会将二维码图片发送至该邮箱。

注意：授权码不是邮箱的登录密码，而是邮箱服务商提供的开通 **IMAP/SMTP** 服务的授权码（提醒：不是 **POP3/SMTP** 服务）， QQ/网易 邮箱可以在网页版的邮箱设置里面开通此项服务，并得到授权码。如果只定义了 mailAccount 而没定义 mailAuthCode ，则程序运行的开始时会要求手工输入此授权码。

邮箱模式已在 QQ 、 网易 和 Google 邮箱中测试过。

#### 服务器模式的配置（ httpServerIP 和 httpServerPort ）

如果需要使用服务器模式，可以配置 httpServerIP 和 httpServerPort 项，一般来说应该设置为公网 ip 。服务器模式开启后，可以通过 http://{httpServerIP}:{httpServerPort}/{any} 来访问二维码图片。其中 {any} 可以是任何非空的数字或字母串。

当邮箱模式和服务器模式同时开启时，发邮件时不会发送真正的图片，只会将图片地址发到邮箱中去，而且只发送一次，二维码过期时刷新一下邮件就可以了。如果只开启邮箱模式，则发邮件时会发送真正的图片，当二维码过期时，需要将邮件设置为已读（用手机 QQ 点开邮件后该邮件就是已读了），之后才会发送最新的二维码图片。

#### 文本模式显示二维码（cmdQrcode）

若 cmdQrcode 项设置为 True ，则会在 term 中以文本模式显示二维码。注意：要使用文本模式，需要自行安装 pillow 和 wcwidth 库，可使用 pip 安装。

#### 自动登录的 QQ 号码（ qq ）

配置文件中每个用户都有 qq 这一项，若此项已设置为某 QQ 号码，则 QQBot 在启动时会先使用此 QQ 号上次登录保存的登录信息来自动登录。

#### 掉线后自动重启（ restartOnOffline ）

如果配置文件中将 restartOnOffline 项设置为 True ，则当 QQBot 掉线或出错终止时，会自动重新启动 QQBot 。

#### 在后台运行 qqbot （ daemon ）

此选项仅在 UNIX 类系统中有效，将配置中的 daemon 选项设置为 True 则会以 daemon 模式运行程序。此时，标准输出和标准错误会重定向到 daemon-$qq.log 文件（其中 $qq 是配置中 qq 选项的值）。

#### 联系人列表获取完成后再启动（ startAfterFetch ）

一般情况下，扫码登录完成就立即启动 QQBot，只有在需要的时候才会去获取联系人列表并更新联系人数据库。如果将配置文件中的 startAfterFetch 设置为 True ，则 **QQBot 会等待所有联系人列表获取完成后才启动** ，注意，如果联系人较多，会耗费较长的时间。

#### QQBot-term 服务器端口号（ termServerPort ）

QQBot 启动后，会开启一个 QQBot-term 服务器监听用户通过 qq 命令行工具发过来的操作命令以及通过 HTTP API 接口发过来的操作命令，此服务器的监听 IP 永远为 127.0.0.1 ，监听端口号默认为 8188 ，可以通过修改 termServerPort 的值来修改此端口号。

如果配置的 QQBot-term 服务器端口号不是默认的 8188 ，那么在运行 qq 命令时，需要在第一个参数中指定端口号，如：

    $ qq 8100 send buddy jack hello
    $ qq 8100 list group-member chatbot

同样，HTTP API 接口的端口号也需要改变，如： http://127.0.0.1:8100/send/buddy/jack/hello 。

如果不需要使用 qq 命令和 HTTP-API 接口，可以将此端口号设置为 0 ，此时 QQBot-term 服务器不会开启。

如果需要在同一台机器上登录多个 QQ 号码，可以直接在不同的终端中开启多个 qqbot 进程进行登录，但是，每个 qqbot 进程必须设置专有的 termServerPort 和 httpServerPort （或者全部设置为 0 或 空值 ），否则会造成端口号冲突。

#### 调试模式（ debug ）

若 debug 项设置为 True ，则运行过程中会打印调试信息。

#### 插件的配置（ pluginPath 和 plugins ）

一般情况下，插件需要存放在系统的 import 目录下或 \~/.qqbot-tmp/plugins 目录下，可以在 pluginPath 选项中配置其他的存放目录。另外，在 plugins 选项中可以指定 QQBot 启动时需要加载的插件。

#### 命令行参数及配置的优先级

配置文件中的所有选项都有对应的命令行参数，在命令行参数中输入的选项优先级比配置文件高。输入 **qqbot -h** 可查看所有命令行参数格式。

程序一共有四个级别的配置，其优先级如下：

    使用 qqbot -u somebody 启动程序时，依次加载：
        根配置 -> 默认配置 -> 用户 somebody 的配置 -> 命令行参数配置

    使用 qqbot 启动程序时，依次加载：
        根配置 -> 默认配置 -> 命令行参数配置

其中：根配置 是固定的，用户无法修改； 默认配置 和 用户配置 可由用户在 v2.x.conf 文件中进行修改；最后，还可以在 命令行参数 中输入配置。

#### 工作目录

qqbot 运行时，会在 工作目录 下 搜索/创建 以下 文件/目录 ：

+ 配置文件： v2.x.conf
+ 插件目录： plugins/
+ 登录文件： v2.x-pyx-xxxx.pickle
+ 联系人数据库文件： 2017-05-06-20-03-12-xxxx-contact.db
+ 临时二维码图片： xxxx.png
+ 保存QQ的文件： qq(pid9816)
+ 以 daemon 模式运行时的 log 文件： daemon-xxx.log

默认的工作目录为 \~/.qqbot-tmp/ ，可以在启动 qqbot 时通过命令行参数 -b|--bench 指定其他工作目录，例如： qqbot -b bench 。

八、 插件
-------------------------

#### 插件的存放位置

插件实际上是一个 python 模块，因此可以是一个 python 文件，也可以是一个 python package。 qqbot 会根据插件名在以下目录中搜索插件：

+ 配置中的 pluginPath 选项（命令行参数 -pp|--pluginPath ）指定的目录
+ 工作目录下的 plugins 目录
+ python 的导入目录

#### 插件的加载/卸载

**hot-plug 方式**

可以在 qqbot 的运行过程中动态的加载/卸载插件，有以下三种方法：

+ 利用 qq 命令行工具： qq plug pluginname 或 qq unplug pluginname
+ 利用 http-api 接口： http://127.0.0.1:8188/plug/pluginname 或 http://127.0.0.1:8188/unplug/pluginname
+ 利用 bot 对象的接口： bot.Plug('pluginname') 或 bot.Unplug('pluginname')

前面两种方法是供 qqbot 进程的外部进程调用的，第三种方法是在 qqbot 进程内部使用的。请勿在 qqbot 进程的内部使用前面两种方法。

注意：采用 hot-plug 方式加载的插件在 qqbot 重启后会丢失。

**auto-plug-at-start 方式**

也可以在 qqbot 的启动时自动加载插件，在配置中的 plugins 选项（命令行参数 -pl|--plugins ）中指定需要加载的插件名就可以了。这些插件将在启动时、登录之前被加载。

另外，如果系统中（或插件目录中）存在名为 **qqbotdefault** 的 package ，那么该 package 下面的所有子模块都会被当成插件在启动时自动加载（注意：qqbotdefault 本身不会作为插件加载）。

#### 插件内的 onPlug 和 onUnplug 回调函数

+ 插件被加载时，会执行 reload(pluginName) ，因此插件内的所有代码都会被执行一次
+ 当采用 hot-plug 的方式加载时，插件内的 onPlug 函数会紧接在 reload 成功后被执行
+ 当采用 auto-plug-at-start 方式加载时，插件在启动时、登录之前被加载，但插件内的 onPlug 函数会延迟到登录成功后才被执行
+ 插件被卸载时，插件内的 onUnplug 被执行

#### 插件的编写

编写插件主要就是编写回调函数或定时任务函数，详见 [第四~六节](https://github.com/pandolia/qqbot#%E5%9B%9B%E5%AE%9E%E7%8E%B0%E4%BD%A0%E8%87%AA%E5%B7%B1%E7%9A%84-qq-%E6%9C%BA%E5%99%A8%E4%BA%BA) 。

#### 插件列表

|名称                |github作者    | 功能说明                 | 是否默认加载                 
|:-------------------|:-------------|:----------------------------|:----------------------------
|[qqbot.plugins.sampleslots](https://github.com/pandolia/qqbot/blob/master/qqbot/plugins/sampleslots.py)             |[pandolia](https://github.com/pandolia)       |回调函数示例       |是
|[qqbot.plugins.schedrestart](https://github.com/pandolia/qqbot/blob/master/qqbot/plugins/schedrestart.py)             |[pandolia](https://github.com/pandolia)       |定时重启       |是
|[qqbot.plugins.miniirc](https://github.com/pandolia/qqbot/blob/master/qqbot/plugins/miniirc.md)             |[pandolia](https://github.com/pandolia)       |IRC服务器       |否
|[adblock](https://github.com/feisuweb/qqbot-plugins/tree/master/adblock.py)             |[feisuweb](https://github.com/feisuweb)       |群广告拦截       |否
|[chatlog](https://github.com/feisuweb/qqbot-plugins/blob/master/chatlog.py)             |[feisuweb](https://github.com/feisuweb)       |聊天内容记录       |否

如果您有好用的插件分享，欢迎发邮件给我。

九、 命令行模式下使用 IRC 聊天
----------------------------

linux 系统下，由于无法使用 QQ 客户端，可以使用插件 qqbot.plugins.miniirc 来实现用 IRC 聊天的功能。加载方式： qq plug qqbot.plugins.miniirc ，或启动时加载： qqbot -pl qqbot.plugins.miniirc ，或者在配置文件中的 plugins 选项中加入 `qqbot.plugins.miniirc` 。

插件加载后将在 6667 端口开启一个微型的 IRC 服务器，用户可以使用 IRC 客户端（如 weechat, irssi 等）连接此服务器来实现命令行模式下的聊天。以下以 weechat 为例介绍使用方法：

    启动 weechat ： weechat

    连接本服务器： /connect localhost

    进入 群聊天 会话： /join group-name

    进入 讨论组聊天 会话： /join !discuss-name

    进入 好友聊天 会话： /query buddy-name

    进入 聊天会话 后，直接敲入文本并回车就可以向对方发送消息了。所有接收到的 QQ 消息也会被转发给相应的 聊天会话 。

    在聊天会话之间切换： ctrl+P 或 ctrl+N

    显示所有 群和讨论组 的名称： /list

以上几乎就是此微型 IRC 服务器所提供的所有功能了，但已经足够用来和 QQ 好友/群/讨论组 聊天了。

十、 smartqq 协议支持及限制
-------------------------

#### 本项目已实现绝大部分 smartqq 协议支持的功能，如下：
+ 消息收/发
+ 联系人（包括 好友/群/讨论组/群成员/讨论组成员）资料获取和查询（包括 QQ号/昵称/名称/备注名/群成员名片）
+ 联系人资料根据需要动态更新
+ 被群内其他成员 @ 的通知
+ 群管理功能： 设置/取消管理员 、 设置/删除群名片 、 群成员禁言 以及 踢除群成员
+ 发送、接收表情（详见 [facemap.py](https://github.com/pandolia/qqbot/blob/master/qqbot/facemap.py)）
+ 可以获取到自身发送的 好友/群/讨论组 消息。但若是自身发送的 好友 消息，只能获取消息文本，无法知道该消息发送给谁。

#### 其他功能：
+ 调用系统默认图片浏览器显示登录二维码、将登录二维码发送至邮箱、开启一个 http 服务器用来显示登录二维码、在命令行窗口使用文本模式显示二维码
+ 用 qq 命令行工具发消息、查询|更新联系人、群管理
+ 提供 HTTP-API 接口发消息、查询|更新联系人、群管理
+ 提供 miniirc 插件，可以在命令行模式下使用 IRC 客户端聊天
+ 掉线后自动重启功能（有时需要手工扫码）
+ 定时执行任务（通过 qqbotsched 实现）

#### 因 smartqq 协议的限制，以下问题无法解决：
+ 无法长时间保持在线状态，每次登录成功后的 cookie 会每在 1 ~ 2 天后失效，将被腾讯服务器强制下线，此时 **必须** 手工扫码重新登录。可以打开邮箱模式和自动重启模式，并配合 qqbot.plugins.schedrestart 插件使用，每天在固定的时间扫码登录一次，基本上可以稳定的保持在线状态。
+ 无法发送图片、文件、音频、 xml 卡片消息
+ 当 好友/群/群成员 存在同名现象或名称中含特殊字符时，无法绑定其实际 QQ
+ 无法在群内 @ 其他成员，即便用本程序在群里发送了 “@jack xxx” 这样的消息， jack 也只能收到这个纯文本，收不到“有人@我”的提醒。
+ 无法向 群/讨论组 内的其他非好友成员发消息，也无法收到非好友成员发过来的临时会话消息
+ 在非常少的情况下，发消息时会重复发送多次，也可能对方已收到消息但返回发送失败的结果

十一、其他
-------------

- [常见问题](https://github.com/pandolia/qqbot/blob/master/faq.md)
- [更新日志](https://github.com/pandolia/qqbot/blob/master/changes)

十二、参考资料
-------------

QQBot 参考了以下开源项目：

- [ScienJus/qqbot](https://github.com/ScienJus/qqbot) (ruby)
- [floatinghotpot/qqbot](https://github.com/floatinghotpot/qqbot) (node.js)
- [sjdy521/Mojo-Webqq](https://github.com/sjdy521/Mojo-Webqq) (perl)

在此感谢以上三位作者的无私分享，特别是感谢 ScienJus 对 SmartQQ 协议所做出的深入细致的分析。

十三、反馈
---------

有任何问题或建议可以发邮件给我 <pandolia@yeah.net> ，或者直接提 issue ，也可以加 QQ 群： 577126408 。但还是希望您在提问之前通读一下本文档，很有可能您想要的答案已经在文档中了。
