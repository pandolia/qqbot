# -*- coding: utf-8 -*-

from email.encoders import encode_base64
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from email.header import Header
import smtplib

from utf8logger import INFO

SERVER_LIB = {
    '163.com': {
        'smtp': 'smtp.163.com', 'pop3': 'pop3.163.com', 'use_ssl': True
    },
    'qq.com': {
        'smtp': 'smtp.qq.com', 'pop3': 'pop.qq.com', 'use_ssl': True
    }
}

def get_conf(server_name, key, kw, default):
    if key in kw:
        return kw[key]
    elif server_name in SERVER_LIB:
        return SERVER_LIB.get(server_name, default)
    else:
        return default


def format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((
        Header(name, 'utf-8').encode(),
        addr.encode('utf-8') if isinstance(addr, unicode) else addr
    ))

class EmailAccount:
    def __init__(self, email_account, email_auth_code, name='', **kw):
        account_name, server_name = email_account.split('@')
        self.name = '%s <%s>' % (name or account_name, email_account)
        self.account = email_account
        self.auth_code = email_auth_code

        self.smtp = get_conf(server_name, 'smtp', kw, 'smtp.'+server_name)
        self.pop3 = get_conf(server_name, 'pop3', kw, 'pop3.'+server_name)
        self.smtp_port = get_conf(server_name, 'smtp_port', kw, 0)
        self.pop3_port = get_conf(server_name, 'pop3_port', kw, 0)
        self.use_ssl = get_conf(server_name, 'use_ssl', kw, False)
        
        INFO('Created email account: %s', self.name)
            
    def sendpng(self, to_addr, png_path, subject):
        try:
            with open(png_path, 'rb') as f:
                png_content = f.read()
        except IOError:
            WARN('')
        
        msg = MIMEMultipart()
        msg['From'] = format_addr(self.name.decode('utf-8'))
        msg['To'] = format_addr(u'%s <%s>' % (to_addr, to_addr))
        msg['Subject'] = Header(subject.decode('utf-8'), 'utf-8').encode()
        msg.attach(MIMEText(
            '<html><body><p><img src="cid:0"</p></body></html>','html','utf-8'
        ))
        
        m = MIMEBase('image', 'png', filename='qrcode.png')
        m.add_header('Content-Disposition', 'attachment', filename='qrcode.png')
        m.add_header('Content-ID', '<0>')
        m.add_header('X-Attachment-Id', '0')
        with open(png_path, 'rb') as f:
            m.set_payload(f.read())
        encode_base64(m)
        msg.attach(m)
        
        SMTP = self.use_ssl and smtplib.SMTP_SSL or smtplib.SMTP
        server = SMTP(self.smtp, self.smtp_port)
        server.set_debuglevel(0)
        server.login(self.account, self.auth_code)
        server.sendmail(self.account, to_addr, msg.as_string())
        server.quit()

        INFO('%s sent png[%s] to %s', self.name, png_path, to_addr)
    
    def poplast(self):
        INFO('%s pop the last emali', self.name)
