# -*- coding: utf-8 -*-

import sys, os
p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if p not in sys.path:
    sys.path.insert(0, p)

version = 'v2.1.10'

sampleConfStr = '''{

    # QQBot 的配置文件
    
    # 用户 somebody 的配置
    "somebody" : {
        
        # QQBot-term 服务器端口号
        "termServerPort" : 8188,
        
        # http 服务器 ip，请设置为公网 ip
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
        
        # 完成一轮联系人列表刷新后的间歇时间
        "fetchInterval" : 120,
        
        # 完成全部联系人列表获取之后才启动 QQBot 
        "startAfterFetch" : False,
        
        # 需要被特别监视的联系人列表
        # 'buddy'/'group'/'discuss' 表示需要特别监视 好友列表/群列表/讨论组列表 中的联系人变动事件
        # 'group-member-456班'/'discuss-member-xx小组' 表示需要特别监视 群”456班“成员列表/讨论组”xx小组“成员列表 中的联系人变动事件
        # 若此项中的列表的数量较少，则被特别监视的列表中的联系人变动事件滞后时间可大幅缩短
        "monitorTables" : ['buddy', 'group-member-456班'],
    
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
        "fetchInterval" : 120, 
        "startAfterFetch" : False,
        "monitorTables" : [],
    },

}
'''

if sys.argv[0].endswith('.py') or sys.argv[0].endswith('.pyc'):
    progname= sys.executable + ' ' + sys.argv[0]
else:
    progname = sys.argv[0]

usage = '''\
QQBot 机器人

用法: {PROGNAME} [-h] [-d] [-nd] [-u USER] [-q QQ]
          [-p TERMSERVERPORT] [-ip HTTPSERVERIP][-hp HTTPSERVERPORT]
          [-m MAILACCOUNT] [-mc MAILAUTHCODE] [-r] [-nr]
          [-fi FETCHINTERVAL]

选项:
  通用:
    -h, --help              显示此帮助页面。
    -d, --debug             启用调试模式。
    -nd, --nodebug          停用调试模式。

  登陆:
    -u USER, --user USER    指定一个配置文件项目以导入设定。
                            USER 指的是配置文件项目的名称。
                            注意: 所有从命令行中指定的参数设定的优先级都会高于
                                  从配置文件中获取的设定。
    -q QQ, --qq QQ          指定本次启动时使用的QQ号。
                            如果指定的QQ号的自动登陆信息存在，那么将会使用自动
                              登陆信息进行快速登陆。

  QTerm本地控制台服务:
    -p TERMSERVERPORT, --termServerPort TERMSERVERPORT
                            更改QTerm控制台的监听端口到 TERMSERVERPORT 。
                            默认的监听端口是 8189 (TCP)。

  HTTP二维码查看服务器设置:
  (请阅读说明文件以了解此HTTP服务器的详细信息。)
    -ip HTTPSERVERIP, --httpServerIP HTTPSERVERIP
                            指定HTTP服务要监听在哪个IP地址上。
                            如需在所有网络接口上监听，请指定 "0.0.0.0" 。
    -hp HTTPSERVERPORT, --httpServerPort HTTPSERVERPORT
                            指定HTTP服务要监听在哪个端口上。

  邮件(IMAP)发送二维码设置:
  (请阅读说明文件以了解如何通过邮件发送二维码，)
    -m MAILACCOUNT, --mailAccount MAILACCOUNT
                            指定用于接收二维码的收件邮箱地址。
    -mc MAILAUTHCODE, --mailAuthCode MAILAUTHCODE
                            设置接收账户的授权码(如果需要的话)。
                            如果命令行和配置文件中都没有指定授权码，而收件
                              邮箱地址已被指定，QQbot将会在启动时要求输入
                              授权码。

  掉线重新启动:
    -r, --restartOnOffline  在掉线时自动重新启动。
    -nr, --norestart        在掉线时不要重新启动。

  其他：
    -fi FETCHINTERVAL, --fetchInterval FETCHINTERVAL
                            设置每轮联系人列表更新之间的间歇时间（单位：秒）。
    -saf, --startAfterFetch 全部联系人资料获取完成后再启动 QQBot
    -mt MONITORTABLES, --monitorTables MONITORTABLES
                            设置需要特别监视的列表，如： -mt buddy,group-member-456班

版本:
  {VERSION}\
'''.format(PROGNAME=progname, VERSION=version)

import os, sys, ast, argparse, platform

from qqbot.utf8logger import SetLogLevel, INFO, RAWINPUT, PRINT
from qqbot.common import STR2BYTES, BYTES2STR

class ConfError(Exception):
    pass

