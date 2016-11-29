# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 11:51:42 2016

@author: huang_cj2
"""

from email.encoders import encode_base64
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from email.header import Header
import smtplib

def format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((
        Header(name, 'utf-8').encode(),
        addr.encode('utf-8') if isinstance(addr, unicode) else addr
    ))

from_addr = 'pandolia@163.com'
auth_code = '???'
to_addr = from_addr
smtp_server = 'smtp.163.com'

msg = MIMEMultipart()
msg['From'] = format_addr(u'QQBOT管理员 <%s>' % from_addr)
msg['To'] = format_addr(u'QQBOT管理员 <%s>' % to_addr)
msg['Subject'] = Header(u'QQBOT 二维码登录', 'utf-8').encode()
msg.attach(MIMEText(
    '<html><body><p><img src="cid:0"</p></body></html>', 'html', 'utf-8'
))


with open('C:\\Users\\huang_cj2\\.qqbot-tmp\\qrcode-1479288297.133000.png', 'rb') as f:
    m = MIMEBase('image', 'png', filename='qrcode.png')
    m.add_header('Content-Disposition', 'attachment', filename='qrcode.png')
    m.add_header('Content-ID', '<0>')
    m.add_header('X-Attachment-Id', '0')
    m.set_payload(f.read())
    encode_base64(m)
    msg.attach(m)

server = smtplib.SMTP(smtp_server)
server.starttls()
server.set_debuglevel(1)
server.login(from_addr, auth_code)
server.sendmail(from_addr, to_addr, msg.as_string())
server.quit()


