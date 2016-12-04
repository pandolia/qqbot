# -*- coding: utf-8 -*-

import os, flask, requests, multiprocessing, time

class QQBotHTTPServer:
    def __init__(self, port, tmpDir):
        self.port, self.tmpDir = int(port), tmpDir
        self.indexHTML = '<html><body>QQBOT-HTTP-SERVER</body></html>'
        self.indexURL = 'http://127.0.0.1:%s/qqbot' % port

    def index(self):
        return self.indexHTML

    def qrcode(self, filename):
        pathname = os.path.join(self.tmpDir, filename+'.png')
        if os.path.exists(pathname):
            return flask.send_file(pathname, mimetype='image/png')
        else:
            flask.abort(404)
    
    def run(self):
        app = flask.Flask(__name__)
        app.route('/qqbot/qrcode/<filename>')(self.qrcode)
        app.route('/qqbot')(self.index)
        app.run(host='0.0.0.0', port=self.port, debug=False)
    
    def isRunning(self):
        try:
            resp = requests.get(self.indexURL)
        except requests.ConnectionError:
            return False
        else:
            return resp.status_code == 200 and resp.content == self.indexHTML

    def Run(self):
        if not self.isRunning():
            self.run()
    
    def RunInBackgroud(self):
        if not self.isRunning():
            self.proc = multiprocessing.Process(target=self.run)
            self.proc.start()
            time.sleep(1)
        else:            
            self.proc = None

if __name__ == '__main__':
    tmpDir = os.path.join(os.path.expanduser('~'), '.qqbot-tmp')
    QQBotHTTPServer(8080, tmpDir).Run()
