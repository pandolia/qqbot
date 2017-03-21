# -*- coding: utf-8 -*-

import sys, os
p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if p not in sys.path:
    sys.path.insert(0, p)
    
import socket, time

from qqbot.utf8logger import INFO, WARN, PRINT
from qqbot.common import PY3, STR2BYTES, BYTES2STR, StartDaemonThread
from qqbot.mainloop import MainLoop, Put

HOST, DEFPORT = '127.0.0.1', 8188

class QTermServer(object):
    def __init__(self, port):
        self.port = port

    def Run(self, onCommand=None):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((HOST, self.port))
            self.sock.listen(5)
        except socket.error as e:
            WARN('无法开启 QQBot term 服务器。%s', e)
            WARN(' qq 命令无法使用')
        else:
            time.sleep(0.1)
            INFO('已在 %s 端口开启 QQBot-Term 服务器，', self.port)
            INFO('QQBot 已启动，请在其他控制台窗口使用 qq 命令来控制 QQBot ，'
                 '示例： qq send buddy jack hello')
            while True:
                try:
                    sock, addr = self.sock.accept()
                except socket.error:
                    WARN('QQBot-Term 服务器出现 accept 错误')
                else:
                    name = 'QTerm客户端"%s:%s"' % addr
                    sock.settimeout(5.0)
                    try:
                        data = sock.recv(1024)
                    except socket.error:
                        sock.close()
                    else:
                        command = BYTES2STR(data)
                        INFO('QTerm 命令：%s', command)
                        Put(onCommand, Client(name, sock), command)
    
    def Test(self):

        def onTermCommand(client, command):
            if command == 'stop':
                client.Reply('QQBot已停止')
                sys.exit(0)
            else:
                client.Reply('Hello, ' + command)

        Put(StartDaemonThread, self.Run, onTermCommand)
        MainLoop()

class Client(object):
    def __init__(self, name, sock):
        self.name = name
        self.sock = sock

    def Reply(self, rep):
        rep = STR2BYTES(str(rep)+'\r\n')
        try:
            self.sock.sendall(rep)
        except socket.error:
            WARN('回复 %s 失败', self.name)
        finally:
            self.sock.close()

def query(port, req):
    resp = b''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:            
        sock.connect((HOST, port))
        sock.sendall(req)
        while True:
            data = sock.recv(8096)
            if not data:
                return resp
            resp += data
    except socket.error:
        return resp
    finally:
        sock.close()

def QTerm():
    try:
        # python qterm.py -s
        # python qterm.py [PORT] [COMMAND]
        if len(sys.argv) == 2 and sys.argv[1] == '-s':
            QTermServer(DEFPORT).Test()
        else:
            if len(sys.argv) >= 2 and sys.argv[1].isdigit():
                port = int(sys.argv[1])
                command = ' '.join(sys.argv[2:]).strip()
            else:
                port = DEFPORT
                command = ' '.join(sys.argv[1:]).strip()
    
            if command:
                if not PY3:
                    command = command.decode(sys.getfilesystemencoding())
                command = command.encode('utf8')
                resp = BYTES2STR(query(port, command))
                if not resp:
                    PRINT('无法连接 QQBot-term 服务器')
                elif not resp.strip():
                    PRINT('QQBot 命令格式错误')
                else:
                    PRINT(resp.strip())

    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    QTerm()
