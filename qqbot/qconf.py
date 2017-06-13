# -*- coding: utf-8 -*-

import sys, os
p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if p not in sys.path:
    sys.path.insert(0, p)

version = 'v2.3.2'

sampleConfStr = '''
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
    #     "startAfterFetch" : False,
    #     "pluginPath" : "",
    #     "plugins" : [],
    #     "pluginsConf" : {}
    # },

}
'''

rootConf = {
    "termServerPort" : 8188,
    "httpServerIP" : "",
    "httpServerPort" : 8189,
    "qq" : "",
    "mailAccount" : "",
    "mailAuthCode" : "",
    "cmdQrcode" : False,
    "debug" : False,
    "restartOnOffline" : False,
    "startAfterFetch" : False,
    "pluginPath" : "",
    "plugins" : [],
    "pluginsConf" : {},
}

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

  工作目录：
    -b BENCH, --bench BENCH 指定工作目录，默认为 “~/.qqbot-tmp/”
                            qqbot 运行时将在工作目录下搜索配置文件（v2.x.conf），
                            在工作目录以下的 plugins 目录中搜索插件；并将登录的
                            pickle 文件、联系人 db 文件 以及 临时二维码图片保存在
                            工作目录下。

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
                              默认的监听端口是 8188 (TCP)。

  HTTP二维码查看服务器设置:
  (请阅读说明文件以了解此HTTP服务器的详细信息。)
    -ip HTTPSERVERIP, --httpServerIP HTTPSERVERIP
                            指定HTTP服务要监听在哪个IP地址上。
    -hp HTTPSERVERPORT, --httpServerPort HTTPSERVERPORT
                            指定HTTP服务要监听在哪个端口上。
                              默认的监听端口是 8189 (TCP)

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
    -cq, --cmdQrcode        以文本模式显示二维码
    -saf, --startAfterFetch 全部联系人资料获取完成后再启动 QQBot
    -pp PLUGINPATH, --pluginPath PLUGINPATH
                            设置插件目录
    -pl PLUGINS, --plugins PLUGINS
                            设置启动时需加载的插件

版本:
  {VERSION}\
