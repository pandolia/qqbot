# -*- coding: utf-8 -*-

account = '???@163.com'
auth_code = '???'
smtp_server = 'smtp.163.com'

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

msg = MIMEMultipart()
msg['From'] = format_addr(u'QQBOT管理员 <%s>' % account)
msg['To'] = format_addr(u'QQBOT管理员 <%s>' % account)
msg['Subject'] = Header(u'QQBOT 二维码登录', 'utf-8').encode()
msg.attach(MIMEText(
    '<html><body><p><img src="cid:0"</p></body></html>', 'html', 'utf-8'
))


with open('C:\\Users\\xxx\\.qqbot-tmp\\qrcode-1479288297.133000.png', 'rb') as f:
    m = MIMEBase('image', 'png', filename='qrcode.png')
    m.add_header('Content-Disposition', 'attachment', filename='qrcode.png')
    m.add_header('Content-ID', '<0>')
    m.add_header('X-Attachment-Id', '0')
    m.set_payload(f.read())
    encode_base64(m)
    msg.attach(m)

server = smtplib.SMTP_SSL(smtp_server)
server.set_debuglevel(1)
server.login(account, auth_code)
server.sendmail(account, account, msg.as_string())
server.quit()


