# -*- coding: utf-8 -*-

import json, subprocess, platform

JsonLoads = lambda s: encJson(json.loads(s))
JsonDumps = json.dumps

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

# usage: CallInNewConsole(['python', 'qrcodeserver.py', '8080', '~/x/dir'])
def CallInNewConsole(args):
    osName = platform.system()

    if osName == 'Windows':
        return subprocess.call(['start'] + list(args), shell=True)

    elif osName == 'Linux':
        cmd = '"' + '" "'.join(args) + '"'

        if hasCommand('mate-terminal'):
            args = ['mate-terminal', '-e', cmd]
        elif hasCommand('gnome-terminal'):
            args = ['gnome-terminal', '-e', cmd]
        elif hasCommand('xterm'):
            args = ['sh', '-c', 'xterm -e %s &' % cmd]
        else:            
            args = ['sh', '-c', 'nohup %s >/dev/null 2>&1 &' % cmd]
        
        return subprocess.call(args)

    else:
        return subprocess.Popen(list(args) + ['&'])

def hasCommand(procName):
    try:
        return procName in subprocess.check_output(['which', procName])
    except subprocess.CalledProcessError:
        return False