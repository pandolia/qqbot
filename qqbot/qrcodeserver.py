# -*- coding: utf-8 -*-

# by @yxwzaxns, @pandolia

import sys, os
p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if p not in sys.path:
    sys.path.insert(0, p)

import time

from qqbot.qterm import QTermServer
from qqbot.common import StartDaemonThread, STR2BYTES, SYSTEMSTR2STR
from qqbot.utf8logger import INFO, ERROR

class QrcodeServer(object):
    def __init__(self, ip, port, qrcodePath, qrcodeId):
        self.qrcodePath = qrcodePath
        self.qrcodeURL = 'http://%s:%s/%s' % (ip, port, qrcodeId)
        StartDaemonThread(QTermServer(port, ip).Run, self.onTermCommand)
        time.sleep(0.5)
        INFO('二维码 HTTP 服务器已在子线程中开启')

    def onTermCommand(self, client, command):
        url = None
        if command.startswith('GET /'):
            end = command.find('\r\n')
            if end != -1 and command[:end-3].endswith(' HTTP/'):
                url = command[5:end-9].rstrip('/')
        
        rep = b''
        if (url is not None) and (url != 'favicon.ico'):
            try:
                with open(self.qrcodePath, 'rb') as f:
                    png = f.read()
            except Exception as e:
                ERROR('读取二维码文件 %s 出错：%s', SYSTEMSTR2STR(self.qrcodePath), e)
            else:
                rep = (
                    b'HTTP/1.1 200 OK\r\n' +
                    b'Connection: close\r\n' + 
                    b'Content-Length: ' + STR2BYTES(str(len(png))) + b'\r\n' +
                    b'Content-Type: image/png\r\n\r\n' +
                    png
                )
    
        client.Reply(rep)

if __name__ == '__main__':
    QrcodeServer('127.0.0.1', 8189, p+'\\tmp.png', 'xxx')
    from qqbot.mainloop import MainLoop; MainLoop()
