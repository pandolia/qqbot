#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from flask import Flask
from flask import send_file

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello World!"

@app.route("/login")
def login():
    qrcodePath = os.getenv('HOME') + '/.qqbot-tmp/'
    qrs = []
    for f in os.listdir(qrcodePath):
        if f[0:6] == 'qrcode':
            qrs.append(qrcodePath + f)
    return send_file(qrs[(list(os.path.getmtime(x) for x in qrs)).index(max(os.path.getmtime(x) for x in qrs))], mimetype='image/png')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port = os.getenv('QQBOT_SERVER_PORT','8080'), debug=False)
