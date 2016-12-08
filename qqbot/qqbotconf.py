# -*- coding: utf-8 -*-


sampleConf = '''\
# HTTP 服务器设置
[httpServer]

# 服务器的 IP 或域名
name = localhost

# 服务器的端口，默认为 8080
port = 8080


# 用户 “usrname” 的用户设置
[USER_usrname]

# 自动登录的 QQ 号
autoLogin = 3497303033

# 接收二维码图片的邮箱账号
mailAccount = 3497303033@qq.com

# 该邮箱的 IMAP/SMTP 服务授权码
mailAuthCode = dsaewfdsfrefdsgdsg
'''


import os, sys

from utf8logger import SetLogLevel, INFO
from utils import MConfigParser

TmpDir = os.path.join(os.path.expanduser('~'), '.qqbot-tmp')
os.path.exists(TmpDir) or os.mkdir(TmpDir)

parser = MConfigParser()
confPath = os.path.join(TmpDir, 'qqbot.conf')
if os.path.exists(confPath):
    parser.read(confPath)
else:
    with open(confPath, 'w') as f:
        f.write(sampleConf)

HTTPServerConf = {
    'name': parser.get('httpServer', 'name', None),
    'port': parser.get('httpServer', 'port', '8080')
}

SetLogLevel('DEBUG')

def UserConf(userName=None):
    if userName is None and len(sys.argv) >= 2:
        userName = sys.argv[1]
    
    if userName:    
        userName = str(userName)
    else:
        userName = '无'

    userSecName = 'USER_' + userName    
    conf = {
        'userName'      : userName,
        'autoLogin'     : parser.get(userSecName, 'autoLogin', None),
        'mailAccount'   : parser.get(userSecName, 'mailAccount', None),
        'mailAuthCode'  : parser.get(userSecName, 'mailAuthCode', None),
    }
    
    if conf['autoLogin'] is None and userName.isdigit():
        conf['autoLogin'] = userName
    
    if conf['mailAccount'] and conf['mailAuthCode'] is None:
        msg = '请输入 %s 的 IMAP/SMTP 服务授权码： ' % conf['mailAccount']
        conf['mailAuthCode'] = raw_input(msg.decode('utf8'))

    return conf

def DisplayConf(conf):
    INFO('登录用户名： %s' % conf['userName'])

    INFO(('登录方式：自动登录（qq=%s）' % conf['autoLogin'])
         if conf['autoLogin'] else '登录方式：手动登录')
            
    INFO('QQBot 二维码 HTTP 服务器模式： %s',
         '开启' if HTTPServerConf['name'] else '关闭')

    INFO('用于接收二维码的邮箱账号：%s',
         conf['mailAccount'] if conf['mailAccount'] else '无')
