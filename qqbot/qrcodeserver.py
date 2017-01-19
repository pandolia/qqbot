# -*- coding: utf-8 -*-

# by @yxwzaxns, @pandolia

import os, flask, time, logging

from common import StartThread
from utf8logger import INFO

class QrcodeServer:
    def __init__(self, ip, port, tmpDir):
        self.ip = ip
        self.port = int(port)
        self.tmpDir = os.path.abspath(tmpDir)
        self.qrcodeURL = 'http://%s:%s/qqbot/qrcode' % (ip, port)
        
        StartThread(self.run, daemon=True)
        time.sleep(0.5)
        INFO('二维码 HTTP 服务器已在子线程中开启')
    
    def run(self):
        # no-flask-info
        logging.getLogger('werkzeug').setLevel(logging.ERROR)

        app = flask.Flask(__name__)
        app.route('/qqbot/qrcode')(self.route_qrcode)
        app.run(host='0.0.0.0', port=self.port, debug=False)

    def route_qrcode(self):        
        last, lastfile = 0, ''
        for f in os.listdir(self.tmpDir):
            if f.endswith('.png'):
                p = os.path.join(self.tmpDir, f)
                cur = os.path.getmtime(p)
                if cur > last:
                    last = cur
                    lastfile = p 

        if lastfile:
            return flask.send_file(lastfile, mimetype='image/png')
        else:
            flask.abort(404)

if __name__ == '__main__':
    QrcodeServer('127.0.0.1', 8189, '.')
    while True:
        time.sleep(100)
