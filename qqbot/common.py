# -*- coding: utf-8 -*-

import json, subprocess, threading, sys

PY3 = sys.version_info[0] == 3

JsonLoads = PY3 and json.loads or (lambda s: encJson(json.loads(s)))
JsonDumps = json.dumps

def STR2BYTES(s):
    return s.encode('utf8') if PY3 else s

def BYTES2STR(b):
    return b.decode('utf8') if PY3 else b

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
    
    def Utf8Partition(msg, n):
        if n >= len(msg):
            return msg, ''
        else:
            # All utf8 characters start with '0xxx-xxxx' or '11xx-xxxx'
            while n > 0 and ord(msg[n]) >> 6 == 2:
                n -= 1
            return msg[:n], msg[n:]
else:
    def Utf8Partition(msg, n):
        return msg[:n], msg[n:]

def HasCommand(procName):
    return subprocess.call(['which', procName], stdout=subprocess.PIPE) == 0

def StartThread(target, *args, **kwargs):
    daemon = kwargs.pop('daemon', False)
    t = threading.Thread(target=target, args=args, kwargs=kwargs)
    t.daemon = daemon
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
