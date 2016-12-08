# -*- coding: utf-8 -*-

import os, flask, requests, multiprocessing, time

class QQBotHTTPServer:
    def __init__(self, name, port, tmpDir):
        self.name, self.port, self.tmpDir = name, int(port), tmpDir
        self._indexHTML = '<html><body>QQBOT-HTTP-SERVER</body></html>'
        self._indexURL = 'http://127.0.0.1:%s/qqbot' % port
    
    def run(self):
        app = flask.Flask(__name__)
        app.route('/qqbot/qrcode/<qrcodeId>')(self.qrcode)
        app.route('/qqbot')(self.index)
        app.run(host='0.0.0.0', port=self.port, debug=False)

    def index(self):
        return self._indexHTML

    def qrcode(self, qrcodeId):
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
        return 'http://%s:%d/qqbot/qrcode/%s' % (self.name, self.port, qrcodeId)
    
    def RunInBackgroud(self):
        if not self.isRunning():
            self.proc = multiprocessing.Process(target=self.run)
            self.proc.start()
            time.sleep(0.5)
        else:            
            self.proc = None
    
    def IsCurrent(self):
        return self.proc and self.proc.is_alive()
    
    def Join(self):
        try:
            self.proc.join()
        except:
            pass
    
    def Terminate(self):
        try:
            self.proc.terminate()
        except:
            pass

if __name__ == '__main__':
    QQBotHTTPServer('localhost', 8080, '.').run()
