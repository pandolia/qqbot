本插件（qqbot.plugins.miniirc）为 qqbot-v2.3.3 的自带插件。加载方式： qq plug qqbot.plugins.miniirc 。或启动时加载： qqbot -pl qqbot.plugins.miniirc 。或者在配置文件中的 plugins 选项中加入 'qqbot.plugins.miniirc' 。

插件加载后将在 6667 端口开启一个微型的 IRC 服务器，用户可以使用 IRC 客户端（如 weechat, irssi 等）连接此服务器来实现命令行模式下的聊天。以下以 weechat 为例介绍使用方法：

启动 weechat ： weechat

连接本服务器： /connect localhost

进入 群聊天 会话： /join group-name

进入 讨论组聊天 会话： /join !discuss-name

进入 好友聊天 会话： /query buddy-name

进入 聊天会话 后，直接敲入文本并回车就可以向对方发送消息了。所有接收到的 QQ 消息也会被转发给相应的 聊天会话 。

在聊天会话之间切换： ctrl+P 或 ctrl+N

显示所有 群和讨论组 的名称： /list

以上几乎就是本插件的微型 IRC 服务器所提供的所有功能了，但已经足够用来和 QQ 好友/群/讨论组 聊天了。
