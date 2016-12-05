httpServerConf = '''\
# 本文件保存 QQBot HTTP 服务器的设置

# 如果本文件中设置了 “http_server_name” 的项，则 QQBot 运行时会开启一个 HTTP 服务器来
# 显示 QQBot 的登录二维码图片。服务器端口号默认为 8080 ，可通过设置 “http_server_port”
# 项来改变此端口号。

# 服务器启动后，可通过下面的地址来访问二维码图片：
#
#   http://<http_server_name>:<http_server_port>/qqbot/qrcode/<qrcode_id>
#
# 其中 “qrcode_id” 是二维码图片 id ，每个 QQBot 实例都会被分配一个唯一的 “qrcode_id“ 。
# 如果该地址需要发送到手机端上进行扫描的，则应保证该地址能在公网中访问。

# 服务器进程启动时会先检查系统中是否已经有同样的服务器在运行，如果有，则退出进程，因此系统中
# 永远只有一个服务器进程在运行。由于每个 QQBot 实例的 ”qrcode_id“ 都是唯一的，因此同一个
# 系统中的所有 QQBot 实例（可能属于不同的进程）可以共用同一个服务器。

# 服务器的 IP 或域名
# http_server_name = localhost

# 服务器的端口，若没有此项，则默认为 8080
# http_server_port = 8080

'''
