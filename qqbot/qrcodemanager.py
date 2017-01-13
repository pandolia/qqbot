# -*- coding: utf-8 -*-

import os, platform, uuid, subprocess, time, threading

from utf8logger import WARN, INFO
from mailagent import MailAgent   

class QrcodeManager:
    def __init__(self, conf):
        self.qrcode = None
        qrcodeId = uuid.uuid4().hex
        if conf.mailAccount:
            self.mailAgent = MailAgent(
                conf.mailAccount, conf.mailAuthCode, name='QQBot管理员'
            )
            self.qrcodeMail = {
                'to_addr': conf.mailAccount,
                'html': ('<p>您的 QQBot 正在登录，请尽快用手机 QQ 扫描下面的二维码。'
                         '若您用手机 QQ 客户端打开此邮件，请直接长按二维码后扫码。若二'
                         '维码已过期，请将本邮件删除，之后 QQBot 会将最新的二维码发送'
                         '到本邮箱。</p>'
                         '<p>{{png}}</p>'),
                'subject': ('%s[%s]' % ('QQBot二维码', qrcodeId)),
                'to_name': '我'
            }
        else:
            self.mailAgent = None
            self.qrcodePath = conf.QrcodePath(qrcodeId)
    
    def Show(self, qrcode=None):
        if qrcode:
            isFirstShow = self.qrcode is None
            self.qrcode = qrcode
            self.show(isFirstShow)
        elif self.mailAgent and not self.hasSent:
            self.show()

    def show(self, isFirstShow=False):
        if self.mailAgent is None:
            with open(self.qrcodePath, 'wb') as f:
                f.write(self.qrcode)
            try:
                showImage(self.qrcodePath)
            except Exception as e:
                WARN('弹出二维码失败 %s，请手动打开file://%s', e, self.qrcodePath)
        else:
            if isFirstShow:
                needSend = True
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
                        smtp.send(png_content=self.qrcode, **self.qrcodeMail)
                except Exception as e:
                    self.hasSent = False
                    WARN('无法将二维码发送至邮箱%s %s', self.mailAgent.account, e)
                else:
                    self.hasSent = True
                    INFO('已将二维码发送至邮箱%s', self.mailAgent.account)
            else:
                self.hasSent = False
    
    def Destroy(self):
        if not self.mailAgent:
            try:
                os.remove(self.qrcodePath)
            except OSError:
                pass
        else:
            threading.Thread(target=self.delMail).start()
            
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
