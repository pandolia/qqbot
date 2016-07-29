# -*- coding: utf-8 -*-
"""

"""

import json, os, logging, pickle, sys, time, random, platform, subprocess
import requests

# codingEqual('utf8', 'UTF8') = True
# codingEqual('utf8', 'UTF_8') = True
# codingEqual('utf8', None) = True
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

def CodingWrap(coding, writer):
    if not codingEqual(coding, writer.encoding):
        return CodingWrappedWriter(coding, writer)
    else:
        return writer

# 在 windows consoler 下， 运行 print "中文" 会出现乱码
# 请使用： utf8_stdout.write("中文\n")
# 相当于： sys.stdout.write("中文\n".decode('utf8').encode(sys.stdout.encoding))
utf8_stdout = CodingWrap('utf8', sys.stdout)

def setLogger():
    logger = logging.getLogger("QQBot")
    if not logger.handlers:
        logging.getLogger("").setLevel(logging.CRITICAL)
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler(utf8_stdout) # 可以在 windows 下正确输出 utf8 编码的中文字符串
        ch.setFormatter(logging.Formatter('[%(asctime)s] [%(name)s %(levelname)s] %(message)s'))
        logger.addHandler(ch)
    return logger

QLogger = setLogger()

TmpDir = os.path.join(os.path.expanduser('~'), '.qqbot-tmp')
if not os.path.exists(TmpDir):
    os.mkdir(TmpDir)

class Token:
    clientid = 53999199

