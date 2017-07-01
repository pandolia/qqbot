本插件（qqbot.plugins.miniirc）为 qqbot-v2.3.3 的自带插件。加载方式： qq plug qqbot.plugins.miniirc 。或启动时加载： qqbot -pl qqbot.plugins.miniirc 。

加载后，将在 6667 端口开启一个微型的 IRC 服务器，用户可以使用 IRC 客户端（如 weechat, irssi 等）连接此服务器来实现命令行模式下的聊天。以下以 weechat 为例介绍使用方法。

启动 weechat ： weechat

连接本服务器： /connect localhost

加入群聊： /join group-name

和好友聊天： /query buddy-name

在消息会话之间切换： ctrl + P 。

以上就是本插件的微型 IRC 服务器所提供的所有功能了，但用来和 QQ 好友/群 聊天也已经足够了。
