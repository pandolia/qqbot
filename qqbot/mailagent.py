# -*- coding: utf-8 -*-

import sys, os
p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if p not in sys.path:
    sys.path.insert(0, p)

import smtplib
import imaplib
from email.encoders import encode_base64
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from email.header import Header, decode_header

from qqbot.common import PY3

if not PY3:
    from email import message_from_string
else:
    from email import message_from_bytes

SERVER_LIB = {
    'sample.com': {
        'smtp': 'smtp.sample.com',
        'imap': 'imap.sample.com',
        'smtp_port': 0,
        'imap_port': 0,
        'use_ssl': True
    }
}

if not PY3:
    def format_addr(s):
        name, addr = parseaddr(s.decode('utf8'))
        return formataddr((
            Header(name, 'utf8').encode(),
            addr.encode('utf8') if isinstance(addr, str) else addr
        ))

class MailAgent(object):
    def __init__(self, account, auth_code, name='', **config):
        account_name, server_name = account.split('@')

        self.smtp = 'smtp.' + server_name
        self.imap = 'imap.' + server_name
        self.smtp_port = 0
        self.imap_port = 0
        self.use_ssl = True
        
        self.__dict__.update(SERVER_LIB.get(server_name, {}))
        self.__dict__.update(config)

        self.name = '%s <%s>' % (name or account_name, account)
        self.account = account
        self.auth_code = auth_code
        
        st_SMTP = smtplib.SMTP_SSL if self.use_ssl else smtplib.SMTP
        st_IMAP = imaplib.IMAP4_SSL if self.use_ssl else imaplib.IMAP4

        if self.smtp_port:
            self.st_SMTP = lambda : st_SMTP(self.smtp, self.smtp_port)
        else:
            self.st_SMTP = lambda : st_SMTP(self.smtp)
               
        if self.imap_port:
            self.st_IMAP = lambda : st_IMAP(self.imap, self.imap_port)
        else:
            self.st_IMAP = lambda : st_IMAP(self.imap)
        
        self.SMTP = lambda : SMTP(self)
        self.IMAP = lambda : IMAP(self)
    
class SMTP(object):
    def __init__(self, mail_agent):
        self.name, self.account = mail_agent.name, mail_agent.account
        self.server = mail_agent.st_SMTP()
        try:
            self.server.login(mail_agent.account, mail_agent.auth_code)
        except:
            self.close()
            raise
    
    def close(self):
        try:
            return self.server.quit()
        except:
            pass
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
            
    def send(self, to_addr, html='', subject='', to_name='', png_content=''):
        subject = subject or 'No subject'
        to_name = to_name or to_addr.split('@')[0]
        html = '<html><body>%s</body></html>' % html
        if html:
            html = html.replace('{{png}}', '<img src="cid:0">')

        msg = MIMEMultipart()
        msg.attach(MIMEText(html, 'html', 'utf8'))
        if not PY3:
            msg['From'] = format_addr(self.name)
            msg['To'] = format_addr('%s <%s>' % (to_name, to_addr))
            msg['Subject'] = Header(subject.decode('utf8'), 'utf8').encode()
        else:
            msg['From'] = self.name
            msg['To'] = '%s <%s>' % (to_name, to_addr)
            msg['Subject'] = subject    
        
        if png_content:
            m = MIMEBase('image', 'png', filename='x.png')
            m.add_header('Content-Disposition', 'attachment', filename='x.png')
            m.add_header('Content-ID', '<0>')
            m.add_header('X-Attachment-Id', '0')
            m.set_payload(png_content)
            encode_base64(m)        
            msg.attach(m)
        
        self.server.sendmail(self.account, to_addr, msg.as_string())

class IMAP(object):
    def __init__(self, mail_agent):
        self.name, self.account = mail_agent.name, mail_agent.account
        self.conn = mail_agent.st_IMAP()
        try:
            self.conn.login(mail_agent.account, mail_agent.auth_code)
            self.conn.select('INBOX')
        except:
            self.close()
            raise
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    
    def close(self):
        try:
            return self.conn.close()
        except:
            pass

#    # NOT SUPPORTED by qq mail.    
#    def getSubject(self, i):
#        conn = self.conn
#        id_list = conn.search(None, 'ALL')[1][0].split()
#        try:
#            email_id = id_list[i]
#        except IndexError:
#            return None, -1
#        data = conn.fetch(email_id, 'BODY.PEEK[HEADER.FIELDS (SUBJECT)]')[1]
#        msg = message_from_string(data[0][1])
#        s, encoding = decode_header(msg['Subject'])[0]
#        subject = s.decode(encoding or 'utf-8').encode('utf-8')
#        return subject, email_id

#    # NOT SUPPORTED by qq mail.    
#    def delMail(self, subject):
#        idx = -1
#        while True:
#            sbj, email_id = self.getSubject(idx)
#            if sbj is None or sbj != subject:
#                break
#            else:
#                self.conn.store(email_id, '+FLAGS', '\\Deleted')
#                self.conn.expunge()
#                idx -= 1

#     # NOT SUPPORTED by qq mail.
#     def search_mail(self, subject, from_addr):
#         criteria = '(FROM "%s" SUBJECT "%s")' % (from_addr, subject)
#         return self.conn.search(None, criteria)[1][0].split()

    def getSubject(self, i):
        conn = self.conn
        id_list = conn.search(None, '(UNSEEN)')[1][0].split()
        try:
            email_id = id_list[i]
        except IndexError:
            return None, -1
        data = conn.fetch(email_id, 'BODY.PEEK[HEADER.FIELDS (SUBJECT)]')[1]
        if not PY3:
            msg = message_from_string(data[0][1])
            s, encoding = decode_header(msg['Subject'])[0]
            subject = s.decode(encoding or 'utf-8').encode('utf-8')
        else:
            msg = message_from_bytes(data[0][1])
            s, encoding = decode_header(msg['Subject'])[0]
            subject = s if type(s) is str else s.decode(encoding or 'utf-8')
        return subject

if __name__ == '__main__':
    import time
    from qconf import QConf
    conf = QConf(['-u', 'hcj'])
    ma = MailAgent(conf.mailAccount, conf.mailAuthCode)

    with ma.SMTP() as s:
        s.send(conf.mailAccount, 'hello', 'faf房间多啦')
    print('send ok')
    
    time.sleep(5)
        
    with ma.IMAP() as i:
        subject = i.getSubject(-1)
        print('latest email: '+subject)
    print('recv ok')
        
#    with ma.IMAP() as i:
#        subject = i.getUnSeenSubject(-1)[0]
#        print 'latest email:', subject
#    print 'recv ok'
#    
#    time.sleep(5)
#    
#    with ma.IMAP() as i:
#        i.delMail(subject)
#    print 'del ok'
