# -*- coding: utf-8 -*-
"""
Created on Tue Nov 29 21:44:42 2016

@author: huang_cj2
"""

import poplib
# from email.parser import Parser

email = 'pandolia@163.com'
auth_code = '???'
pop3_server = 'pop3.163.com'

server = poplib.POP3(pop3_server)

print server.getwelcome()

server.user(email)
server.pass_(auth_code)

print 'Messages: %s. Size: %s' % server.stat()

resp, mails, octets = server.list()

print mails

index = len(mails)

server.dele(index)

# resp, lines, octets = server.retr(index)

# msg_content = '\r\n'.join(lines)

# msg = Parser().parsestr(msg_content)

server.quit()

