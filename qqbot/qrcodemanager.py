# -*- coding: utf-8 -*-

import os, platform, uuid, subprocess

from utf8logger import WARN, INFO, DEBUG
from qqbotconf import HTTPServerConf, TmpDir
from httpserver import QQBotHTTPServer
from mailagent import MailAgent

if HTTPServerConf['name']:
    QrcodeServer = QQBotHTTPServer(tmpDir=TmpDir, **HTTPServerConf)
else:
    QrcodeServer = None    

class QrcodeManager:
    def __init__(self, conf):
        qrcodeId = uuid.uuid4().hex
        self.qrcodePath = os.path.join(TmpDir, qrcodeId+'.png')

        if QrcodeServer:
            QrcodeServer.RunInBackgroud()
            self.qrcodeURL = QrcodeServer.QrcodeURL(qrcodeId)

        if conf['mailAccount']:
            account = conf['mailAccount']
            authCode = conf['mailAuthCode']
            self.mailAgent = MailAgent(account, authCode, name='QQBot管理员')
            if QrcodeServer:
                html = ('<p>您的 QQBot 正在登录，请尽快用手机 QQ 扫描下面的二维码。'
                        '若二维码已过期，请重新打开本邮件。若您看不到二维码图片，请确保'
                        '图片地址 <a href="{0}">{0}</a> 可以通过公网访问。</p>'
                        '<p><img src="{0}"></p>').format(self.qrcodeURL)
            else:
                html = ('<p>您的 QQBot 正在登录，请尽快用手机 QQ 扫描下面的二维码。'
                        '若二维码已过期，请将本邮件删除，删除后 QQBot 会在几分钟后将'
                        '最新的二维码发送到本邮箱。</p>'
                        '<p>{{png}}</p>')
            self.qrcodeMail = {
                'to_addr': account,
                'html': html,
                'subject': ('%s[%s]' % ('QQBot二维码', qrcodeId)),
                'png_content': '',
                'to_name': '我'
            }
            self.hasSent = False
        else:
            self.mailAgent = None
        
        self.showedBefore = False

    def Show(self, qrcode):
        with open(self.qrcodePath, 'wb') as f:
            f.write(qrcode)

        if QrcodeServer is None and self.mailAgent is None:
            try:
                showImage(self.qrcodePath)
            except:
                DEBUG('', exc_info=True)
                WARN('自动弹出二维码失败，请手动打开 file://%s', self.qrcodePath)
        
        if QrcodeServer:
            INFO('请使用浏览器访问二维码，图片地址： %s', self.qrcodeURL)
        
        if self.mailAgent:
            if not self.hasSent:
                needSend = True
                self.hasSent = True
            elif QrcodeServer:
                needSend = False
            else:
                try:
                    with self.mailAgent.IMAP() as imap:
                        last_subject = imap.getSubject(-1)
                except:
                    DEBUG('', exc_info=True)
                    WARN('查询 %s 中的邮件失败', self.mailAgent.account)
                    needSend = True
                else:
                    DEBUG('邮箱中最新一封邮件的主题：%s', str(last_subject))
                    needSend = (last_subject != self.qrcodeMail['subject'])
            
            if needSend:
                if not QrcodeServer:
                    self.qrcodeMail['png_content'] = qrcode

                try:
                    with self.mailAgent.SMTP() as smtp:
                        smtp.send(**self.qrcodeMail)
                except:
                    DEBUG('', exc_info=True)
                    WARN('无法将二维码发送至邮箱 %s', self.mailAgent.account)
                else:
                    INFO('已将二维码发送至邮箱 %s', self.mailAgent.account)
    
    def Destroy(self):
        try:
            os.path.remove(self.qrcodePath)
        except OSError:
            pass

# FILENAME must be an utf8 encoding string
def showImage(filename):
    osName = platform.system()
    if osName == 'Windows':
        filename = filename.decode('utf8').encode('cp936')
        retcode = subprocess.call([filename], shell=True)
    elif osName == 'Linux':
        retcode = subprocess.call(['gvfs-open', filename])
    elif osName == 'Darwin':
        retcode = subprocess.call(['open', filename])
    else:
        retcode = 1
    if retcode:
        raise

if __name__ == '__main__':
    from qqbotconf import UserConf
    import time
    conf = UserConf('usrname')
    qrm = QrcodeManager(conf)
    with open('tmp.png', 'rb') as f:
        qrcode = f.read()
    qrm.Show(qrcode)
    time.sleep(5)
    qrm.Show(qrcode)
