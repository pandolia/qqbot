# -*- coding: utf-8 -*-

defaultConfStr = '''\
{
# QQBot 的配置文件

# 显示/关闭调试信息，默认为 False
"debug" : False,

# QQBot 掉线后自动重启，默认为 False
"restartOnOffline" : False,

# 服务器的 IP 或域名，默认为 ""
"httpServerName" : "",

# 服务器的端口，仅 httpServerName 不为 "" 时有效，默认为 8080
"httpServerPort" : 8080,

# 用户信息
"userInfo" : {

    # 用户 DEFAULT ，默认用户
    "DEFAULT" : {
    
        # 自动登录的 QQ 号（i.e. "3497303033"），默认为 ""
        "QQ" : "",
        
        # 接收二维码图片的邮箱账号（i.e. "3497303033@qq.com"），默认为 ""
        "mailAccount" : "",
        
        # 该邮箱的 IMAP/SMTP 服务授权码（i.e. "feregfgftrasdsew"），默认为 ""
        "mailAuthCode" : "",

    },

    # 用户 somebody
    "somebody" : {
        "QQ" : "",
        "mailAccount" : "",
        "mailAuthCode" : "",
    },

},

}
'''

import os, sys, ast
from utf8logger import SetLogLevel, INFO, CRITICAL, RAWINPUT

class QQBotConf:
    isInit = False
    
    @classmethod
    def init(cls, argv=None):
        cls.readConf()
        cls.readCommandLine(argv)
        cls.configure()
        cls.isInit = True
    
    @classmethod
    def readConf(cls):
        conf = ast.literal_eval(defaultConfStr)
        cls.userDefInfo = conf['userInfo']['DEFAULT']
        confPath = cls.ConfPath()
        if os.path.exists(confPath):
            try:
                with open(confPath) as f:
                    cusConf = ast.literal_eval(f.read())

                if type(cusConf) is not dict:
                    raise ValueError('Must be a dict')

                for k, v in conf.items():
                    if k in cusConf:
                        if type(v) is not type(cusConf[k]):
                            raise ValueError('key: %s' % k)
                        conf[k] = cusConf[k]
                
                if type(conf['userInfo']) is not dict:
                    raise ValueError('key: userInfo')
                
                for k, v in conf['userInfo'].items():
                    if type(k) is not str or type(v) is not dict:
                        raise ValueError('key: userInfo.%s' % k)

            except IOError:
                CRITICAL('读取配置文件出现 IOError')
                sys.exit(1)

            except (SyntaxError, ValueError) as e:
                CRITICAL('配置文件语法或格式错误，%s', e)
                sys.exit(1)

        else:
            try:
                with open(confPath, 'w') as f:
                    f.write(defaultConfStr)
            except IOError:
                pass
        
        cls.__dict__.update(conf)
            
    @classmethod
    def readCommandLine(cls, argv=None):
        argv = sys.argv[1:] if argv is None else argv
        
        if argv and argv[0] and argv[0][0] != '-':
            cls.defaultUser = argv[0]
        else:
            cls.defaultUser = 'DEFAULT'
        
        if '-d' in argv or '--debug' in argv:
            cls.debug = True
        
        if '-nd' in argv or '--no-debug' in argv:
            cls.debug = False
        
        if '-r' in argv or '--restart-on-offline' in argv:
            cls.restartOnOffline = True
        
        if '-nr' in argv or '--no-restart-on-offline' in argv:
            cls.restartOnOffline = False        
    
    @classmethod
    def configure(cls):
        SetLogLevel(cls.debug and 'DEBUG' or 'INFO')

    def __init__(self, userName=None, version='unknown'):
        QQBotConf.init() # QQBotConf.isInit or QQBotConf.init()
        self.getUserInfo(userName, version)

    def getUserInfo(self, userName, version):
        self.version = version
        userName = str(userName) if userName else QQBotConf.defaultUser
        userInfo = QQBotConf.userInfo.get(userName, QQBotConf.userDefInfo)
        
        for k in QQBotConf.userDefInfo:
            self.__dict__[k] = str(userInfo.get(k, ''))
        
        if (not self.QQ) and userName.isdigit():
            self.QQ = userName

        argv = sys.argv[1:]
        if '-ac' in argv or '--mail-auth-code' in argv:
            if '-ac' in argv:
                i = argv.index('-ac')
            else:
                i = argv.index('--mail-auth-code')

            if i < len(argv) - 1 and argv[i+1] and argv[i+1][0] != '-':
                self.mailAuthCode = argv[i+1]
        
        if self.mailAccount and not self.mailAuthCode:
            msg = '请输入 %s 的 IMAP/SMTP 服务授权码： ' % self.mailAccount
            self.mailAuthCode = RAWINPUT(msg)
            userInfo['mailAuthCode'] = self.mailAuthCode
        
        self.userName = userName

    def Display(self):
        INFO('配置完成')

        INFO('调试模式：%s', '开启' if QQBotConf.debug else '关闭')
        
        INFO('QQBot 二维码 HTTP 服务器模式： %s',
             '开启' if QQBotConf.httpServerName else '关闭')

        INFO('掉线后自动重启：%s',
             '是' if QQBotConf.restartOnOffline else '否')
        
        INFO('登录用户名： %s' % self.userName)
    
        INFO(('登录方式：自动登录（qq=%s）' % self.QQ)
             if self.QQ else '登录方式：手动登录')
    
        INFO('用于接收二维码的邮箱账号：%s',
             self.mailAccount if self.mailAccount else '无')
    
    tmpDir = os.path.join(os.path.expanduser('~'), '.qqbot-tmp')
    
    @classmethod
    def absPath(cls, rela):
        return os.path.join(cls.tmpDir, rela)
    
    @classmethod
    def ConfPath(cls):
        return cls.absPath('qqbot.conf')

    def PicklePath(self):
        return self.absPath('%s-%s.pickle' % (self.version, self.QQ))
    
    @classmethod
    def QrcodePath(cls, qrcodeId):
        return cls.absPath(qrcodeId+'.png')

if not os.path.exists(QQBotConf.tmpDir):
    os.mkdir(QQBotConf.tmpDir)

if __name__ == '__main__':
    QQBotConf().Display()
