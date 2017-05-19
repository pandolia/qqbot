import socket

class MySocketServer(object):
    def __init__(self, host, port, numListen=1, name=None):
        self.host = host
        self.port = int(port)
        self.numListen = numListen
        self.name = '%s<%s:%s>' % ((name or 'Socket-Server'), host, port)

    def Run(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            self.sock.listen(self.numListen)
        except socket.error as e:
            self.onStartFail(e)
        else:
            self.onStart()
            while True:
                try:
                    sock, addr = self.sock.accept()
                except socket.error as e:
                    self.onAcceptError(e)
                else:
                    self.onAccept(sock, addr)
    
    def onStartFail(self, e):
        print('Failed to start %s. %s' % (self.name, e))
    
    def onStart(self):
        print('%s is started' % self.name)

    def onAcceptError(self, e):
        print('%s encountered accept-error. %s' % (self.name, e))

    def onAccept(self, sock, addr):
        self.onConnect(addr)
        sock.settimeout(5.0)
        try:
            data = sock.recv(8192)
        except socket.error as e:
            self.onRecvError(sock, addr, e)
            sock.close()
        else:
            self.onData(sock, addr, data)
    
    def onConnect(self, addr):
        print('Client<%s:%s> connected' % addr)
    
    def onRecvError(self, sock, addr, e):
        print('Failed to receive data from Client<%s:%s>. %s' % (addr[0], addr[1], e))
    
    def onData(self, sock, addr, data):
        print('Receive from Client<%s:%s>: %s' % (addr[0], addr[1], data))
        try:
            sock.sendall('Hello, ' + data)
        except socket.error as e:
            print('Failed to send data to Client<%s:%s>. e' % (addr[0], addr[1], e))
        finally:
            sock.close()

def Query(host, port, req):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    resp = b''
    try:            
        sock.connect((host, int(port)))
        sock.sendall(req)
        while True:
            data = sock.recv(8096)
            if not data:
                return resp
            else:
                resp += data
    except socket.error:
        return resp
    finally:
        sock.close()

if __name__ == '__main__':
    import sys
    data = ' '.join(sys.argv[1:]).strip()
    if data:
        host, port = '127.0.0.1', 8132
        if data == '-s':
            MySocketServer(host, port).Run()
        else:
            print(Query(host, port, data))