class QConf(object):
    def __init__(self, qq=None, user=None):        
        self.qq = None if qq is None else str(qq)
        self.user = None if user is None else str(user)
        self.version = version
        self.readCmdLine()
        self.readConfFile()
        self.configure()
    
    def readCmdLine(self):
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('-h', '--help', action='store_true')
        parser.add_argument('-u', '--user')        
        parser.add_argument('-q', '--qq')        
        parser.add_argument('-p', '--termServerPort', type=int)
        parser.add_argument('-ip', '--httpServerIP')                            
        parser.add_argument('-hp', '--httpServerPort', type=int)        
        parser.add_argument('-m', '--mailAccount')
        parser.add_argument('-mc', '--mailAuthCode')        
        parser.add_argument('-d', '--debug', action='store_true', default=None)        
        parser.add_argument('-nd', '--nodebug', action='store_true')        
        parser.add_argument('-r', '--restartOnOffline',
                            action='store_true', default=None)        
        parser.add_argument('-nr', '--norestart', action='store_true')
        parser.add_argument('-fi', '--fetchInterval', type=int)
        parser.add_argument('-saf', '--startAfterFetch',
                            action='store_true', default=None)    
        parser.add_argument('-mt', '--monitorTables')

        try:
            opts = parser.parse_args()
        except:
            PRINT(usage)
            sys.exit(1)            
        
        if opts.help:
            PRINT(usage)
            sys.exit(0)
        
        if opts.nodebug:
            opts.debug = False
        
        if opts.norestart:
            opts.restartOnOffline = False
        
        delattr(opts, 'nodebug')
        delattr(opts, 'norestart')
        
        if opts.monitorTables:
            opts.monitorTables = opts.monitorTables.split(',')
        
        for k, v in list(opts.__dict__.items()):
            if getattr(self, k, None) is None:
                setattr(self, k, v)

    def readConfFile(self):
        conf = ast.literal_eval(sampleConfStr)['默认配置']

        confPath = self.ConfPath()

        if os.path.exists(confPath):
            try:
                with open(confPath, 'rb') as f:
                    cusConf = ast.literal_eval(BYTES2STR(f.read()))
    
                if type(cusConf) is not dict:
                    raise ConfError('文件内容必须是一个dict')
                    
                elif self.user is None:
                    pass
                
                elif self.user not in cusConf:
                    raise ConfError('用户 %s 不存在' % self.user)  
                    
                elif type(cusConf[self.user]) is not dict:
                    raise ConfError('用户 %s 的配置必须是一个 dict' % self.user)
                    
                else:        
                    for k, v in list(cusConf[self.user].items()):
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
                PRINT('配置文件 %s 错误: %s\n' % (confPath, e), end='')
                sys.exit(1)
        
        else:
            try:
                with open(confPath, 'wb') as f:
                    f.write(STR2BYTES(sampleConfStr))
            except IOError:
                pass
            
            if self.user is not None:
                PRINT('用户 %s 不存在\n' % self.user, end='')
                sys.exit(1)
        
        for k, v in list(conf.items()):
            if getattr(self, k, None) is None:
                setattr(self, k, v)
        
        if self.mailAccount and not self.mailAuthCode:
            msg = '请输入 %s 的 IMAP/SMTP 服务授权码： ' % self.mailAccount
            self.mailAuthCode = RAWINPUT(msg)

    def configure(self):
        if 0 <= self.fetchInterval < 60:
            self.fetchInterval = 60
        SetLogLevel(self.debug and 'DEBUG' or 'INFO')

    def Display(self):
        INFO('QQBot-%s', self.version)
        INFO('Python %s', platform.python_version())
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
        INFO('每轮联系人列表刷新之间的间歇时间：%d 秒', self.fetchInterval)
        INFO('启动方式：%s',
             self.startAfterFetch and '慢启动（联系人列表获取完成后再启动）'
                                   or '快速启动（登录成功后立即启动）')
        INFO('需要被特别监视的联系人列表：%s', ', '.join(self.monitorTables) or '无')
    
    tmpDir = os.path.join(os.path.expanduser('~'), '.qqbot-tmp')
    
    @classmethod
    def absPath(cls, rela):
        return os.path.join(cls.tmpDir, rela)

    def ConfPath(self):
        return self.absPath('%s.conf' % self.version[:4])

    def PicklePath(self):
        return self.absPath(
            '%s-py%s-%s.pickle' %
            (self.version[:4], platform.python_version(), self.qq)
        )
    
    @classmethod
    def QrcodePath(cls, qrcodeId):
        return cls.absPath(qrcodeId+'.png')

if not os.path.exists(QConf.tmpDir):
    os.mkdir(QConf.tmpDir)

if __name__ == '__main__':
    QConf().Display()
    print('')
    QConf(user='somebody').Display()
