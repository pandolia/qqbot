# -*- coding: utf-8 -*-

import json, subprocess, threading, sys, platform, os

PY3 = sys.version_info[0] == 3

JsonLoads = PY3 and json.loads or (lambda s: encJson(json.loads(s)))
JsonDumps = json.dumps

def STR2BYTES(s):
    return s.encode('utf8') if PY3 else s

def BYTES2STR(b):
    return b.decode('utf8') if PY3 else b

def BYTE2SYSTEMSTR(b):
    return b.decode('utf8') if PY3 else \
           b.decode('utf8').encode(sys.stdin.encoding)

if not PY3:
    def encJson(obj):
        if hasattr(obj, 'encode'):
            return obj.encode('utf8')
        elif isinstance(obj, list):
            return [encJson(e) for e in obj]
        elif isinstance(obj, dict):
            return dict((encJson(k), encJson(v)) for k,v in obj.items())
        else:
            return obj
    
    def Partition(msg, n):
        if n >= len(msg):
            return msg, ''
        else:
            # All utf8 characters start with '0xxx-xxxx' or '11xx-xxxx'
            while n > 0 and ord(msg[n]) >> 6 == 2:
                n -= 1
            return msg[:n], msg[n:]
else:
    def Partition(msg, n):
        return msg[:n], msg[n:]

#_p = re.compile(r'[0-9]+|[a-zA-Z][a-z]*')
#
#def SplitWords(s):
#    return _p.findall(s)
#
#def MinusSeperate(s):
#    return '-'.join(SplitWords(s)).lower()

def HasCommand(procName):
    return subprocess.call(['which', procName], stdout=subprocess.PIPE) == 0

#def StartThread(target, *args, **kwargs):
#    threading.Thread(target=target, args=args, kwargs=kwargs).start()

def StartDaemonThread(target, *args, **kwargs):
    t = threading.Thread(target=target, args=args, kwargs=kwargs)
    t.daemon = True
    t.start()

class LockedValue(object):
    def __init__(self, initialVal=None):
        self.val = initialVal
        self.lock = threading.Lock()
    
    def setVal(self, val):
        with self.lock:
            self.val = val
    
    def getVal(self):
        with self.lock:
            val = self.val
        return val

# usage: CallInNewConsole(['python', 'qterm.py'])
def CallInNewConsole(args=None):
    args = sys.argv[1:] if args is None else args
    
    if not args:
        return 1

    osName = platform.system()

    if osName == 'Windows':
        return subprocess.call(['start'] + list(args), shell=True)
        
    elif osName == 'Linux':
        cmd = subprocess.list2cmdline(args)
        if HasCommand('mate-terminal'):
            args = ['mate-terminal', '-e', cmd]
        elif HasCommand('gnome-terminal'):
            args = ['gnome-terminal', '-e', cmd]
        elif HasCommand('xterm'):
            args = ['sh', '-c', 'xterm -e %s &' % cmd]
        else:
            return 1
            # args = ['sh', '-c', 'nohup %s >/dev/null 2>&1 &' % cmd]
        return subprocess.call(args, preexec_fn=os.setpgrp)
        
    elif osName == 'Darwin':
        return subprocess.call(['open','-W','-a','Terminal.app'] + list(args))
        
    else:
        return 1
        # return subprocess.Popen(list(args) + ['&'])

if PY3:
    import queue as Queue
else:
    import Queue

class DotDict(object):
    def __init__(self, **kw):
        self.__dict__.update(**kw)

Pass = lambda *arg, **kwargs: None

def LeftTrim(s, head):
    if s.startswith(head):
        return s[:len(head)]
    else:
        return s

def AutoTest():
    with open(sys.argv[1], 'rb') as f:
        for line in f.read().split(b'\n'):
            line = BYTE2SYSTEMSTR(line.strip())
            if not line:
                continue
            elif line.startswith('#'):
                print(line)
            else:
                print('>>> '+line)
                os.system(line)
                sys.stdout.write('\npress enter to continue...')
                if PY3:
                    input()
                else:
                    raw_input()
                print()
