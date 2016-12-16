# -*- coding: utf-8 -*-

import os, sys, flask, requests, time

from common import CallInNewConsole
from utf8logger import INFO, CRITICAL

class QrcodeServer:
    def __init__(self, name, port, tmpDir, runInBackgroud=True):
        assert type(port) is int or (type(port) is str and port.isdigit())
        assert os.path.isdir(tmpDir)
        self.name, self.port, self.tmpDir = name, int(port), tmpDir
        self._indexHTML = '<html><body>QQBOT-HTTP-SERVER</body></html>'
        self._indexURL = 'http://localhost:%s/qqbot' % port
        if not self.isRunning():
            if runInBackgroud:
                args = 'python', __file__, str(port), tmpDir
                if CallInNewConsole(args):
                    CRITICAL('无法运行命令"%s"，二维码 HTTP 服务器启动失败' % 
                             ' '.join(args))
                    sys.exit(0)
                else:
                    time.sleep(1.0)
                    INFO('已在后台开启二维码 HTTP 服务器')
            else:
                print >>sys.stderr, ' * QQBot\'s QRCODE HTTP server'
                self.run()
        else:
            INFO('二维码 HTTP 服务器正在后台运行')        
    
    def run(self):
        app = flask.Flask(__name__)
        app.route('/qqbot')(self.route_index)
        app.route('/qqbot/qrcode/<qrcodeId>')(self.route_qrcode)
        app.run(host='0.0.0.0', port=self.port, debug=False)

    def route_index(self):
        return self._indexHTML
    
    # @app.route('/qqbot/qrcode/<qrcodeId>')
    def route_qrcode(self, qrcodeId):
        pngPath = os.path.join(self.tmpDir, qrcodeId+'.png')
        if os.path.exists(pngPath):
            return flask.send_file(pngPath, mimetype='image/png')
        else:
            flask.abort(404)
    
    def isRunning(self):
        try:
            resp = requests.get(self._indexURL)
        except requests.ConnectionError:
            return False
        else:
            return resp.status_code==200 and resp.content==self._indexHTML
    
    def QrcodeURL(self, qrcodeId):
        return 'http://%s:%d/qqbot/qrcode/%s' % (self.name,self.port,qrcodeId)

def main():
    # usage: python qrcodeserver.py 8080 . [-b]
    QrcodeServer('localhost', sys.argv[1], sys.argv[2], sys.argv[-1]=='-b')

if __name__ == '__main__':
    main()
