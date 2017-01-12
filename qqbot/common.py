# -*- coding: utf-8 -*-

import json, platform, subprocess, os, threading

JsonLoads = lambda s: encJson(json.loads(s))
JsonDumps = json.dumps

class DotDict:
    def __init__(self, **kw):
        self.__dict__.update(kw)
    
    def __repr__(self):
        s = '%s(%s)' % (self.__class__.__name__, self.__dict__)
        return s.decode('string-escape')
    
    def update(self, d):
        self.__dict__.update(d)

def encJson(obj):
    if hasattr(obj, 'encode'):
        return obj.encode('utf8')
    elif isinstance(obj, list):
        return [encJson(e) for e in obj]
    elif isinstance(obj, dict):
        return dict((encJson(k), encJson(v)) for k,v in obj.iteritems())
    else:
        return obj

CutDict = lambda d, keys: dict((k, d.pop(k)) for k in keys if k in d)

def Utf8Partition(msg, n):
    if n >= len(msg):
        return msg, ''
    else:
        # All utf8 characters start with '0xxx-xxxx' or '11xx-xxxx'
        while n > 0 and ord(msg[n]) >> 6 == 2:
            n -= 1
        return msg[:n], msg[n:]

# usage: CallInNewConsole(['python', 'qterm.py'])
def CallInNewConsole(args):
    osName = platform.system()
    if osName == 'Windows':
        return subprocess.call(['start'] + list(args), shell=True)
        
    elif osName == 'Linux':
        cmd = subprocess.list2cmdline(args)
        if hasCommand('mate-terminal'):
            args = ['mate-terminal', '-e', cmd]
        elif hasCommand('gnome-terminal'):
            args = ['gnome-terminal', '-x', cmd]
        elif hasCommand('xterm'):
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

def hasCommand(procName):
    try:
        return procName in subprocess.check_output(['which', procName])
    except subprocess.CalledProcessError:
        return False

def StartDaemonThread(target, *args, **kwargs):
    t = threading.Thread(target=target, args=args, kwargs=kwargs)
    t.daemon = True
    t.start()