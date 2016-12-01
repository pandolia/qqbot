# -*- coding: utf-8 -*-

account = '???@163.com'
auth_code = '???'
pop3_server = 'pop3.163.com'

import poplib

server = poplib.POP3_SSL(pop3_server)
server.getwelcome()
server.user(account)
server.pass_(auth_code)
resp, mails, octets = server.list()
mails and server.dele(len(mails))
server.quit()
