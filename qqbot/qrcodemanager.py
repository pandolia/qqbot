# -*- coding: utf-8 -*-

import os, platform, uuid, subprocess, threading, time

from utf8logger import WARN, INFO
from mailagent import MailAgent   

class QrcodeManager:
    def __init__(self, conf):
        qrcodeId = uuid.uuid4().hex
        if conf.mailAccount:
            self.mailAgent = MailAgent(
                conf.mailAccount, conf.mailAuthCode, name='QQBot管理员'
            )
            self.qrcodeMail = {
                'to_addr': conf.mailAccount,
                'html': ('<p>您的 QQBot 正在登录，请尽快用手机 QQ 扫描下面的二维码。'
                         '若您用手机 QQ 客户端打开此邮件，请直接长按二维码后扫码。若二'
                         '维码已过期，请将本邮件设为已读或删除，之后 QQBot 会将最新的'
                         '二维码发送到本邮箱。</p>'
                         '<p>{{png}}</p>'),
                'subject': ('%s[%s]' % ('QQBot二维码', qrcodeId)),
                'to_name': '我'
            }
            self.hasSent = False
        else:
            self.mailAgent = None
            self.qrcodePath = conf.QrcodePath(qrcodeId)

    def Show(self, qrcode):
        if self.mailAgent is None:
            with open(self.qrcodePath, 'wb') as f:
                f.write(qrcode)
            try:
                showImage(self.qrcodePath)
            except Exception as e:
                WARN('弹出二维码失败 %s，请手动打开 file://%s', e, self.qrcodePath)
        else:
            if not self.hasSent:
                needSend = True
                self.hasSent = True
            else:
                try:
                    with self.mailAgent.IMAP() as imap:
                        last_subject = imap.getUnSeenSubject(-1)[0]
                except Exception as e:
                    WARN('查询 %s 中的邮件失败 %s', self.mailAgent.account, e)
                    needSend = True
                else:
                    needSend = (last_subject != self.qrcodeMail['subject'])
            
            if needSend:                    
                try:
                    with self.mailAgent.SMTP() as smtp:
                        smtp.send(png_content=qrcode, **self.qrcodeMail)
                except Exception as e:
                    WARN('无法将二维码发送至邮箱%s(%s)', self.mailAgent.account, e)
                else:
                    INFO('已将二维码发送至邮箱%s', self.mailAgent.account)
    
    def Clear(self):
        self.hasSent = False
        if not self.mailAgent:
            try:
                os.remove(self.qrcodePath)
            except OSError:
                pass
        else:
            t = threading.Thread(target=self.delMail)
            t.daemon = True
            t.start()
            
    def delMail(self):
        try:
            time.sleep(1)
            with self.mailAgent.IMAP() as imap:
                imap.delMail(subject=self.qrcodeMail['subject'])
        except Exception as e:
            WARN('删除二维码邮件失败 %s', e)

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
    # 需要先在 ~/.qqbot-tmp/v1.9.6.conf 文件中设置好邮箱帐号和授权码
    conf = QQBotConf(user='x', version='v1.9.6')
    qrm = QrcodeManager(conf)
    with open('tmp.png', 'rb') as f:
        qrcode = f.read()
    qrm.Show(qrcode)
    time.sleep(5)
    qrm.Show(qrcode)
    qrm.Clear()
