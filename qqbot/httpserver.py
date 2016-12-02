# -*- coding: utf-8 -*-

import os
import flask

def runHttpServer(host, port, tmpDir):

    def login():
        last, lastfile = 0, ''
        for f in os.listdir(tmpDir):
            if f[0:6] == 'qrcode':
                p = os.path.join(tmpDir, f)
                cur = os.path.getmtime(p)
                if cur > last:
                    last = cur
                    lastfile = p
        return lastfile and flask.send_file(lastfile, mimetype='image/png')

    app = flask.Flask(__name__)
    app.route("/qqbot/login")(login)
    app.run(host=host, port=int(port), debug=False)
