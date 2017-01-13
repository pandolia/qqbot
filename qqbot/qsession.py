#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, random, pickle, time, requests

from qconf import QConf
from qrcodemanager import QrcodeManager
from qcontacts import QContacts
from common import JsonLoads, JsonDumps
from utf8logger import CRITICAL, WARN, INFO, DEBUG, DisableLog, EnableLog

def QLogin(qq=None, user=None, conf=None):
    if conf is None:        
        conf = QConf(qq, user)

    if conf.qq:
        INFO('开始自动登录...')    
        picklePath = conf.PicklePath()
        try:
            with open(picklePath, 'rb') as f:
                session, contacts = pickle.load(f)
        except Exception as e:
            WARN('自动登录失败，原因：%s', e)
        else:
            INFO('成功从文件 "%s" 中恢复登录信息和联系人' % picklePath)
            try:
                session.TestLogin()
            except QSession.Error:
                WARN('自动登录失败，原因：上次保存的登录信息已过期')
            else:
                INFO('登录成功。登录账号：%s(%s)', session.nick, session.qq)
                return session, contacts

    INFO('开始手动登录...')
    session = QSession()
    contacts = session.Login(conf)
    INFO('登录成功。登录账号：%s(%s)', session.nick, session.qq)

    conf.qq = session.qq
    picklePath = conf.PicklePath()
    try:
        with open(picklePath, 'wb') as f:
            pickle.dump((session, contacts), f)
    except IOError:
        WARN('保存登录信息及联系人失败：IOError %s', picklePath)
    else:
        INFO('登录信息及联系人已保存至文件：file://%s' % picklePath)
    
    return session, contacts

