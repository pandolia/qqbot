#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
QQBot -- A conversation robot base on Tencent's SmartQQ
website: https://github.com/pandolia/qqbot/
author: pandolia@yeah.net
"""

QQBotVersion = "QQBot-v1.7.3"

import json, os, logging, pickle, sys, time, random, platform, subprocess
import requests, Queue, threading

# 'utf8', 'UTF8', 'utf-8', 'utf_8', None are all represent the same encoding
def codingEqual(coding1, coding2):
    return coding1 is None or coding2 is None or \
           coding1.replace('-', '').replace('_', '').lower() == \
           coding2.replace('-', '').replace('_', '').lower()

class CodingWrappedWriter:
    def __init__(self, coding, writer):
        self.coding, self.writer = coding, writer

    def write(self, s):
        return self.writer.write(s.decode(self.coding).encode(self.writer.encoding))

    def flush(self):
        return self.writer.flush()

# 在 windows consoler 下， 运行 print "中文" 会出现乱码
# 请使用： utf8_stdout.write("中文\n")
# 相当于： sys.stdout.write("中文\n".decode('utf8').encode(sys.stdout.encoding))
if codingEqual('utf8', sys.stdout.encoding):
    utf8_stdout = sys.stdout
else:
    utf8_stdout = CodingWrappedWriter('utf8', sys.stdout)

def setLogger():
    logger = logging.getLogger(QQBotVersion)
    if not logger.handlers:
        logging.getLogger("").setLevel(logging.CRITICAL)
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler(utf8_stdout) # 可以在 windows 下正确输出 utf8 编码的中文字符串
        ch.setFormatter(logging.Formatter('[%(asctime)s] [%(name)s %(levelname)s] %(message)s'))
        logger.addHandler(ch)
    return logger

QLogger = setLogger()

try:
    TmpDir = os.path.join(os.path.expanduser('~'), '.qqbot-tmp')
    if not os.path.exists(TmpDir):
        os.mkdir(TmpDir)
    tmpfile = os.path.join(TmpDir, 'tmptest%f' % random.random())
    with open(tmpfile, 'w') as f:
        f.write('test')
    os.remove(tmpfile)
except:
    TmpDir = os.getcwd()

class RequestError(Exception):
    pass

class QQBot:
    def Login(self, qqNum=None):
        if qqNum is None and len(sys.argv) == 2 and sys.argv[1].isdigit():
            qqNum = int(sys.argv[1])

        if qqNum is None:
            QLogger.info('登录方式：手动登录')
            self.manualLogin()
        else:
            try:
                QLogger.info('登录方式：自动登录')
                self.autoLogin(qqNum)
            except Exception as e:
                if not isinstance(e, RequestError):
                    QLogger.warning('', exc_info=True)
                QLogger.warning('自动登录失败，改用手动登录')
                self.manualLogin()

        QLogger.info('登录成功。登录账号：%s (%d)', self.nick, self.qqNum)

    def manualLogin(self):
        self.prepareLogin()
        self.getQrcode()
        self.waitForAuth()
        self.getPtwebqq()
        self.getVfwebqq()
        self.getUinAndPsessionid()
        self.testLogin()
        self.fetchBuddy()
        self.fetchGroup()
        self.fetchDiscuss()
        self.dumpSessionInfo()

    def autoLogin(self, qqNum):
        self.loadSessionInfo(qqNum)
        self.testLogin()

    def dumpSessionInfo(self):
        picklePath = os.path.join(TmpDir, '%s-%d.pickle' % (QQBotVersion[:-2], self.qqNum))
        try:
            with open(picklePath, 'wb') as f:
                pickle.dump(self.__dict__, f)
        except:
            QLogger.warning('', exc_info=True)
            QLogger.warning('保存登录 Session info 失败')
        else:
            QLogger.info('登录信息已保存至文件：file://%s' % picklePath)
        self.pollSession = pickle.loads(pickle.dumps(self.session))

    def loadSessionInfo(self, qqNum):
        picklePath = os.path.join(TmpDir, '%s-%d.pickle' % (QQBotVersion[:-2], qqNum))
        with open(picklePath, 'rb') as f:
            self.__dict__ = pickle.load(f)
            QLogger.info('成功从文件 file://%s 中恢复登录信息' % picklePath)
        self.pollSession = pickle.loads(pickle.dumps(self.session))

    def prepareLogin(self):
        self.clientid = 53999199
        self.msgId = 6000000
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:27.0) Gecko/20100101 Firefox/27.0',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        })    
        self.urlGet(
            'https://ui.ptlogin2.qq.com/cgi-bin/login?daid=164&target=self&style=16&mibao_css=m_webqq&' + \
            'appid=501004106&enable_qlogin=0&no_verifyimg=1&s_url=http%3A%2F%2Fw.qq.com%2Fproxy.html&' + \
            'f_url=loginerroralert&strong_login=1&login_state=10&t=20131024001'
        )
        self.session.cookies.update(dict(
            RK='OfeLBai4FB', ptcz='ad3bf14f9da2738e09e498bfeb93dd9da7540dea2b7a71acfb97ed4d3da4e277',
            pgv_pvi='911366144', pgv_info='ssid pgv_pvid=1051433466',
            qrsig='hJ9GvNx*oIvLjP5I5dQ19KPa3zwxNI62eALLO*g2JLbKPYsZIRsnbJIxNe74NzQQ'
        ))
        self.getAuthStatus()
        self.session.cookies.pop('qrsig')

    def getAuthStatus(self):
        return self.urlGet(
            url = 'https://ssl.ptlogin2.qq.com/ptqrlogin?webqq_type=10&remember_uin=1&login2qq=1&aid=501004106&' + \
                  'u1=http%3A%2F%2Fw.qq.com%2Fproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&' + \
                  'ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&dumy=&fp=loginerroralert&' + \
                  'action=0-0-' + repr(random.random() * 900000 + 1000000) + \
                  '&mibao_css=m_webqq&t=undefined&g=1&js_type=0&js_ver=10141&login_sig=&pt_randsalt=0',
            Referer = 'https://ui.ptlogin2.qq.com/cgi-bin/login?daid=164&target=self&style=16&mibao_css=m_webqq&' + \
                      'appid=501004106&enable_qlogin=0&no_verifyimg=1&s_url=http%3A%2F%2Fw.qq.com%2Fproxy.html&' + \
                      'f_url=loginerroralert&strong_login=1&login_state=10&t=20131024001'
        ).content
    
    def getQrcode(self):
        QLogger.info('登录 Step1 - 获取二维码')
        if not hasattr(self, 'qrcodePath'):
            self.qrcodePath = os.path.join(TmpDir, 'qrcode-%f.png' % time.time())
        qrcode = self.urlGet(
            'https://ssl.ptlogin2.qq.com/ptqrshow?appid=501004106&e=0&l=M&s=5&d=72&v=4&t=' + repr(random.random())
        ).content
        with open(self.qrcodePath, 'wb') as f:
            f.write(qrcode)
        try:
            showImage(self.qrcodePath)
        except:
            QLogger.warning('', exc_info=True)
            QLogger.warning('自动弹出二维码图片失败，请手动打开图片并用手机QQ扫描，图片地址 file://%s' % self.qrcodePath)
    
    def waitForAuth(self):
        while True:
            time.sleep(3)
            authStatus = self.getAuthStatus()
            if '二维码未失效' in authStatus:
                # "ptuiCB('66','0','','0','二维码未失效。(457197616)', '');\r\n"
                QLogger.info('登录 Step2 - 等待二维码扫描及授权')
            elif '二维码认证中' in authStatus:
                # "ptuiCB('67','0','','0','二维码认证中。(1006641921)', '');\r\n"
                QLogger.info('二维码已扫描，等待授权')
            elif '二维码已失效' in authStatus:
                # "ptuiCB('65','0','','0','二维码已失效。(4171256442)', '');\r\n"
                QLogger.warning('二维码已失效, 重新获取二维码')
                self.getQrcode()
            elif '登录成功' in authStatus:
                # ptuiCB('0','0','http://ptlogin4.web2.qq.com/check_sig?...','0','登录成功！', 'nickname');\r\n"
                QLogger.info('已获授权')
                items = authStatus.split(',')
                self.nick = items[-1].split("'")[1]
                self.qqNum = int(self.session.cookies['superuin'][1:])
                self.urlPtwebqq = items[2].strip().strip("'")
                try:
                    os.remove(self.qrcodePath)
                except:
                    pass
                delattr(self, 'qrcodePath')
                break
            else:
                raise Exception('获取二维码扫描状态时出错, html="%s"' % authStatus)
    
    def getPtwebqq(self):
        QLogger.info('登录 Step3 - 获取ptwebqq')
        self.urlGet(self.urlPtwebqq)
        self.ptwebqq = self.session.cookies['ptwebqq']
    
    def getVfwebqq(self):
        QLogger.info('登录 Step4 - 获取vfwebqq')
        self.vfwebqq = self.smartRequest(
            url = 'http://s.web2.qq.com/api/getvfwebqq?ptwebqq=%s&clientid=%s&psessionid=&t=%s' % \
                  (self.ptwebqq, self.clientid, repr(random.random())),
            Referer = 'http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1',
            Origin = 'http://s.web2.qq.com'
        )['vfwebqq'].encode('utf8')
    
    def getUinAndPsessionid(self):
        QLogger.info('登录 Step5 - 获取uin和psessionid')
        result = self.smartRequest(
            url = 'http://d1.web2.qq.com/channel/login2',
            data = {
                'r': json.dumps({
                    "ptwebqq":self.ptwebqq, "clientid":self.clientid, "psessionid":"", "status":"online"
                })
            },
            Referer = 'http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2',
            Origin = 'http://d1.web2.qq.com'
        )
        self.uin = result['uin']
        self.psessionid = result['psessionid'].encode('utf8')
        self.hash = qHash(self.uin, self.ptwebqq)

    def testLogin(self):
        # 请求一下 get_online_buddies 页面，似乎可以避免103错误。若请求无错误发生，则表明登录成功
        self.smartRequest(
            url = 'http://d1.web2.qq.com/channel/get_online_buddies2?vfwebqq=%s&clientid=%d&psessionid=%s&t=%s' % \
                  (self.vfwebqq, self.clientid, self.psessionid, repr(random.random())),
            Referer = 'http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2',
            Origin = 'http://d1.web2.qq.com',
            repeatOnDeny = 0
        )

    def fetchBuddy(self):
        QLogger.info('登录 Step6 - 获取好友列表')
        result = self.smartRequest(
            url = 'http://s.web2.qq.com/api/get_user_friends2',
            data = {'r': json.dumps({"vfwebqq":self.vfwebqq, "hash":self.hash})},
            Referer = 'http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2'
        )
        buddies = result['info']
        self.buddy = tuple((buddy['uin'], buddy['nick'].encode('utf-8')) for buddy in buddies)
        self.buddyStr = '好友列表:\n' + idNameList2Str(self.buddy)
        QLogger.info('获取朋友列表成功，共 %d 个朋友' % len(self.buddy))

    def fetchGroup(self):
        QLogger.info('登录 Step7 - 获取群列表')
        result = self.smartRequest(
            url = 'http://s.web2.qq.com/api/get_group_name_list_mask2',
            data = {'r': json.dumps({"vfwebqq":self.vfwebqq, "hash":self.hash})},
            Referer = 'http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2'
        )
        groups = result['gnamelist']
        self.group = tuple((group['gid'], group['name'].encode('utf-8')) for group in groups)
        self.groupStr = '讨论组列表:\n' + idNameList2Str(self.group)
        QLogger.info('获取群列表成功，共 %d 个群' % len(self.group))

    def fetchDiscuss(self):
        QLogger.info('登录 Step8 - 获取讨论组列表')
        result = self.smartRequest(
            url = 'http://s.web2.qq.com/api/get_discus_list?clientid=%s&psessionid=%s&vfwebqq=%s&t=%s' % \
                  (self.clientid, self.psessionid, self.vfwebqq, repr(random.random())),
            Referer = 'http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2'
        )
        discusses = result['dnamelist']
        self.discuss = tuple((discuss['did'], discuss['name'].encode('utf-8')) for discuss in discusses)
        self.discussStr = '讨论组列表:\n' + idNameList2Str(self.discuss)
        QLogger.info('获取讨论组列表成功，共 %d 个讨论组' % len(self.discuss))
    
    def refetch(self):
        self.fetchBuddy()
        self.fetchGroup()
        self.fetchDiscuss()
        self.nick = self.getBuddyDetailInfo(self.uin)['nick'].encode('utf8')
    
    def getBuddyDetailInfo(self, buddy_uin):
        return self.smartRequest(
            url = 'http://s.web2.qq.com/api/get_friend_info2?tuin={uin}'.format(uin=buddy_uin) + \
                  '&vfwebqq={vfwebqq}&clientid=53999199&psessionid={psessionid}&t=0.1'.format(**self.__dict__),
            Referer = 'http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1'
        )

    def poll(self):
        result = self.smartRequest(
            url = 'http://d1.web2.qq.com/channel/poll2',
            data = {
                'r': json.dumps({
                    "ptwebqq":self.ptwebqq, "clientid":self.clientid,
                    "psessionid":self.psessionid, "key":""
                })
            },
            sessionObj = self.pollSession,
            Referer = 'http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2'
        )
        if 'errmsg' in result:
            pollResult = ('', 0, 0, '')  # 无消息
        else:
            result = result[0]
            msgType = {'message':'buddy', 'group_message':'group', 'discu_message':'discuss'}[result['poll_type']]
            from_uin = result['value']['from_uin']
            buddy_uin = result['value'].get('send_uin', from_uin)
            msg = ''.join(
                m.encode('utf8') if isinstance(m, unicode) else "[face%d]" % m[1] if isinstance(m, list) else ''\
                for m in result['value']['content'][1:]
            )
            pollResult = msgType, from_uin, buddy_uin, msg
            if msgType == 'buddy':
                QLogger.info('来自 %s%d 的消息: <%s>' % (msgType, from_uin, msg))
            else:
                QLogger.info('来自 %s%d(buddy%d) 的消息: <%s>' % pollResult)
        return pollResult
    
    def send(self, msgType, to_uin, msg):
        while msg:
            front, msg = utf8Partition(msg, 600)
            self._send(msgType, to_uin, front)

    def _send(self, msgType, to_uin, msg):
        self.msgId += 1        
        if self.msgId % 10 == 0:
            QLogger.info('已连续发送10条消息，强制 sleep 10秒，请等待...')
            time.sleep(10)
        else:
            time.sleep(random.randint(3,5))
        sendUrl = {
            'buddy': 'http://d1.web2.qq.com/channel/send_buddy_msg2',
            'group': 'http://d1.web2.qq.com/channel/send_qun_msg2',
            'discuss': 'http://d1.web2.qq.com/channel/send_discu_msg2'
        }
        sendTag = {"buddy":"to", "group":"group_uin", "discuss":"did"}
        self.smartRequest(
            url = sendUrl[msgType], 
            data = {
                'r': json.dumps({
                    sendTag[msgType]: to_uin,
                    "content": json.dumps([
                        msg,
                        ["font", {"name": "宋体", "size": 10, "style": [0,0,0], "color": "000000"}]
                    ]),
                    "face": 522,
                    "clientid": self.clientid,
                    "msg_id": self.msgId,
                    "psessionid": self.psessionid
                })
            },
            Referer = 'http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2'
        )        
        QLogger.info('向 %s%s 发送消息成功' % (msgType, to_uin))

    def urlGet(self, url, **kw):
        time.sleep(0.2)
        self.session.headers.update(kw)
        return self.session.get(url)

    def smartRequest(self, url, data=None, repeatOnDeny=2, sessionObj=None, **kw):
        time.sleep(0.1)
        session = sessionObj or self.session
        i, j = 0, 0
        while True:
            html = ''
            session.headers.update(**kw)
            try:
                if data is None:
                    html = session.get(url).content
                else:
                    html = session.post(url, data=data).content
                result = json.loads(html)
            except (requests.ConnectionError, ValueError):
                i += 1
                QLogger.warning('', exc_info=True)
                errorInfo = '网络错误或url地址错误'
            else:
                retcode = result.get('retcode', result.get('errCode', -1))
                if retcode == 0 or retcode == 1202:
                    return result.get('result', result)
                else:
                    j += 1
                    errorInfo = '请求被拒绝错误'
            errMsg = '第%d次请求“%s”时出现“%s”，html=%s' % (i+j, url, errorInfo, html)

            # 出现网络错误可以多试几次；若网络没问题，但 retcode 有误，一般连续 3 次都出错就没必要再试了
            if i <= 5 and j <= repeatOnDeny:
                QLogger.warning(errMsg + '！等待 3 秒后重新请求一次。')
                time.sleep(3)
            else:
                QLogger.warning(errMsg + '！停止再次请求！！！')
                raise RequestError

    # class attribut `helpInfo` will be printed at the beginning of `Run` method   
    helpInfo = '帮助命令："-help"'

    def Run(self):
        self.msgQueue = Queue.Queue()
        self.stopped = False

        pullThread = threading.Thread(target=self.pullForever)
        pullThread.setDaemon(True)
        pullThread.start()
        
        QLogger.info(
            'QQBot已启动，请用其他QQ号码向本QQ %s<%d> 发送命令来操作QQBot。%s' % \
            (self.nick, self.qqNum, self.__class__.__dict__.get('helpInfo', ''))
        )        
        
        while not self.stopped:
            try:
                pullResult = self.msgQueue.get()
                if pullResult is None:
                    break
                self.onPollComplete(*pullResult)
            except KeyboardInterrupt:
                self.stopped = True
            except RequestError:
                QLogger.error('向 QQ 服务器请求数据时出错')
                break
            except:
                QLogger.warning('', exc_info=True)
                QLogger.warning(' onPollComplete 方法出错，已忽略')
        
        if self.stopped:
            QLogger.info("QQBot正常退出")
        else:
            QLogger.error('QQBot异常退出')

    def pullForever(self):
        while not self.stopped:
            try:
                pullResult = self.poll()
                self.msgQueue.put(pullResult)
            except KeyboardInterrupt:
                self.stopped = True
                self.msgQueue.put(None)
            except RequestError:
                QLogger.error('向 QQ 服务器请求数据时出错')
                self.msgQueue.put(None)
                break
            except:
                QLogger.warning('', exc_info=True)
                QLogger.warning(' poll 方法出错，已忽略')

    # overload this method to build your own QQ-bot.    
    def onPollComplete(self, msgType, from_uin, buddy_uin, message):
        reply = ''    
        if message == '-help':
            reply = '欢迎使用QQBot，使用方法：\n' + \
                    '\t-help\n' + \
                    '\t-list buddy|group|discuss\n' + \
                    '\t-send buddy|group|discuss uin message\n' + \
                    '\t-refetch\n' + \
                    '\t-stop\n'
        elif message[:6] == '-list ':
            reply = getattr(self, message[6:].strip()+'Str', '')
        elif message[:6] == '-send ':
            args = message[6:].split(' ', 2)
            if len(args) == 3 and args[1].isdigit() and args[0] in ['buddy', 'group', 'discuss']:               
                self.send(args[0], int(args[1]), args[2].strip())
                reply = '消息发送成功'
        elif message == '-refetch':
            self.refetch()
            reply = '重新获取 好友/群/讨论组 成功'
        elif message == '-stop':
            reply = 'QQBot已关闭'
            self.stopped = True
        self.send(msgType, from_uin, reply)

# $filename must be an utf8 string
def showImage(filename):
    osName = platform.system()
    if osName == 'Windows':
        retcode = subprocess.call([filename.decode('utf8').encode('cp936')], shell=True)
    elif osName == 'Linux':
        retcode = subprocess.call(['gvfs-open', filename])
    elif osName == 'Darwin':
        retcode = subprocess.call(['open', filename])
    else:
        retcode = 1
    if retcode:
        raise

def idNameList2Str(idNames):
    return '\n'.join('\t%d, %s (%d)' % (i,el[1],el[0]) for i,el in enumerate(idNames))

def qHash(x, K):
    N = [0] * 4
    for T in range(len(K)):
        N[T%4] ^= ord(K[T])

    U = "ECOK"
    V = [0] * 4    
    V[0] = ((x >> 24) & 255) ^ ord(U[0])
    V[1] = ((x >> 16) & 255) ^ ord(U[1])
    V[2] = ((x >>  8) & 255) ^ ord(U[2])
    V[3] = ((x >>  0) & 255) ^ ord(U[3])

    U1 = [0] * 8

    for T in range(8):
        U1[T] = N[T >> 1] if T % 2 == 0 else V[T >> 1]

    N1 = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]
    V1 = ""
    for aU1 in U1:
        V1 += N1[((aU1 >> 4) & 15)]
        V1 += N1[((aU1 >> 0) & 15)]

    return V1

def utf8Partition(msg, n):
    if n >= len(msg):
        return msg, ''
    else:
        # All utf8 characters start with '0xxx-xxxx' or '11xx-xxxx'
        while n > 0 and ord(msg[n]) >> 6 == 2:
            n -= 1
        return msg[:n], msg[n:]

def main():
    bot = QQBot()
    bot.Login()
    bot.Run()

if __name__ == '__main__':
    main()
