# -*- coding: utf-8 -*-

from email.encoders import encode_base64
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from email.header import Header
import smtplib
import poplib
import os

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
        return SERVER_LIB[server_name].get(key, default)
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
        self.SMTP = smtplib.SMTP_SSL if self.use_ssl else smtplib.SMTP
        self.POP3 = poplib.POP3_SSL if self.use_ssl else poplib.POP3
            
    def sendpng(self, to_addr, png_path, subject=''):
        with open(png_path, 'rb') as f:
            png_content = f.read()
        
        filename = os.path.basename(png_path)
        m = MIMEBase('image', 'png', filename=filename)
        m.add_header('Content-Disposition', 'attachment', filename=filename)
        m.add_header('Content-ID', '<0>')
        m.add_header('X-Attachment-Id', '0')
        m.set_payload(png_content)
        encode_base64(m)
        
        msg = MIMEMultipart()
        subject = (subject or filename).decode('utf-8')
        html = '<html><body><p><img src="cid:0"</p></body></html>'
        msg['From'] = format_addr(self.name.decode('utf-8'))
        msg['To'] = format_addr(u'%s <%s>' % (to_addr, to_addr))
        msg['Subject'] = Header(subject, 'utf-8').encode()
        msg.attach(MIMEText(html,'html','utf-8'))
        msg.attach(m)
        
        if self.smtp_port:
            server = self.SMTP(self.smtp, self.smtp_port)
        else:
            server = self.SMTP(self.smtp)
        server.set_debuglevel(0)
        server.login(self.account, self.auth_code)
        server.sendmail(self.account, to_addr, msg.as_string())
        server.quit()
    
    def poplast(self):
        if self.pop3_port:
            server = self.POP3(self.pop3, self.pop3_port)
        else:
            server = self.POP3(self.pop3)
        server.getwelcome()
        server.user(self.account)
        server.pass_(self.auth_code)
        resp, mails, octets = server.list()
        mails and server.dele(len(mails))
        server.quit()

if __name__ == '__main__':
    account = raw_input('Email account: ')
    auth_code = raw_input('Email auth code: ')
    png_path = raw_input('PNG file path: ')
    e = EmailAccount(account, auth_code)
    e.sendpng(account, png_path)
    e.sendpng(account, png_path)
    e.poplast()
    