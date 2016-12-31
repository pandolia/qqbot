#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
QQBot   -- A conversation robot base on Tencent's SmartQQ
Website -- https://github.com/pandolia/qqbot/
Author  -- pandolia@yeah.net
"""

QQBotVersion = 'v1.9.7'

import sys, random, pickle, time, requests, threading, Queue, subprocess

from utf8logger import CRITICAL, WARN, INFO, DEBUG, DisableLog, EnableLog
from common import JsonLoads, JsonDumps, Utf8Partition, CutDict
from qqbotconf import QQBotConf
from qrcodemanager import QrcodeManager

def main():
    try:
        if sys.argv[-1] == '--subprocessCall':
            isSubprocessCall = True
            sys.argv.pop()
        else:
            isSubprocessCall = False
            
        conf = QQBotConf(version=QQBotVersion)
        if not conf.restartOnOffline or isSubprocessCall:
            bot = QQBot(conf=conf)
            bot.Login()
            bot.Run()
        else:
            args = ['python', __file__] + \
                   sys.argv[1:] + \
                   ['--mailAuthCode', conf.mailAuthCode] + \
                   ['--subprocessCall']
            while subprocess.call(args) != 0:
                INFO('重新启动 QQBot ')

    except KeyboardInterrupt:
        sys.exit(0)

class RequestError(SystemExit):
    pass

class QQBot:
    def __init__(self, qq=None, user=None, conf=None):
        INFO('QQBot-%s', QQBotVersion)
        self.conf = conf or QQBotConf(qq, user, QQBotVersion)
        self.conf.Display()
        self.qrcodeManager = QrcodeManager(self.conf)
        self.nonDumpAttrs = self.__dict__.keys()

    def Login(self):
        INFO(self.conf.qq and '开始自动登录...' or '开始手动登录...')
        if not self.conf.qq or not self.autoLogin():
            self.manualLogin()
        INFO('登录成功。登录账号：%s (%d)', self.nick, self.qqNum)

    def manualLogin(self):
        try:
            self.prepareSession()
            self.waitForAuth()
            self.getPtwebqq()
            self.getVfwebqq()
            self.getUinAndPsessionid()
            self.testLogin()
            self.fetchBuddies()
            self.fetchGroups()
            self.fetchDiscusses()
            self.dumpSessionInfo()
        except RequestError:
            CRITICAL('手动登录失败！')
            sys.exit(1)

    def autoLogin(self):
        try:
            self.loadSessionInfo()
            self.testLogin()
            return True
        except RequestError:
            e = '上次保存的 Session info 已过期'
        except Exception as e:
            e = str(e)
        
        WARN('自动登录失败，原因：%s', e)
        return False

    def dumpSessionInfo(self):
        self.pollSession = pickle.loads(pickle.dumps(self.session))
        picklePath = self.conf.PicklePath()
        nonDump = CutDict(self.__dict__, self.nonDumpAttrs)
        try:
            with open(picklePath, 'wb') as f:
                f.write(pickle.dumps(self.__dict__))
        except IOError:
            WARN('保存 Session info 失败：IOError %s', picklePath)
        else:
            INFO('Session info 已保存至文件：file://%s' % picklePath)
        self.__dict__.update(nonDump)

    def loadSessionInfo(self):
        picklePath = self.conf.PicklePath()
        with open(picklePath, 'rb') as f:
            self.__dict__.update(pickle.load(f))
        INFO('成功从文件 file://%s 中恢复 Session info' % picklePath)

    def prepareSession(self):
        self.clientid = 53999199
        self.msgId = 6000000
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9;'
                           ' rv:27.0) Gecko/20100101 Firefox/27.0'),
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        })
        self.urlGet(
            'https://ui.ptlogin2.qq.com/cgi-bin/login?daid=164&target=self&'
            'style=16&mibao_css=m_webqq&appid=501004106&enable_qlogin=0&'
            'no_verifyimg=1&s_url=http%3A%2F%2Fw.qq.com%2Fproxy.html&'
            'f_url=loginerroralert&strong_login=1&login_state=10&t=20131024001'
        )
        self.session.cookies.update({
            'RK': 'OfeLBai4FB',
            'pgv_pvi': '911366144',
            'pgv_info': 'ssid pgv_pvid=1051433466',
            'ptcz': ('ad3bf14f9da2738e09e498bfeb93dd9da7'
                     '540dea2b7a71acfb97ed4d3da4e277'),
            'qrsig': ('hJ9GvNx*oIvLjP5I5dQ19KPa3zwxNI'
                      '62eALLO*g2JLbKPYsZIRsnbJIxNe74NzQQ')
        })
        self.getAuthStatus()
        self.session.cookies.pop('qrsig')

    def waitForAuth(self):
        try:
            qrcode = self.getQrcode()
            self.qrcodeManager.Show(qrcode)
            while True:
                time.sleep(3)
                authStatus = self.getAuthStatus()
                if '二维码未失效' in authStatus:
                    INFO('登录 Step2 - 等待二维码扫描及授权')
                    if self.conf.mailAccount:
                        self.qrcodeManager.Show(qrcode)
                elif '二维码认证中' in authStatus:
                    INFO('二维码已扫描，等待授权')
                elif '二维码已失效' in authStatus:
                    WARN('二维码已失效, 重新获取二维码')
                    qrcode = self.getQrcode()
                    self.qrcodeManager.Show(qrcode)
                elif '登录成功' in authStatus:
                    INFO('已获授权')
                    items = authStatus.split(',')
                    self.nick = items[-1].split("'")[1]
                    self.qqNum = int(self.session.cookies['superuin'][1:])
                    self.conf.qq = str(self.qqNum)
                    self.urlPtwebqq = items[2].strip().strip("'")
                    break
                else:
                    CRITICAL('获取二维码扫描状态时出错, html="%s"', authStatus)
                    sys.exit(1)
        finally:
            self.qrcodeManager.Clear()

    def getQrcode(self, firstTime=True):
        INFO('登录 Step1 - 获取二维码')
        return self.urlGet(
            'https://ssl.ptlogin2.qq.com/ptqrshow?appid=501004106&e=0&l=M&' +
            's=5&d=72&v=4&t=' + repr(random.random())
        )

    def getAuthStatus(self):
        return self.urlGet(
            url='https://ssl.ptlogin2.qq.com/ptqrlogin?webqq_type=10&' +
                'remember_uin=1&login2qq=1&aid=501004106&u1=http%3A%2F%2F' +
                'w.qq.com%2Fproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&' +
                'ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&' +
                'dumy=&fp=loginerroralert&action=0-0-' +
                repr(random.random() * 900000 + 1000000) +
                '&mibao_css=m_webqq&t=undefined&g=1&js_type=0' +
                '&js_ver=10141&login_sig=&pt_randsalt=0',
            Referer=('https://ui.ptlogin2.qq.com/cgi-bin/login?daid=164&'
                     'target=self&style=16&mibao_css=m_webqq&appid=501004106&'
                     'enable_qlogin=0&no_verifyimg=1&s_url=http%3A%2F%2F'
                     'w.qq.com%2Fproxy.html&f_url=loginerroralert&'
                     'strong_login=1&login_state=10&t=20131024001')
        )

    def getPtwebqq(self):
        INFO('登录 Step3 - 获取ptwebqq')
        self.urlGet(self.urlPtwebqq)
        self.ptwebqq = self.session.cookies['ptwebqq']

    def getVfwebqq(self):
        INFO('登录 Step4 - 获取vfwebqq')
        self.vfwebqq = self.smartRequest(
            url = ('http://s.web2.qq.com/api/getvfwebqq?ptwebqq=%s&'
                   'clientid=%s&psessionid=&t={rand}') %
                  (self.ptwebqq, self.clientid),
            Referer = ('http://s.web2.qq.com/proxy.html?v=20130916001'
                       '&callback=1&id=1'),
            Origin = 'http://s.web2.qq.com'
        )['vfwebqq']

    def getUinAndPsessionid(self):
        INFO('登录 Step5 - 获取uin和psessionid')
        result = self.smartRequest(
            url = 'http://d1.web2.qq.com/channel/login2',
            data = {
                'r': JsonDumps({
                    'ptwebqq': self.ptwebqq, 'clientid': self.clientid,
                    'psessionid': '', 'status': 'online'
                })
            },
            Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001'
                       '&callback=1&id=2'),
            Origin = 'http://d1.web2.qq.com'
        )
        self.uin = result['uin']
        self.psessionid = result['psessionid']
        self.hash = qHash(self.uin, self.ptwebqq)

    def testLogin(self):
        try:
            DisableLog()
            # 请求一下 get_online_buddies 页面，避免103错误。
            # 若请求无错误发生，则表明登录成功
            self.smartRequest(
                url = ('http://d1.web2.qq.com/channel/get_online_buddies2?'
                       'vfwebqq=%s&clientid=%d&psessionid=%s&t={rand}') %
                      (self.vfwebqq, self.clientid, self.psessionid),
                Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001&'
                           'callback=1&id=2'),
                Origin = 'http://d1.web2.qq.com',
                repeatOnDeny = 0
            )
        finally:
            EnableLog()

    def fetchBuddies(self):
        INFO('登录 Step6 - 获取好友列表')
        result = self.smartRequest(
            url = 'http://s.web2.qq.com/api/get_user_friends2',
            data = {
                'r': JsonDumps({'vfwebqq':self.vfwebqq, 'hash':self.hash})
            },
            Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001&'
                       'callback=1&id=2')
        )
        ss, self.buddies, self.buddiesDictU, self.buddiesDictQ = [], [], {}, {}
        for info in result.get('info', []):
            uin = info['uin']
            name = info['nick']
            qq = self.fetchBuddyQQ(uin)
            buddy = {'uin': uin, 'qq': qq, 'name': name}
            self.buddies.append(buddy)
            self.buddiesDictU[uin] = buddy
            self.buddiesDictQ[qq] = buddy
            s = '%d, %s, uin%d' % (qq, name, uin)
            INFO('好友： ' + s)
            ss.append(s)
        self.buddyStr = '好友列表:\n' + '\n'.join(ss)
        INFO('获取朋友列表成功，共 %d 个朋友' % len(self.buddies))
    
    def fetchBuddyQQ(self, uin):
        return self.smartRequest(
            url = ('http://s.web2.qq.com/api/get_friend_uin2?tuin=%d&'
                   'type=1&vfwebqq=%s&t={rand}') % (uin, self.vfwebqq),
            Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001&'
                       'callback=1&id=2')
        )['account']

    def fetchBuddyDetailInfo(self, uin):
        return self.smartRequest(
            url = ('http://s.web2.qq.com/api/get_friend_info2?tuin=%s&'
                   'vfwebqq=%s&clientid=%s&psessionid=%s&t={rand}') % \
                  (uin, self.vfwebqq, self.clientid, self.psessionid),
            Referer = ('http://s.web2.qq.com/proxy.html?v=20130916001&'
                       'callback=1&id=1')
        )
    
    unexist = {'uin': -1, 'qq': -1, 'name': 'UNEXIST',
               'member': {}, 'memberStr': ''}
    
    def getBuddyByUin(self, uin):
        return self.buddiesDictU.get(uin, QQBot.unexist)
    
    def getBuddyByQQ(self, qq):
        return self.buddiesDictQ.get(qq, QQBot.unexist)

    def fetchGroups(self):
        INFO('登录 Step7 - 获取群列表')
        INFO('=' * 60)
        result = self.smartRequest(
            url = 'http://s.web2.qq.com/api/get_group_name_list_mask2',
            data = {
                'r': JsonDumps({'vfwebqq':self.vfwebqq, 'hash':self.hash})
            },
            Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001&'
                       'callback=1&id=2')
        )

        ss, self.groups, self.groupsDictU, self.groupsDictQ = [], [], {}, {}
        for info in result.get('gnamelist', []):
            uin = info['gid']
            name = info['name']
            qq = self.fetchGroupQQ(uin)
            member = self.fetchGroupMember(info['code'])
            group = {'uin': uin, 'qq': qq, 'name': name, 'member': member}

            self.groups.append(group)
            self.groupsDictU[uin] = group
            self.groupsDictQ[qq%1000000] = group

            s = '%d, %s, uin%d' % (qq, name, uin)
            ss.append(s)
            INFO('群： ' + s)

            mss = []
            for uin, name in member.items():
                ms = '%s, uin%d' % (name, uin)
                INFO('    成员: %s', ms)
                mss.append(ms)
            INFO('=' * 60)

            group['memberStr'] = '群 %s 的成员列表:\n%s' % (name,'\n'.join(mss))

        self.groupStr = '群列表:\n' + '\n'.join(ss)

        INFO('获取群列表成功，共 %d 个朋友' % len(self.groups))
    
    def fetchGroupQQ(self, uin):
        return self.smartRequest(
            url = ('http://s.web2.qq.com/api/get_friend_uin2?tuin=%d&'
                   'type=4&vfwebqq=%s&t={rand}') % (uin, self.vfwebqq),
            Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001&'
                       'callback=1&id=2')
        )['account']
    
    def fetchGroupMember(self, gcode):
        ret = self.smartRequest(
            url = ('http://s.web2.qq.com/api/get_group_info_ext2?gcode=%d'
                   '&vfwebqq=%s&t={rand}') % (gcode, self.vfwebqq),
            Referer = ('http://s.web2.qq.com/proxy.html?v=20130916001'
                       '&callback=1&id=1')
        )
        minfos = ret['minfo']
        members = ret['ginfo']['members']
        return dict((m['muin'],inf['nick']) for m,inf in zip(members,minfos))
    
    def getGroupByUin(self, uin):
        return self.groupsDictU.get(uin, QQBot.unexist)
    
    def getGroupByQQ(self, qq):
        return self.groupsDictQ.get(qq%1000000, QQBot.unexist)

    def fetchDiscusses(self):
        INFO('登录 Step8 - 获取讨论组列表')
        INFO('=' * 60)
        result = self.smartRequest(
            url = ('http://s.web2.qq.com/api/get_discus_list?clientid=%s&'
                   'psessionid=%s&vfwebqq=%s&t={rand}') % 
                  (self.clientid, self.psessionid, self.vfwebqq),
            Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001'
                       '&callback=1&id=2')
        )
        ss, self.discusses, self.discussesDict = [], [], {}
        for info in result.get('dnamelist', []):
            uin = info['did']
            name = info['name']
            member = self.fetchDiscussMember(uin)
            discuss = {'uin': uin, 'name': name, 'member': member}
            self.discusses.append(discuss)
            self.discussesDict[uin] = discuss
            s = '%s, uin%d' % (name, uin)
            INFO('讨论组： ' + s)
            ss.append(s)            
            
            mss = []
            for uin, name in member.items():
                ms = '%s, uin%d' % (name, uin)
                INFO('    成员: %s', ms)
                mss.append(ms)
            INFO('=' * 60)

            discuss['memberStr'] = '讨论组的 %s 的成员列表:\n%s' % \
                                   (name, '\n'.join(mss))            
            
        self.discussStr = '讨论组列表:\n' + '\n'.join(ss)
        INFO('获取讨论组列表成功，共 %d 个讨论组' % len(self.discusses))
    
    def fetchDiscussMember(self, uin):
        ret = self.smartRequest(
            url = ('http://d1.web2.qq.com/channel/get_discu_info?'
                   'did=%s&psessionid=%s&vfwebqq=%s&clientid=%s&t={rand}') %
                  (uin, self.psessionid, self.vfwebqq, self.clientid),
            Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001'
                       '&callback=1&id=2')
        )
        return dict((m['uin'], m['nick']) for m in ret['mem_info'])
    
    def getDiscussByUin(self, uin):
        return self.discussesDict.get(uin, QQBot.unexist)

    def refetch(self):
        self.fetchBuddies()
        self.fetchGroups()
        self.fetchDiscusses()
        self.nick = self.fetchBuddyDetailInfo(self.uin)['nick']

    def poll(self):
        result = self.smartRequest(
            url = 'https://d1.web2.qq.com/channel/poll2',
            data = {
                'r': JsonDumps({
                    'ptwebqq':self.ptwebqq, 'clientid':self.clientid,
                    'psessionid':self.psessionid, 'key':''
                })
            },
            sessionObj = self.pollSession,
            Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001&'
                       'callback=1&id=2')
        )
        if not result or 'errmsg' in result:
            return ('', 0, 0, '')  # 无消息
        else:
            result = result[0]

            msgType = {
                'message': 'buddy',
                'group_message': 'group',
                'discu_message': 'discuss'
            }[result['poll_type']]
            from_uin = result['value']['from_uin']
            buddy_uin = result['value'].get('send_uin', from_uin)
            msg = ''.join(
                ('[face%d]' % m[1]) if isinstance(m, list) else str(m)
                for m in result['value']['content'][1:]
            )

            if msgType == 'buddy':
                bName = self.getBuddyByUin(buddy_uin)['name']
                INFO('来自 好友“%s” 的消息: "%s"' % (bName, msg))
            elif msgType == 'group':
                group = self.getGroupByUin(from_uin)
                gName = group['name']
                bName = group['member'].get(buddy_uin, 'unknown')
                INFO('来自 群“%s”[成员“%s”] 的消息: "%s"' % (gName, bName, msg))
            else:
                discuss = self.getDiscussByUin(from_uin)
                gName = discuss['name']
                bName = discuss['member'].get(buddy_uin, 'unknown')
                INFO('来自 讨论组“%s”[成员“%s”] 的消息: "%s"' % (gName,bName,msg))

            return (msgType, from_uin, buddy_uin, msg)

    def send(self, msgType, to_uin, msg):
        while msg:
            front, msg = Utf8Partition(msg, 600)
            self._send(msgType, to_uin, front)

    def _send(self, msgType, to_uin, msg):
        self.msgId += 1
        if self.msgId % 10 == 0:
            INFO('已连续发送10条消息，强制 sleep 10秒，请等待...')
            time.sleep(10)
        else:
            time.sleep(random.randint(3,5))
        sendUrl = {
            'buddy': 'http://d1.web2.qq.com/channel/send_buddy_msg2',
            'group': 'http://d1.web2.qq.com/channel/send_qun_msg2',
            'discuss': 'http://d1.web2.qq.com/channel/send_discu_msg2'
        }
        sendTag = {'buddy':'to', 'group':'group_uin', 'discuss':'did'}
        self.smartRequest(
            url = sendUrl[msgType],
            data = {
                'r': JsonDumps({
                    sendTag[msgType]: to_uin,
                    'content': JsonDumps([
                        msg, ['font', {'name': '宋体', 'size': 10,
                                       'style': [0,0,0], 'color': '000000'}]
                    ]),
                    'face': 522,
                    'clientid': self.clientid,
                    'msg_id': self.msgId,
                    'psessionid': self.psessionid
                })
            },
            Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001&'
                       'callback=1&id=2')
        )
        
        if msgType == 'buddy':
            INFO('向 好友“%s” 发消息成功', self.getBuddyByUin(to_uin)['name'])
        elif msgType == 'group':
            INFO('向 群“%s” 发消息成功', self.getGroupByUin(to_uin)['name'])
        else:
            INFO('向 讨论组“%s” 发消息成功', self.getDiscussByUin(to_uin)['name'])

    def urlGet(self, url, **kw):
        time.sleep(0.2)
        self.session.headers.update(kw)
        return self.session.get(url).content

    def smartRequest(self, url, data=None,
                     repeatOnDeny=2, sessionObj=None, **kw):
        session = sessionObj or self.session
        nCE, nTO, nUE, nDE = 0, 0, 0, 0
        while True:
            url = url.format(rand=repr(random.random()))
            html, errorInfo = '', ''
            session.headers.update(**kw)
            try:
                if data is None:
                    resp = session.get(url)
                else:
                    resp = session.post(url, data=data)
            except requests.ConnectionError as e:
                nCE += 1
                errorInfo = '网络错误 %s' % e
            else:
                html = resp.content
                if resp.status_code in (502, 504):
                    session.get(
                        ('http://pinghot.qq.com/pingd?dm=w.qq.com.hot&'
                         'url=/&hottag=smartqq.im.polltimeout&hotx=9999&'
                         'hoty=9999&rand=%s') % random.randint(10000, 99999)
                    )
                    if url == 'https://d1.web2.qq.com/channel/poll2':
                        return {'errmsg': ''}
                    nTO += 1
                    errorInfo = '超时'
                else:
                    try:
                        result = JsonLoads(html)
                    except ValueError:
                        nUE += 1
                        errorInfo = ' URL 地址错误'
                    else:
                        retcode = \
                            result.get('retcode', result.get('errCode', -1))
                        if retcode in (0, 1202, 100003):
                            return result.get('result', result)
                        else:
                            nDE += 1
                            errorInfo = '请求被拒绝错误'

            # 出现网络错误或超时可以多试几次 (nCE < 5, nTO < 9)；
            # 若出现 URL 地址错误或 retcode 有误，一般连续 3 次都出错就没必要再试了
            if nCE < 5 and nTO < 9 and nUE < 3 and nDE <= repeatOnDeny:
                DEBUG('第%d次请求“%s”时出现“%s”, html=%s',
                      nCE+nTO+nUE+nDE, url, errorInfo, repr(html))
            else:
                CRITICAL('第%d次请求“%s”时出现“%s”，终止 QQBot',
                         nCE+nTO+nUE+nDE, url, errorInfo)
                raise RequestError  # (SystemExit)

    # class attribute `helpInfo` will be printed at the start of `Run` method
    helpInfo = '帮助命令："-help"'

    def Run(self):
        self.msgQueue = Queue.Queue()
        self.pollThread = threading.Thread(target=self.pollForever)
        self.pollThread.daemon = True
        self.pollThread.start()

        INFO(
            'QQBot已启动，请用其他QQ号码向本QQ %s<%d> 发送命令来操作QQBot。%s' % \
            (self.nick, self.qqNum, self.__class__.__dict__.get('helpInfo',''))
        )

        while True:
            try:
                pollResult = self.msgQueue.get(timeout=1)
            except Queue.Empty:
                continue
            else:
                if pollResult is None:
                    sys.exit(1)
                self.onPollComplete(*pollResult)

    def pollForever(self):
        try:
            while True:
                pollResult = self.poll()
                self.msgQueue.put(pollResult)
        finally:
            self.msgQueue.put(None)

    # override this method to build your own QQ-bot.
    def onPollComplete(self, msgType, from_uin, buddy_uin, message):
        argv = message.strip().split()
        argc = len(argv)
        
        if not argv:
            return

        elif argv[0] == '-help' and argc == 1:
            reply = ('欢迎使用QQBot，使用方法：\n'
                     '    -help\n'
                     '    -list buddy|group|discuss\n'
                     '    -send buddy|group|discuss {qq_or_uin} message\n'
                     '    -member group|discuss {qq_or_uin}\n'
                     '    -refetch\n'
                     '    -stop\n')

        elif argv[0] == '-list' and argc == 2:
            reply = getattr(self, argv[1] + 'Str', '')

        elif argv[0] == '-send' and argc >= 4 and argv[2].isdigit() \
                                and argv[1] in ('buddy', 'group', 'discuss'):                    
            qq = int(argv[2])
            if argv[1] == 'buddy':
                uin = self.getBuddyByQQ(qq)['uin']
            elif argv[1] == 'group':
                uin = self.getGroupByQQ(qq)['uin']
            else:
                uin = self.getDiscussByUin(qq)['uin']
            
            if uin == -1:
                reply = ('请检查接收者账号是否有误，若是新加的 好友/群/讨论组 ，'
                         '请先运行 refetch ')
            else:
                self.send(argv[1], uin, ' '.join(argv[3:]))
                reply = '消息发送成功'
        
        elif argv[0] == '-member' and argc == 3 and argv[2].isdigit():
            if argv[1] == 'group':
                reply = self.getGroupByQQ(int(argv[2]))['memberStr']
            elif argv[1] == 'discuss':
                reply = self.getDiscussByUin(int(argv[2]))['memberStr']
            else:
                return
            if not reply:
                reply = ('请检查 群/讨论组 账号是否有误，若是新加的 群/讨论组 ，'
                         '请先运行 refetch ')

        elif argv[0] == '-refetch' and argc == 1:
            self.refetch()
            reply = '重新获取 好友/群/讨论组 成功'

        elif argv[0] == '-stop' and argc == 1:
            INFO('收到 stop 命令，QQBot 即将停止')
            self.send(msgType, from_uin, 'QQBot已关闭')
            INFO('QQBot 正常停止')
            sys.exit(0)

        else:            
            return
        
        self.send(msgType, from_uin, reply)
    
    def stop(self):
        sys.exit(0)

def qHash(x, K):
    N = [0] * 4
    for T in range(len(K)):
        N[T%4] ^= ord(K[T])

    U, V = 'ECOK', [0] * 4
    V[0] = ((x >> 24) & 255) ^ ord(U[0])
    V[1] = ((x >> 16) & 255) ^ ord(U[1])
    V[2] = ((x >>  8) & 255) ^ ord(U[2])
    V[3] = ((x >>  0) & 255) ^ ord(U[3])

    U1 = [0] * 8
    for T in range(8):
        U1[T] = N[T >> 1] if T % 2 == 0 else V[T >> 1]

    N1, V1 = '0123456789ABCDEF', ''
    for aU1 in U1:
        V1 += N1[((aU1 >> 4) & 15)]
        V1 += N1[((aU1 >> 0) & 15)]

    return V1

if __name__ == '__main__':
    main()
