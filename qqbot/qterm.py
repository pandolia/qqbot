# -*- coding: utf-8 -*-

import sys, os
p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if p not in sys.path:
    sys.path.insert(0, p)

from qqbot.utf8logger import INFO, ERROR, PRINT
from qqbot.common import BYTES2STR, SYSTEMSTR2BYTES
from qqbot.mysocketserver import MySocketServer, Query
from qqbot.mainloop import Put

HOST, DEFPORT = '127.0.0.1', 8188

class QTermServer(MySocketServer):
    def __init__(self, port, onCommand):
        MySocketServer.__init__(self, HOST, port, 'QQBot-Term 服务器')
        self.response = onCommand
    
    def Run(self):
        if not self.port:
            INFO('QQBot-Term 服务器未开启，qq 命令和 HTTP-API 接口将无法使用')
        else:
            MySocketServer.Run(self)
    
    def onStartFail(self, e):
        ERROR('qq 命令和 HTTP-API 接口将无法使用')

    def onStart(self):
        INFO('请在其他终端使用 qq 命令来控制 QQBot ，示例： qq send buddy jack hello')
    
    def onData(self, sock, addr, data):
        Put(MySocketServer.onData, self, sock, addr, data)

def QTerm():
    # python qterm.py [PORT] [COMMAND]
    if len(sys.argv) >= 2 and sys.argv[1].isdigit():
        port = sys.argv[1]
        command = ' '.join(sys.argv[2:]).strip()
    else:
        port = DEFPORT
        command = ' '.join(sys.argv[1:]).strip()

    if command:
        resp = BYTES2STR(Query(HOST, port, SYSTEMSTR2BYTES(command)))
        if not resp:
            PRINT('无法连接 QQBot-Term 服务器')
        elif not resp.strip():
            PRINT('QQBot 命令格式错误')
        else:
            PRINT(resp.strip())

if __name__ == '__main__':
    QTerm()
