# -*- coding: utf-8 -*-

defaultConfStr = '''\
{
# QQBot 的配置文件，本文件的配置在 qqbotconf 模块被导入时就已被读取

# 全局设置
"global" : {

    # 显示/关闭调试信息，默认为 False
    "debug" : False,

    # QQBot 掉线后自动重启，默认为 False
    "restartOnOffline" : False,
    
    # 服务器的 IP 或域名，默认为 ""
    "httpServerName" : "",
    
    # 服务器的端口，仅 httpServerName 不为 "" 时有效，默认为 8080
    "httpServerPort" : 8080,

    # 默认登录用户，默认为 "无"
    "defaultUser" : "无",
},

# 用户 somebody 的用户设置
"USER_somebody" : {

    # 自动登录的 QQ 号（i.e. "3497303033"），默认为 ""
    "autoLogin" : "",
    
    # 接收二维码图片的邮箱账号（i.e. "3497303033@qq.com"），默认为 ""
    "mailAccount" : "",
    
    # 该邮箱的 IMAP/SMTP 服务授权码（i.e. "feregfgftrasdsew"），默认为 ""
    "mailAuthCode" : "",
},

}
'''

import os, sys, ast

from utf8logger import SetLogLevel, INFO, CRITICAL

TmpDir, GlobalConf, userConfDict, userDefConf = None, None, None, None

def configure(argv=None):
    global TmpDir, GlobalConf, userConfDict, userDefConf
    
    TmpDir = os.path.join(os.path.expanduser('~'), '.qqbot-tmp')
    if not os.path.exists(TmpDir):
        os.mkdir(TmpDir)

    allConf = ast.literal_eval(defaultConfStr)
    GlobalConf = allConf['global']
    userDefConf = allConf['USER_somebody']

    confPath = os.path.join(TmpDir, 'qqbot.conf')
    if os.path.exists(confPath):
        try:
            with open(confPath) as f:
                s = f.read()
        except IOError:
            CRITICAL('读取配置文件出现 IOError')
            sys.exit(1)
        
        try:
            userConfDict = ast.literal_eval(s)
        except ValueError:
            CRITICAL('配置文件语法错误，应使用 python 的 dict 语法')
            sys.exit(1)
        
        GlobalConf.update(userConfDict.pop('global', {}))
    
    else:
        try:
            with open(confPath, 'w') as f:
                f.write(defaultConfStr)
        except IOError:
            pass
        
        userConfDict = {}
    
    if argv is None:
        argv = sys.argv[1:]
    
    if argv and argv[0] and argv[0][0] != '-':
        GlobalConf['defaultUser'] = argv[0]
    
    if '-d' in argv or '--debug' in argv:
        GlobalConf['debug'] = True
    
    if '-r' in argv or '--restart-on-offline' in argv:
        GlobalConf['restartOnOffline'] = True
    
    if GlobalConf['debug']:
        SetLogLevel('DEBUG')
    else:
        SetLogLevel('INFO')

_userConfDict = {}

def UserConf(userName=None):
    if not userName:
        userName = GlobalConf['defaultUser']
    else:
        userName = str(userName)
    
    if userName in _userConfDict:
        return _userConfDict[userName]
    
    conf = userDefConf.copy()
    conf.update(userConfDict.get('USER_'+userName, {}))    
    conf['userName'] = userName
    
    if (not conf['autoLogin']) and userName.isdigit():
        conf['autoLogin'] = userName
    
    if conf['mailAccount'] and (not conf['mailAuthCode']):
        msg = '请输入 %s 的 IMAP/SMTP 服务授权码： ' % conf['mailAccount']
        conf['mailAuthCode'] = raw_input(msg.decode('utf8'))
    
    _userConfDict[userName] = conf

    return conf

def DisplayUserConf(conf):    
    INFO('登录用户名： %s' % conf['userName'])

    INFO(('登录方式：自动登录（qq=%s）' % conf['autoLogin'])
         if conf['autoLogin'] else '登录方式：手动登录')
            
    INFO('QQBot 二维码 HTTP 服务器模式： %s',
         '开启' if GlobalConf['httpServerName'] else '关闭')

    INFO('用于接收二维码的邮箱账号：%s',
         conf['mailAccount'] if conf['mailAccount'] else '无')
    
    INFO('掉线后自动重启：%s',
         '是' if GlobalConf['restartOnOffline'] else '否')

    INFO('显示调试信息：%s',
         '是' if GlobalConf['debug'] else '否')

configure()