class QSession:

    class Error(SystemExit):
        pass

    def Login(self, conf):        
        self.prepareSession()
        self.waitForAuth(conf)
        self.getPtwebqq()
        self.getVfwebqq()
        self.getUinAndPsessionid()
        self.TestLogin()
        return self.Fetch(silence=False)

    def prepareSession(self):
        self.clientid = 53999199
        self.msgId = 6000000
        self.httpsVerify = True
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
    
    def Copy(self):
        c = QSession()
        c.__dict__.update(self.__dict__)
        c.session = pickle.loads(pickle.dumps(c.session))
        return c

    def getQrcode(self):
        INFO('登录 Step1 - 获取二维码')
        return self.urlGet(
            'https://ssl.ptlogin2.qq.com/ptqrshow?appid=501004106&e=0&l=M&' +
            's=5&d=72&v=4&t=' + repr(random.random())
        )

    def waitForAuth(self, conf):
        qrcodeManager = QrcodeManager(conf)
        try:
            qrcodeManager.Show(self.getQrcode())
            while True:
                time.sleep(3)
                authStatus = self.getAuthStatus()
                if '二维码未失效' in authStatus:
                    INFO('登录 Step2 - 等待二维码扫描及授权')
                    qrcodeManager.Show()
                elif '二维码认证中' in authStatus:
                    INFO('二维码已扫描，等待授权')
                elif '二维码已失效' in authStatus:
                    WARN('二维码已失效, 重新获取二维码')
                    qrcodeManager.Show(self.getQrcode())
                elif '登录成功' in authStatus:
                    INFO('已获授权')
                    items = authStatus.split(',')
                    self.nick = str(items[-1].split("'")[1])
                    self.qq = str(int(self.session.cookies['superuin'][1:]))
                    self.urlPtwebqq = items[2].strip().strip("'")
                    break
                else:
                    CRITICAL('获取二维码扫描状态时出错, html="%s"', authStatus)
                    sys.exit(1)
        finally:
            qrcodeManager.Destroy()

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

    def TestLogin(self):
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
                repeateOnDeny = 0
            )
        finally:
            EnableLog()
    
    def Fetch(self, silence=True):
        contacts = QContacts()
        self.fetchBuddies(contacts, silence)
        self.fetchGroups(contacts, silence)
        self.fetchDiscusses(contacts, silence)
        return contacts

    def fetchBuddies(self, contacts, silence=True):
        if not silence:            
            INFO('登录 Step6 - 获取好友列表')
        
        result = self.smartRequest(
            url = 'http://s.web2.qq.com/api/get_user_friends2',
            data = {
                'r': JsonDumps({'vfwebqq':self.vfwebqq, 'hash':self.hash})
            },
            Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001&'
                       'callback=1&id=2')
        )['info']
        
        for info in result:
            uin = str(info['uin'])
            name = str(info['nick'])
            qq = str(self.fetchBuddyQQ(uin))
            contact = contacts.Add('buddy', uin, name, qq)
            if not silence:            
                INFO(repr(contact))
            
        if not silence:
            INFO('获取朋友列表成功，共 %d 个朋友' % len(result))
    
    def fetchBuddyQQ(self, uin):
        return self.smartRequest(
            url = ('http://s.web2.qq.com/api/get_friend_uin2?tuin=%s&'
                   'type=1&vfwebqq=%s&t={rand}') % (uin, self.vfwebqq),
            Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001&'
                       'callback=1&id=2'),
            timeoutRetVal = {'account': ''}
        )['account']

    # def fetchBuddyDetailInfo(self, uin):
    #     return self.smartRequest(
    #         url = ('http://s.web2.qq.com/api/get_friend_info2?tuin=%s&'
    #                'vfwebqq=%s&clientid=%s&psessionid=%s&t={rand}') % \
    #               (uin, self.vfwebqq, self.clientid, self.psessionid),
    #         Referer = ('http://s.web2.qq.com/proxy.html?v=20130916001&'
    #                    'callback=1&id=1')
    #     )

    def fetchGroups(self, contacts, silence=True):
        if not silence:
            INFO('登录 Step7 - 获取群列表')
            INFO('=' * 60)
        
        result = self.smartRequest(
            url = 'http://s.web2.qq.com/api/get_group_name_list_mask2',
            data = {
                'r': JsonDumps({'vfwebqq':self.vfwebqq, 'hash':self.hash})
            },
            Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001&'
                       'callback=1&id=2')
        )['gnamelist']

        for info in result:
            uin = str(info['gid'])
            name = str(info['name'])
            qq = str(self.fetchGroupQQ(uin))
            members = self.fetchGroupMember(info['code'])

            c = contacts.Add('group', uin, name, qq, members)
            
            if not silence:
                INFO(repr(c))
                for uin, name in members.items():
                    INFO('    成员: %s, uin%s', name, uin)
                INFO('=' * 60)

        if not silence:
            INFO('获取群列表成功，共 %d 个群' % len(result))
    
    def fetchGroupQQ(self, uin):
        return self.smartRequest(
            url = ('http://s.web2.qq.com/api/get_friend_uin2?tuin=%s&'
                   'type=4&vfwebqq=%s&t={rand}') % (uin, self.vfwebqq),
            Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001&'
                       'callback=1&id=2'),
            timeoutRetVal = {'account': ''}
        )['account']
    
    def fetchGroupMember(self, gcode):
        ret = self.smartRequest(
            url = ('http://s.web2.qq.com/api/get_group_info_ext2?gcode=%s'
                   '&vfwebqq=%s&t={rand}') % (gcode, self.vfwebqq),
            Referer = ('http://s.web2.qq.com/proxy.html?v=20130916001'
                       '&callback=1&id=1')
        )
        return dict((str(m['muin']), str(inf['nick']))
                    for m, inf in zip(ret['ginfo']['members'], ret['minfo']))

    def fetchDiscusses(self, contacts, silence=True):
        if not silence:
            INFO('登录 Step8 - 获取讨论组列表')
            INFO('=' * 60)

        result = self.smartRequest(
            url = ('http://s.web2.qq.com/api/get_discus_list?clientid=%s&'
                   'psessionid=%s&vfwebqq=%s&t={rand}') % 
                  (self.clientid, self.psessionid, self.vfwebqq),
            Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001'
                       '&callback=1&id=2')
        )['dnamelist']

        for info in result:
            uin = str(info['did'])
            name = str(info['name'])
            members = self.fetchDiscussMember(uin)

            c = contacts.Add('discuss', uin, name, members=members)
            
            if not silence:
                INFO(repr(c))
                for uin, name in members.items():
                    INFO('    成员: %s, uin%s', name, uin)
                INFO('=' * 60)

        if not silence:
            INFO('获取讨论组列表成功，共 %d 个讨论组', len(result))
    
    def fetchDiscussMember(self, uin):
        ret = self.smartRequest(
            url = ('http://d1.web2.qq.com/channel/get_discu_info?'
                   'did=%s&psessionid=%s&vfwebqq=%s&clientid=%s&t={rand}') %
                  (uin, self.psessionid, self.vfwebqq, self.clientid),
            Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001'
                       '&callback=1&id=2')
        )
        return dict((str(m['uin']), str(m['nick'])) for m in ret['mem_info'])

    def Poll(self):
        result = self.smartRequest(
            url = 'https://d1.web2.qq.com/channel/poll2',
            data = {
                'r': JsonDumps({
                    'ptwebqq':self.ptwebqq, 'clientid':self.clientid,
                    'psessionid':self.psessionid, 'key':''
                })
            },
            Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001&'
                       'callback=1&id=2')
        )

        if not result or 'errmsg' in result:
            return 'timeout', '', '', ''
        else:
            result = result[0]
            ctype = {
                'message': 'buddy',
                'group_message': 'group',
                'discu_message': 'discuss'
            }[result['poll_type']]
            fromUin = str(result['value']['from_uin'])
            memberUin = str(result['value'].get('send_uin', ''))
            content = ''.join(
                ('[face%d]' % m[1]) if isinstance(m, list) else str(m)
                for m in result['value']['content'][1:]
            )
            return ctype, fromUin, memberUin, content

    def Send(self, ctype, uin, content):
        self.msgId += 1
        sendUrl = {
            'buddy': 'http://d1.web2.qq.com/channel/send_buddy_msg2',
            'group': 'http://d1.web2.qq.com/channel/send_qun_msg2',
            'discuss': 'http://d1.web2.qq.com/channel/send_discu_msg2'
        }
        sendTag = {'buddy':'to', 'group':'group_uin', 'discuss':'did'}
        self.smartRequest(
            url = sendUrl[ctype],
            data = {
                'r': JsonDumps({
                    sendTag[ctype]: int(uin),
                    'content': JsonDumps([
                        content,
                        ['font', {'name': '宋体', 'size': 10,
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
        if self.msgId % 10 == 0:
            INFO('已连续发送10条消息，强制 sleep 10秒，请等待...')
            time.sleep(10)
        else:
            time.sleep(random.randint(1, 3))

    def urlGet(self, url, **kw):
        time.sleep(0.2)
        self.session.headers.update(kw)
        if self.httpsVerify:
            try:
                return self.session.get(url, verify=True).content
            except (requests.exceptions.SSLError, AttributeError):
                self.httpsVerify = False
        return self.session.get(url, verify=False).content

    def smartRequest(self, url, data=None,
                     timeoutRetVal=None, repeateOnDeny=2, **kw):
        nCE, nTO, nUE, nDE = 0, 0, 0, 0
        while True:
            url = url.format(rand=repr(random.random()))
            html = ''
            errorInfo = ''
            self.session.headers.update(**kw)
            try:
                if data is None:
                    resp = self.session.get(url, verify=self.httpsVerify)
                else:
                    resp = self.session.post(url, data=data,
                                             verify=self.httpsVerify)
            except requests.ConnectionError as e:
                nCE += 1
                errorInfo = '网络错误 %s' % e
            else:
                html = resp.content
                if resp.status_code in (502, 504):
                    self.session.get(
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
                        if retcode in (0, 1202, 100003, 100100):
                            return result.get('result', result)
                        else:
                            nDE += 1
                            errorInfo = '请求被拒绝错误'

            # 出现网络错误、超时、 URL 地址错误可以多试几次 
            # 若网络没有问题但 retcode 有误，一般连续 3 次都出错就没必要再试了
            if nCE < 5 and nTO < 20 and nUE < 5 and nDE <= repeateOnDeny:
                DEBUG('第%d次请求“%s”时出现“%s”, html=%s',
                      nCE+nTO+nUE+nDE, url, errorInfo, repr(html))
                time.sleep(0.5)
            else:
                if nTO == 20 and timeoutRetVal:
                    return timeoutRetVal

                CRITICAL('第%d次请求“%s”时出现“%s”，终止 QQBot',
                         nCE+nTO+nUE+nDE, url, errorInfo)
                raise QSession.Error

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
    session, contacts = QLogin(conf=QConf(3497303033))
