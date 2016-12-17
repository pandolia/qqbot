# -*- coding: utf-8 -*-

import os, platform, uuid, subprocess

from utf8logger import WARN, INFO
from qrcodeserver import QrcodeServer
from mailagent import MailAgent   

class QrcodeManager:
    def __init__(self, conf):
        qrcodeId = uuid.uuid4().hex
        self.qrcodePath = conf.QrcodePath(qrcodeId)
        if conf.httpServerName:
            self.qrcodeServer = QrcodeServer(conf.httpServerName,
                                             conf.httpServerPort,
                                             conf.tmpDir)
            self.qrcodeURL = self.qrcodeServer.QrcodeURL(qrcodeId)
        else:
            self.qrcodeServer = None        

        if conf.mailAccount:
            self.mailAgent = MailAgent(conf.mailAccount,
                                       conf.mailAuthCode,
                                       name='QQBot管理员')
            if self.qrcodeServer:
                html = ('<p>您的 QQBot 正在登录，请尽快用手机 QQ 扫描下面的二维码。'
                        '若您用手机 QQ 客户端打开此邮件，请直接长按二维码后扫码。'
                        '若二维码已过期，请重新打开本邮件。若您看不到二维码图片，请确保'
                        '图片地址 <a href="{0}">{0}</a> 可以通过公网访问。</p>'
                        '<p><img src="{0}"></p>').format(self.qrcodeURL)
            else:
                html = ('<p>您的 QQBot 正在登录，请尽快用手机 QQ 扫描下面的二维码。'
                        '若您用手机 QQ 客户端打开此邮件，请直接长按二维码后扫码。'
                        '若二维码已过期，请将本邮件删除，删除后 QQBot 会在几分钟后将'
                        '最新的二维码发送到本邮箱。</p>'
                        '<p>{{png}}</p>')
            self.qrcodeMail = {
                'to_addr': conf.mailAccount,
                'html': html,
                'subject': ('%s[%s]' % ('QQBot二维码', qrcodeId)),
                'png_content': '',
                'to_name': '我'
            }
            self.hasSent = False
        else:
            self.mailAgent = None

    def Show(self, qrcode):
        with open(self.qrcodePath, 'wb') as f:
            f.write(qrcode)

        if self.qrcodeServer is None and self.mailAgent is None:
            try:
                showImage(self.qrcodePath)
            except Exception as e:
                WARN('弹出二维码失败(%s)，请手动打开 file://%s', e, self.qrcodePath)
        
        if self.qrcodeServer:
            INFO('请使用浏览器访问二维码，图片地址： %s', self.qrcodeURL)
        
        if self.mailAgent:
            if not self.hasSent:
                needSend = True
                self.hasSent = True
            elif self.qrcodeServer:
                needSend = False
            else:
                try:
                    with self.mailAgent.IMAP() as imap:
                        last_subject = imap.getSubject(-1)
                except Exception as e:
                    WARN('查询 %s 中的邮件失败(%s)', self.mailAgent.account, e)
                    needSend = True
                else:
                    needSend = (last_subject != self.qrcodeMail['subject'])
                    if not needSend:
                        INFO('最近发送的二维码邮件尚未被删除，因此不再重复发送')
            
            if needSend:
                if not self.qrcodeServer:
                    self.qrcodeMail['png_content'] = qrcode
                try:
                    with self.mailAgent.SMTP() as smtp:
                        smtp.send(**self.qrcodeMail)
                except Exception as e:
                    WARN('无法将二维码发送至邮箱%s(%s)', self.mailAgent.account, e)
                else:
                    INFO('已将二维码发送至邮箱%s', self.mailAgent.account)
    
    def Clear(self):
        self.hasSent = False
        try:
            os.remove(self.qrcodePath)
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
    from qqbotconf import QQBotConf
    import time
    # 需要先在 ~/.qqbot-tmp/qqbot.conf 文件中设置好邮箱帐号和授权码
    conf = QQBotConf()
    qrm = QrcodeManager(conf)
    with open('tmp.png', 'rb') as f:
        qrcode = f.read()
    qrm.Show(qrcode)
    time.sleep(5)
    qrm.Show(qrcode)
    qrm.Destroy()