'''.format(PROGNAME=progname,  VERSION=version)

deprecatedConfKeys = ['fetchInterval', 'monitorTables']

import os, sys, ast, argparse, platform, time, pkgutil

from qqbot.utf8logger import SetLogLevel, INFO, RAWINPUT, PRINT, ERROR
from qqbot.common import STR2BYTES, BYTES2STR, SYSTEMSTR2STR, STR2SYSTEMSTR

class ConfError(Exception):
    pass

class QConf(object):
    def __init__(self, argv=None):
        self.version = version
        self.readCmdLine(argv)
        self.readConfFile()
        self.configure()
    
    def readCmdLine(self, argv):
        if argv is None:
            argv = sys.argv[1:]

        parser = argparse.ArgumentParser(add_help=False)

        parser.add_argument('-h', '--help', action='store_true')

        parser.add_argument('-u', '--user')

        parser.add_argument('-q', '--qq')

        parser.add_argument('-b', '--bench')

        parser.add_argument('-p', '--termServerPort', type=int)

        parser.add_argument('-ip', '--httpServerIP')                            

        parser.add_argument('-hp', '--httpServerPort', type=int)        

        parser.add_argument('-m', '--mailAccount')

        parser.add_argument('-mc', '--mailAuthCode') 

        parser.add_argument('-cq', '--cmdQrcode',
                            action='store_true', default=None)

        parser.add_argument('-d', '--debug',
                            action='store_true', default=None)        

        parser.add_argument('-nd', '--nodebug', action='store_true')        

        parser.add_argument('-r', '--restartOnOffline',
                            action='store_true', default=None)        

        parser.add_argument('-nr', '--norestart',
                            action='store_true')

        parser.add_argument('-saf', '--startAfterFetch',
                            action='store_true', default=None)

        parser.add_argument('-pp', '--pluginPath')

        parser.add_argument('-pl', '--plugins')

        try:
            opts = parser.parse_args(argv)
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
        
        if not opts.bench:
            opts.bench = os.path.join(os.path.expanduser('~'), '.qqbot-tmp')
        
        opts.bench = os.path.abspath(opts.bench)        
        opts.benchstr = SYSTEMSTR2STR(opts.bench)

        if not os.path.exists(opts.bench):
            try:
                os.mkdir(opts.bench)
            except Exception as e:
                PRINT('无法创建工作目录 %s ， %s' % (opts.benchstr, e))
                sys.exit(1)
        elif not os.path.isdir(opts.bench):
            PRINT('无法创建工作目录 %s ' % opts.benchstr)
            sys.exit(1)
        
        if opts.plugins:
            opts.plugins = SYSTEMSTR2STR(opts.plugins).split(',')
        
        if opts.pluginPath:
            opts.pluginPath = SYSTEMSTR2STR(opts.pluginPath)
        
        for k, v in list(opts.__dict__.items()):
            if getattr(self, k, None) is None:
                setattr(self, k, v)

    def readConfFile(self):
        confPath = self.ConfPath()
        strConfPath = SYSTEMSTR2STR(confPath)
        conf = rootConf.copy()

        if os.path.exists(confPath):
            try:
                with open(confPath, 'rb') as f:
                    cusConf = ast.literal_eval(BYTES2STR(f.read()))
    
                if type(cusConf) is not dict:
                    raise ConfError('文件内容必须是一个 dict')

                if type(cusConf.get('默认配置', {})) is not dict:
                    raise ConfError('默认配置必须是一个 dict')
                
                if self.user is not None:
                    if self.user not in cusConf:
                        raise ConfError('用户 %s 不存在' % self.user)                        
                    elif type(cusConf[self.user]) is not dict:
                        raise ConfError('用户 %s 的配置必须是一个 dict'%self.user)                    
                    else:
                        names = ['默认配置', self.user]
                else:
                    names = ['默认配置']
                    
                for name in names:
                    for k, v in list(cusConf.get(name, {}).items()):
                        if k in deprecatedConfKeys:
                            PRINT('被废弃的配置选项 %s ，将忽略此选项' % k)
                        elif k not in conf:
                            raise ConfError('不存在的配置选项 %s.%s ' % (name, k))                               
                        elif type(v) is not type(conf[k]):
                            t = type(conf[k]).__name__
                            raise ConfError('%s.%s 必须是一个 %s' % (name, k, t))
                        else:
                            conf[k] = v
                            
            except (IOError, SyntaxError, ValueError, ConfError) as e:
                PRINT('配置文件 %s 错误: %s\n' % (strConfPath, e), end='')
                sys.exit(1)
        
        else:
            PRINT('未找到配置文件“%s”，将使用默认配置' % strConfPath)
            try:
                with open(confPath, 'wb') as f:
                    f.write(STR2BYTES(sampleConfStr))
            except IOError:
                pass
            else:
                PRINT('已创建一个默认配置文件“%s”' % strConfPath)
            
            if self.user is not None:
                PRINT('用户 %s 不存在\n' % self.user, end='')
                sys.exit(1)
        
        for k, v in list(conf.items()):
            if getattr(self, k, None) is None:
                setattr(self, k, v)

        if self.pluginPath and not os.path.isdir(STR2SYSTEMSTR(self.pluginPath)):
            PRINT('配置文件 %s 错误: 插件目录 “%s” 不存在\n' % \
                  (strConfPath, self.pluginPath), end='')
            sys.exit(1)
        
        if self.mailAccount and not self.mailAuthCode:
            msg = '请输入 %s 的 IMAP/SMTP 服务授权码： ' % self.mailAccount
            self.mailAuthCode = RAWINPUT(msg)
        
        
        if self.cmdQrcode:
            try:
                import PIL
                import wcwidth
            except ImportError:
                PRINT('您已选择以文本模式显示二维码，请先安装 pillow, wcwidth 库')
                sys.exit(1)
                
    def configure(self):
        p = self.absPath('plugins')
        if not os.path.exists(p):
            try:
                os.mkdir(p)
            except:
                pass

        if os.path.isdir(p):
            if p not in sys.path:
                sys.path.insert(0, p)
            self.pluginPath1 = SYSTEMSTR2STR(p)
        else:
            self.pluginPath1 = None

        if self.pluginPath:
            p = os.path.abspath(STR2SYSTEMSTR(self.pluginPath))
            if p not in sys.path:
                sys.path.insert(0, p)
            self.pluginPath = SYSTEMSTR2STR(p)

        try:
            import qqbotdefault as q
        except ImportError:
            pass
        else:        
            for x,name,y in pkgutil.iter_modules(q.__path__, q.__name__+'.'):
                self.plugins.append(name)

        SetLogLevel(self.debug and 'DEBUG' or 'INFO')

    def Display(self):
        INFO('QQBot-%s', self.version)
        INFO('Python %s', platform.python_version())
        INFO('工作目录：%s', self.benchstr)
        INFO('配置文件：%s', SYSTEMSTR2STR(self.ConfPath()))
        INFO('用户名：%s', self.user or '无')
        INFO('登录方式：%s', self.qq and ('自动（qq=%s）' % self.qq) or '手动')        
        INFO('命令行服务器端口号：%s', self.termServerPort or '无')
        INFO('二维码服务器 ip ：%s', self.httpServerIP or '无')
        INFO('二维码服务器端口号：%s',
             self.httpServerIP and self.httpServerPort or '无')
        INFO('用于接收二维码的邮箱账号：%s', self.mailAccount or '无')
        INFO('邮箱服务授权码：%s', self.mailAccount and '******' or '无')
        INFO('以文本模式显示二维码：%s', self.cmdQrcode and '是' or '否')
        INFO('调试模式：%s', self.debug and '开启' or '关闭')
        INFO('掉线后自动重启：%s', self.restartOnOffline and '是' or '否')
        INFO('启动方式：%s',
             self.startAfterFetch and '慢启动（联系人列表获取完成后再启动）'
                                   or '快速启动（登录成功后立即启动）')
        self.pluginPath and INFO('插件目录0：%s', self.pluginPath)
        self.pluginPath1 and INFO('插件目录1：%s', self.pluginPath1)
        INFO('启动时需要加载的插件：%s', self.plugins)

    def absPath(self, rela):
        return os.path.join(self.bench, rela)

    def ConfPath(self):
        return self.absPath('%s.conf' % self.version[:4])

    def PicklePath(self):
        return self.absPath(
            '%s-py%s-%s.pickle' %
            (self.version[:4], platform.python_version(), self.qq)
        )

    def QrcodePath(self, qrcodeId):
        return self.absPath(qrcodeId+'.png')
    
    def SetQQ(self, qq):
        self.qq = qq
    
    def StoreQQ(self):
        if not self.qq:
            return

        try:
            fn = self.absPath('qq(pid%s)' % os.getppid())
            with open(fn, 'w') as f:
                f.write(self.qq)
        except Exception as e:
            ERROR('无法保存当前 QQ 号码, %s', e)
    
    def LoadQQ(self):
        time.sleep(0.5)
        fn = self.absPath('qq(pid%s)' % os.getpid())
        
        if not os.path.exists(fn):
            return self.qq

        try:
            with open(fn, 'r') as f:
                qq = f.read()
        except Exception as e:
            ERROR('无法读取上次运行的 QQ 号码, %s', e)
            qq = self.qq
        else:
            self.qq = qq
            
        try:
            os.remove(fn)
        except OSError:
            pass

        return qq

if __name__ == '__main__':
    QConf().Display()
    # print('')
    QConf(['-u', 'somebody', '-q', 'xxx']).Display()