class QQBot:
    def Login(self, qqNum=None):
        QLogger.info('正在登录，请等待...')
        QLogger.info('登录 Step0 - 检测登录方式')
        if qqNum is None and len(sys.argv) == 2 and sys.argv[1].isdigit():
            qqNum = int(sys.argv[1])

        if qqNum is None:
            QLogger.info('登录方式：手动扫码')
            self.manualLogin()
        else:
            try:
                QLogger.info('登录方式：自动登录')
                self.autoLogin(qqNum)
            except Exception:
                 QLogger.warning('自动登录失败，改用手动登录', exc_info=True)
                 #self.manualLogin()
        QLogger.info('登录成功')

    def manualLogin(self):
        self.prepareLogin()
        self.getQrcode()
        self.waitForAuth()
        self.getPtwebqq()
        self.getVfwebqq()
        self.getUinAndPsessionid()
        self.fetchBuddy()
        self.fetchGroup()
        self.fetchDiscuss()
        self.dumpSessionInfo()
    
    def autoLogin(self, qqNum):
        self.loadSessionInfo(qqNum)
        self.fetchBuddy()
        self.fetchGroup()
        self.fetchDiscuss()
    
    def dumpSessionInfo(self):
        picklePath = os.path.join(TmpDir, '%d.pickle' % self.token.qqNum)
        pickle.dump([self.session, self.token.__dict__], file(picklePath, 'wb'))
        QLogger.info('登录 Session info 已保存至文件：file://%s' % picklePath)
    
    def loadSessionInfo(self, qqNum):
        self.token = Token()
        picklePath = os.path.join(TmpDir, '%d.pickle' % qqNum)
        self.session, self.token.__dict__ = pickle.load(file(picklePath, 'rb'))
        QLogger.info('成功从文件 file://%s 中恢复登录 Session info ，跳过登录 Step 1-5' % picklePath)
    
    def prepareLogin(self):
        self.token = Token()
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
        file(self.qrcodePath, 'wb').write(qrcode)
        try:
            showImage(self.qrcodePath)
        except:
            QLogger.warning('自动弹出二维码图片失败，请用手动打开图片并用手机QQ扫描，图片地址 --> file://%s' % self.qrcodePath)            
    
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
                # ptuiCB('0','0','http://ptlogin4.web2.qq.com/check_sig?...','0','登录成功！', 'kingfucking');\r\n"
                QLogger.info('已获授权')
                items = authStatus.split(',')
                self.token.nick = items[-1].split("'")[1]
                self.token.qqNum = int(self.session.cookies['superuin'][1:])
                self.urlPtwebqq = items[2].strip().strip("'")
                os.remove(self.qrcodePath)
                break
            else:
                raise Exception("reason='检查二维码扫描信息', errInfo='%s'" % authStatus)
    
    def getPtwebqq(self):
        QLogger.info('登录 Step3 - 获取ptwebqq')
        self.urlGet(self.urlPtwebqq)
        self.token.ptwebqq = self.session.cookies['ptwebqq']
    
    def getVfwebqq(self):
        QLogger.info('登录 Step4 - 获取vfwebqq')
        self.token.vfwebqq = self.urlGet(
            url = 'http://s.web2.qq.com/api/getvfwebqq?ptwebqq=%s&clientid=%s&psessionid=&t=%s' % \
                  (self.token.ptwebqq, self.token.clientid, repr(random.random())),
            Referer = 'http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1',
            Origin = 'http://s.web2.qq.com'
        ).json()['result']['vfwebqq']
    
    def getUinAndPsessionid(self):
        QLogger.info('登录 Step5 - 获取uin和psessionid')
        result = self.urlPost(
            url = 'http://d1.web2.qq.com/channel/login2',
            data = {
                'r': json.dumps({
                    "ptwebqq":self.token.ptwebqq, "clientid":self.token.clientid, "psessionid":"", "status":"online"
                })
            },
            Referer = 'http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2',
            Origin = 'http://d1.web2.qq.com'
        ).json()['result']
        self.token.uin = result['uin']
        self.token.psessionid = result['psessionid']
        self.token.hash = qHash(self.token.uin, self.token.ptwebqq)
    
    def fetchBuddy(self):
        QLogger.info('登录 Step6 - 获取好友列表')
        
        # get一下get_online_buddies网页，似乎可以避免103错误
        self.urlGet(
            url = 'http://d1.web2.qq.com/channel/get_online_buddies2?vfwebqq=%s&clientid=%d&psessionid=%s&t=%s' % \
                  (self.token.vfwebqq, self.token.clientid, self.token.psessionid, repr(random.random())),
            Referer = 'http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2',
            Origin = 'http://d1.web2.qq.com'
        )
    
        result = self.urlPost(
            url = 'http://s.web2.qq.com/api/get_user_friends2',
            data = {'r': json.dumps({"vfwebqq":self.token.vfwebqq, "hash":self.token.hash})},
            Referer = 'http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2'
        ).json()
        if result['retcode'] == 0:
            buddies = result['result']['info']
            self.buddy = tuple((buddy['uin'], buddy['nick'].encode('utf-8')) for buddy in buddies)
            self.buddyStr = '好友列表:\n' + idNameList2Str(self.buddy)
            QLogger.info('获取朋友列表成功，共 %d 个朋友' % len(self.buddy))
        else:
            raise Exception("reason='获取好友列表', errInfo=" + str(result))
    
    def fetchGroup(self):
        QLogger.info('登录 Step7 - 获取群列表')
        result = self.urlPost(
            url = 'http://s.web2.qq.com/api/get_group_name_list_mask2',
            data = {'r': json.dumps({"vfwebqq":self.token.vfwebqq, "hash":self.token.hash})},
            Referer = 'http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2'
        ).json()
        if result['retcode'] == 0:
            groups = result['result']['gnamelist']
            self.group = tuple((group['gid'], group['name'].encode('utf-8')) for group in groups)     
            self.groupStr = '讨论组列表:\n' + idNameList2Str(self.group)
            QLogger.info('获取群列表成功，共 %d 个群' % len(self.group))
        else:
            raise Exception("reason='获取群列表', errInfo=" + str(result)) 
    
    def fetchDiscuss(self):
        QLogger.info('登录 Step8 - 获取讨论组列表')
        result = self.urlGet(
            url = 'http://s.web2.qq.com/api/get_discus_list?clientid=%s&psessionid=%s&vfwebqq=%s&t=%s' % \
                  (self.token.clientid, self.token.psessionid, self.token.vfwebqq, repr(random.random())),
            Referer = 'http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2'
        ).json()
        if result['retcode'] == 0:
            discusses = result['result']['dnamelist']
            self.discuss = tuple((discuss['did'], discuss['name'].encode('utf-8')) for discuss in discusses)
            self.discussStr = '讨论组列表:\n' + idNameList2Str(self.discuss)
            QLogger.info('获取讨论组列表成功，共 %d 个讨论组' % len(self.discuss))
        else:
            raise Exception("reason='获取讨论组列表', errInfo=" + str(result))
    
    def poll(self):
        time.sleep(0.3)
        result = self.urlPost(
            url = 'http://d1.web2.qq.com/channel/poll2',
            data = {
                'r': json.dumps({
                    "ptwebqq":self.token.ptwebqq, "clientid":self.token.clientid,
                    "psessionid":self.token.psessionid, "key":""
                })
            },
            Referer = 'http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2'
        ).json()
        if result['retcode'] == 0:
            if 'errmsg' in result: # 无消息
                return ('', 0, 0, '')
            result = result['result'][0]
            msgType = {'message':'buddy', 'group_message':'group', 'discu_message':'discuss'}[result['poll_type']]
            msg = result['value']['content'][1].encode('utf-8')
            from_uin = result['value']['from_uin']
            buddy_uin = result['value'].get('send_uin', from_uin)
            pollResult = msgType, from_uin, buddy_uin, msg
            if msgType == 'buddy':
                QLogger.info('收到一条来自 %s%d 的消息: <%s>' % (msgType, from_uin, msg))
            else:
                QLogger.info('收到一条来自 %s%d(buddy%d) 的消息: <%s>' % pollResult)
            return pollResult
        else:
            raise Exception('errInfo=<%s>' % result)
    
    def sendLongMsg(self, msgType, to_uin, msg):
        while msg:
            front, msg = utf8Partition(msg, 580)
            self.send(msgType, to_uin, front)
    
    def send(self, msgType, to_uin, msg):
        if not msg:
            return ''
        
        try:
            self.msgId += 1
        except AttributeError:
            self.msgId = 6000001
        
        sendUrl = {
            'buddy': 'http://d1.web2.qq.com/channel/send_buddy_msg2',
            'group': 'http://d1.web2.qq.com/channel/send_qun_msg2',
            'discuss': 'http://d1.web2.qq.com/channel/send_discu_msg2'
        }
        sendTag = {"buddy":"to", "group":"group_uin", "discuss":"did"}
        msg = '%s\r\nTag%s' % (msg, repr(random.random()))
        try:
            result = self.urlPost(
                url = sendUrl[msgType], 
                data = {
                    'r': json.dumps({
                        sendTag[msgType]: to_uin,
                        "content": json.dumps([
                            msg, ["font", {"name": "宋体", "size": 10, "style": [0,0,0], "color": "000000"}]
                        ]),
                        "face": 522,
                        "clientid": self.token.clientid,
                        "msg_id": self.msgId,
                        "psessionid": self.token.psessionid
                    })
                },
                Referer = 'http://d1.web2.qq.com/proxy.html?v=20151105001&callback=1&id=2'
            ).json()
        except Exception:
            raise Exception('消息发送失败:  <%s> --> %s%s' % (msg, msgType, to_uin))

        if result.get("errCode", 1) == 0 or result.get('retcode', 1) == 1202:
            sendInfo = '向%s%s发送消息成功' % (msgType, to_uin)
            QLogger.info(sendInfo)
            time.sleep(3)
            if self.msgId % 15 == 0:
                time.sleep(30)
            return sendInfo
        else:
            raise Exception('消息发送失败:  <%s> --> %s%s，errInfo=<%s>' % (msg, msgType, to_uin, result))
        
    
    def urlGet(self, url, **kw):
        time.sleep(0.2)
        self.session.headers.update(kw)
        return self.session.get(url)
    
    def urlPost(self, url, data, **kw):
        time.sleep(0.2)
        self.session.headers.update(kw)
        return self.session.post(url, data=data)
    
    helpInfo = '帮助命令："-help"'  
    
    def PollForever(self):
        QLogger.info(
            'QQBot已启动，请用其他QQ号码向本QQ %s<%d> 发送命令来操作QQBot。%s' % \
            (self.token.nick, self.token.qqNum, self.helpInfo)
        )
        self.stopped = False
        while not self.stopped:
            pullResult = self.poll()
            try:
                self.onPollComplete(*pullResult)
            except Exception:
                QLogger.warning(' onPollComplete 函数出现错误，已忽略', exc_info=True)
        QLogger.info('QQBot已停止')
    
    # overload this method to build your own QQ-bot.    
    def onPollComplete(self, msgType, from_uin, buddy_uin, message): 
        targets = ('buddy', 'group', 'discuss')        
        reply = ''    
        if message == '-help':
            reply = '欢迎使用QQBot，使用方法：\r\n' + \
                    '    -help\r\n' + \
                    '    -list buddy|group|discuss\r\n' + \
                    '    -send buddy/group/discuss uin message\r\n' + \
                    '    -stop'
        elif message[:6] == '-list ':
            target = message[6:].strip()
            reply = getattr(self, target+'Str', '')
        elif message[:6] == '-send ':
            args = message[6:].split(' ', 2)
            if len(args) == 3 and args[0] in targets and args[1].isdigit():
                reply = self.send(args[0], int(args[1]), args[2].strip())
        elif message == '-stop':
            self.stopped = True
            reply = 'QQBot已停止'
        self.sendLongMsg(msgType, from_uin, reply)

# $filename must be an utf8 string
def showImage(filename):
    osName = platform.system()
    if osName == 'Windows':
        retcode = subprocess.call([filename.decode('utf8').encode('cp936')], shell=True)
    elif osName == 'Linux':
        retcode = subprocess.call(['gvfs-open', filename])
    else:
        retcode = 1
    if retcode:
        raise

def idNameList2Str(idNames):
    return '\n'.join('  %d, %s (%d)' % (i,el[1],el[0]) for i,el in enumerate(idNames))

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
        
    while n > 0:        
        ch = ord(msg[n])
        # All utf8 characters start with '0xxx-xxxx' or '11xx-xxxx'
        if (ch >> 7 == 0) or (ch >> 6 == 3):
            break
        n -= 1
    return msg[:n], msg[n:]

if __name__ == '__main__':
    qqbot = QQBot()
    qqbot.Login()
    qqbot.PollForever()
