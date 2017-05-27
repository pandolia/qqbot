# -*- coding: utf-8 -*-

# by @yxwzaxns, @pandolia

import sys, os
p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if p not in sys.path:
    sys.path.insert(0, p)

from qqbot.mysocketserver import MySocketServer
from qqbot.common import STR2BYTES, BYTES2STR, SYSTEMSTR2STR
from qqbot.utf8logger import ERROR

class QrcodeServer(MySocketServer):
    def __init__(self, ip, port, qrcodePath, qrcodeId):
        MySocketServer.__init__(self, ip, port, '二维码 HTTP 服务器')
        self.qrcodePath = qrcodePath
        self.qrcodeURL = 'http://%s:%s/%s' % (ip, port, qrcodeId)

    def response(self, request):
        request = BYTES2STR(request)
        url = None
        if request.startswith('GET /'):
            end = request.find('\r\n')
            if end != -1 and request[:end-3].endswith(' HTTP/'):
                url = request[5:end-9].rstrip('/')
        
        resp = b''
        if (url is not None) and (url != 'favicon.ico'):
            try:
                with open(self.qrcodePath, 'rb') as f:
                    png = f.read()
            except Exception as e:
                ERROR('读取二维码文件 %s 出错：%s', SYSTEMSTR2STR(self.qrcodePath), e)
            else:
                resp = (
                    b'HTTP/1.1 200 OK\r\n' +
                    b'Connection: close\r\n' + 
                    b'Content-Length: ' + STR2BYTES(str(len(png))) + b'\r\n' +
                    b'Content-Type: image/png\r\n\r\n' +
                    png
                )
    
        return resp

if __name__ == '__main__':
    QrcodeServer('127.0.0.1', 8189, os.path.join(p, 'prettytable.png'), 'xxx').Run()
