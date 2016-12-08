# -*- coding: utf-8 -*-


import os, sys, platform, random, pickle, uuid
import time, requests, subprocess, threading, Queue

from utf8logger import setLogLevel, CRITICAL, ERROR, WARN, INFO, DEBUG
from utils import jsonLoads, jsonDumps, MConfigParser
from httpserver import QQBotHTTPServer
from mailagent import MailAgent

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

class Conf:

    @classmethod
    def init(cls):    
        cls.tmpDir = os.path.join(os.path.expanduser('~'), '.qqbot-tmp')
        cls._parser = MConfigParser()
    
        if not os.path.exists(cls.tmpDir):
            os.mkdir(cls.tmpDir)
    
        confPath = os.path.join(cls.tmpDir, 'qqbot.conf')
        if os.path.exists(confPath):
            cls._parser.read(confPath)
        else:
            with open(confPath, 'w') as f:
                f.write(sampleConf)
        
        name = cls._parser.get('httpServer', 'name', None)
        port = cls._parser.get('httpServer', 'port', '8080')
        if name:
            cls.httpServer = QQBotHTTPServer(name, port, cls.tmpDir)
        else:
            cls.httpServer = None
        
    @classmethod
    def getUserConf(cls, userName=None):
        if userName is None and len(sys.argv) >= 2:
            userName = sys.argv[1]
        
        if not userName:
            userName = '无'
        else:
            userName = str(userName)
        
        userSecName = 'USER_' + str(userName)
    
        conf = {
            'userName'       :  userName,
            'httpServerName' :  cls._parser.get('httpServer', 'Name'),
            'httpServerPort' :  cls._parser.get('httpServer', 'Port'),
            'autoLogin'      :  cls._parser.get(userSecName, 'autoLogin'),
            'mailAccount'    :  cls._parser.get(userSecName, 'mailAccount'),
            'mailAuthCode'   :  cls._parser.get(userSecName, 'mailAuthCode')
        }
        
        if conf['autoLogin'] is None and userName.isdigit():
            conf['autoLogin'] = userName
        
        if conf['mailAccount'] and conf['mailAuthCode'] is None:
            conf['mailAuthCode'] = raw_input(u'请输入 %s 的 IMAP/SMTP 服务授权码： ')
        
        return conf

def displayConf(version, conf):
    INFO('QQBot %s 正在登录。用户名： %s' % (version, conf['userName']))
    if conf['autoLogin']:
        INFO('登录方式：自动登录（qq=%s）' % conf['autoLogin'])
    else:
        INFO('登录方式：手动登录')

    INFO('QQBot HTTP 服务器模式： %s' % \
               (conf['httpServerName'] and '开启' or '关闭'))
    INFO('用于接收二维码的邮箱账号：%s', conf['mailAccount'] or '无')