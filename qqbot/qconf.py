# -*- coding: utf-8 -*-

version = 'v2.0.7'

sampleConfStr = '''{

    # QQBot 的配置文件
    
    # 用户 somebody 的配置
    "somebody" : {
        
        # QQBot-term 服务器端口号
        "termServerPort" : 8188,
        
        # http 服务器 ip，请设置为公网 ip
        # 注意本 ip 不是用来设置服务器的监听 ip 的，只是用来向用户显示图片链接地址的
        # 服务器的监听 ip 永远是 0.0.0.0 ，只要本 ip 不为空，服务器就会开启
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
'''

import os, sys, ast, argparse
from utf8logger import SetLogLevel, INFO, RAWINPUT, utf8Stdout

class ConfError(Exception):
    pass

class QConf:
    def __init__(self, qq=None, user=None):        
        self.qq = None if qq is None else str(qq)
        self.user = None if user is None else str(user)
        self.version = version
        self.readCmdLine()
        self.readConfFile()
        self.configure()
    
    def readCmdLine(self):
        parser = argparse.ArgumentParser()
        
        parser.add_argument('-u', '--user', help='set user name')
        
        parser.add_argument('-q', '--qq',  help='set qq number')
        
        parser.add_argument('-p', '--termServerPort', type=int,
                            help='set the port of term server')
                            
        parser.add_argument('-ip', '--httpServerIP',
                            help='set the ip address of http server')
                            
        parser.add_argument('-hp', '--httpServerPort', type=int,
                            help='set the port of http server')
        
        parser.add_argument('-m', '--mailAccount',
                            help='set mail account that send/receive QRCODE')
        
        parser.add_argument('-mc', '--mailAuthCode',
                            help='set auth code of that mail account')
        
        parser.add_argument('-d', '--debug', action='store_true',
                            help='turn on debug mode', default=None)
        
        parser.add_argument('-nd', '--nodebug', action='store_true',
                            help='turn off debug mode')
        
        parser.add_argument('-r', '--restartOnOffline', action='store_true',
                            help='restart when offline', default=None)
        
        parser.add_argument('-nr', '--norestartOnOffline', action='store_true',
                            help='no restart when offline')
        
        opts = parser.parse_args()
        
        if opts.nodebug:
            opts.debug = False
        
        if opts.norestartOnOffline:
            opts.restartOnOffline = False
        
        delattr(opts, 'nodebug')
        delattr(opts, 'norestartOnOffline')
        
        for k, v in opts.__dict__.items():
            if getattr(self, k, None) is None:
                setattr(self, k, v)

    def readConfFile(self):
        conf = ast.literal_eval(sampleConfStr)['默认配置']
        
        confPath = self.ConfPath()
        
        if os.path.exists(confPath):
            try:
                with open(confPath) as f:
                    cusConf = ast.literal_eval(f.read())
    
                if type(cusConf) is not dict:
                    raise ConfError('文件内容必须是一个dict')
                    
                elif self.user is None:
                    pass
                
                elif self.user not in cusConf:
                    raise ConfError('用户 %s 不存在' % self.user)  
                    
                elif type(cusConf[self.user]) is not dict:
                    raise ConfError('用户 %s 的配置必须是一个 dict' % self.user)
                    
                else:        
                    for k, v in cusConf[self.user].items():
                        if k not in conf:
                            raise ConfError(
                                '不存在的配置选项 %s.%s ' % (self.user, k)
                            )
                               
                        elif type(v) is not type(conf[k]):
                            raise ConfError(
                                '%s.%s 必须是一个 %s' % 
                                (self.user, k, type(conf[k]).__name__)
                            )
    
                        else:
                            conf[k] = v
                            
            except (IOError, SyntaxError, ValueError, ConfError) as e:
                utf8Stdout.write('配置文件 %s 错误: %s\n' % (confPath, e))
                sys.exit(1)
        
        else:
            try:
                with open(confPath, 'w') as f:
                    f.write(sampleConfStr)
            except IOError:
                pass
            
            if self.user is not None:
                utf8Stdout.write('用户 %s 不存在\n' % self.user)
                sys.exit(1)
        
        for k, v in conf.items():
            if getattr(self, k) is None:
                setattr(self, k, v)
        
        if self.mailAccount and not self.mailAuthCode:
            msg = '请输入 %s 的 IMAP/SMTP 服务授权码： ' % self.mailAccount
            self.mailAuthCode = RAWINPUT(msg)

    def configure(self):
        SetLogLevel(self.debug and 'DEBUG' or 'INFO')

    def Display(self):
        INFO('QQBot-%s', self.version)
        INFO('配置完成')
        INFO('用户名： %s', self.user or '无')
        INFO('登录方式：%s', self.qq and ('自动（qq=%s）' % self.qq) or '手动')        
        INFO('命令行服务器端口号：%s', self.termServerPort)       
        INFO('HTTP 服务器 ip ：%s', self.httpServerIP or '无')       
        INFO('HTTP 服务器端口号：%s',
             self.httpServerIP and self.httpServerPort or '无')
        INFO('用于接收二维码的邮箱账号：%s', self.mailAccount or '无')
        INFO('邮箱服务授权码：%s', self.mailAccount and '******' or '无')
        INFO('调试模式：%s', self.debug and '开启' or '关闭')
        INFO('掉线后自动重启：%s', self.restartOnOffline and '是' or '否')
    
    tmpDir = os.path.join(os.path.expanduser('~'), '.qqbot-tmp')
    
    @classmethod
    def absPath(cls, rela):
        return os.path.join(cls.tmpDir, rela)

    def ConfPath(self):
        return self.absPath('%s.conf' % self.version[:4])

    def PicklePath(self):
        return self.absPath('%s-%s.pickle' % (self.version, self.qq))
    
    @classmethod
    def QrcodePath(cls, qrcodeId):
        return cls.absPath(qrcodeId+'.png')

if not os.path.exists(QConf.tmpDir):
    os.mkdir(QConf.tmpDir)

if __name__ == '__main__':
    QConf().Display()
    QConf(user='somebody').Display()
