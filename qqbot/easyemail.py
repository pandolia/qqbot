# -*- coding: utf-8 -*-

from email.encoders import encode_base64
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from email.header import Header, decode_header
from email import message_from_string
import smtplib
import imaplib

SERVER_LIB = {
    'sample.com': {
        'smtp': 'smtp.sample.com',
        'imap': 'imap.sample.com',
        'smtp_port': 0,
        'imap_port': 0,
        'use_ssl': True
    }
}

def format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((
        Header(name, 'utf-8').encode(),
        addr.encode('utf-8') if isinstance(addr, unicode) else addr
    ))

def run_no_exc(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except:
        pass

def conf_update(default, custom):
    for k, v in custom.items():
        if k in default:
            default[k] = v

class EmailHost:
    def __init__(self, email_account, email_auth_code, name='', **config):
        account_name, server_name = email_account.split('@')

        self.smtp = 'smtp.' + server_name
        self.imap = 'imap.' + server_name
        self.smtp_port = 0
        self.imap_port = 0
        self.use_ssl = True
        
        conf_update(self.__dict__, SERVER_LIB.get(server_name, {}))
        conf_update(self.__dict__, config)

        self.name = '%s <%s>' % (name or account_name, email_account)
        self.account = email_account
        self.auth_code = email_auth_code
        
        SMTP = smtplib.SMTP_SSL if self.use_ssl else smtplib.SMTP
        IMAP = imaplib.IMAP4_SSL if self.use_ssl else imaplib.IMAP4

        if self.smtp_port:
            self.SMTP = lambda : SMTP(self.smtp, self.smtp_port)
        else:
            self.SMTP = lambda : SMTP(self.smtp)
               
        if self.imap_port:
            self.IMAP = lambda : IMAP(self.imap, self.imap_port)
        else:
            self.IMAP = lambda : IMAP(self.imap)
        
        self.openSMTP = lambda : SMTPOpener(self)
        self.openIMAP = lambda : IMAPOpener(self)
    
        self.closeSMTP = lambda : run_no_exc(self.smtp_server.quit)
        self.closeimap = lambda : run_no_exc(self.imap_conn.close)
            
    def send(self, to_addr, html='', subject='', to_name='', png_content=''):
        subject = subject or 'No subject'
        to_name = to_name or to_addr.split('@')[0]
        png_tag = png_content and '<p><img src="cid:0"></p>'
        html = '<html><body>%s%s</body></html>' % (html, png_tag)

        msg = MIMEMultipart()
        msg['From'] = format_addr(self.name.decode('utf-8'))
        msg['To'] = format_addr(u'%s <%s>' % (to_name, to_addr))
        msg['Subject'] = Header(subject.decode('utf-8'), 'utf-8').encode()
        msg.attach(MIMEText(html, 'html', 'utf-8'))
        
        if png_content:
            m = MIMEBase('image', 'png', filename='p0.png')
            m.add_header('Content-Disposition', 'attachment', filename='p0.png')
            m.add_header('Content-ID', '<0>')
            m.add_header('X-Attachment-Id', '0')
            m.set_payload(png_content)
            encode_base64(m)        
            msg.attach(m)
        
        self.smtp_server.sendmail(self.account, to_addr, msg.as_string())
    
    def get_subject(self, i):
        conn = self.imap_conn        
        data = conn.uid.search(None, "ALL")[1]
        id_list = data[0].split()
        try:
            email_id = id_list[i]
        except IndexError:
            return None        
        data = conn.fetch(email_id, 'BODY.PEEK[HEADER.FIELDS (SUBJECT)]')[1]
        msg = message_from_string(data[0][1])
        s, encoding = decode_header(msg['Subject'])[0]
        subject = s.decode(encoding).encode('utf-8')        
        return subject
    
class SMTPOpener:
    def __init__(self, email_host):
        self.__dict__ = email_host.__dict__
        self.smtp_server = self.SMTP()
        try:
            self.smtp_server.login(self.account, self.auth_code)
        except:
            self.closeSMTP()
            raise
    
    def __enter__(self):
        pass
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.closeSMTP()

class IMAPOpener:
    def __init__(self, email_host):
        self.__dict__ = email_host.__dict__
        self.imap_conn = self.IMAP()
        try:
            self.imap_conn.login(self.account, self.auth_code)
            self.imap_conn.select('INBOX')
        except:
            self.closeIMAP()
            raise
    
    def __enter__(self):
        pass
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.closeIMAP()

if __name__ == '__main__':
#    account = raw_input('Email account: ')
#    auth_code = raw_input('Email auth code: ')
#    png_path = raw_input('PNG file path: ')

    e = EmailHost(account, auth_code)
    
#    with open(png_path, 'rb') as f:
#        s = f.read()
    
#    with e.openSMTP():
#        e.send(account, png_content=s)
#        e.send(account, png_content=s)
#    
#    with e.openIMAP():
#        e.poplast()
#        e.poplast()
#        e.poplast()
    