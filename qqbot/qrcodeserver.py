# -*- coding: utf-8 -*-

import os, flask, requests, multiprocessing, time, logging

from utf8logger import INFO

class QrcodeServer:
    def __init__(self, name, port, tmpDir):
        self.name, self.port, self.tmpDir = name, int(port), tmpDir
        self._indexHTML = '<html><body>QQBOT-HTTP-SERVER</body></html>'
        self._indexURL = 'http://127.0.0.1:%s/qqbot' % port
        if not self.isRunning():
            proc = multiprocessing.Process(target=self.run)
            proc.daemon = True
            proc.start()
            self.proc, self.procIdent = proc, proc.ident
            time.sleep(0.5)
            INFO('二维码 HTTP 服务器已在子进程中开启')
        else:
            self.procIdent = None
            INFO('二维码 HTTP 服务器正在其他进程中运行')
    
    def run(self):
        logging.getLogger('werkzeug').setLevel(logging.ERROR) # no-flask-info
        app = flask.Flask(__name__)
        app.route('/qqbot')(self.route_index)
        app.route('/qqbot/qrcode/<qrcodeId>')(self.route_qrcode)
        app.run(host='0.0.0.0', port=self.port, debug=False)

    def route_index(self):
        return self._indexHTML

    def route_qrcode(self, qrcodeId):
        if callable(self.tmpDir):
            pngPath = self.tmpDir(qrcodeId)
        else:
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
            return resp.status_code == 200 and resp.content == self._indexHTML
    
    def QrcodeURL(self, qrcodeId):
        return 'http://%s:%d/qqbot/qrcode/%s' % (self.name,self.port,qrcodeId)
    
    def Join(self):
        if self.procIdent:
            for p in multiprocessing.active_children():
                if p.ident == self.procIdent:
                    INFO('二维码服务器正在子进程中运行，请勿关闭本程序')
                    try:
                        self.proc.join()
                    except:
                        pass
                    break

def main():
    from qqbotconf import QQBotConf
    QrcodeServer('localhost', 8080, QQBotConf.QrcodePath).Join()

if __name__ == '__main__':
    main()
