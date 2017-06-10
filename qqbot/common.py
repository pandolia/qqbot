# -*- coding: utf-8 -*-

import json, subprocess, threading, sys, platform, os

PY3 = sys.version_info[0] == 3

JsonLoads = PY3 and json.loads or (lambda s: encJson(json.loads(s)))
JsonDumps = json.dumps

_PASS = lambda s: s

if PY3:
    STR2UNICODE = _PASS
    UNICODE2STR = _PASS

    STR2BYTES = lambda s: s.encode('utf8')
    BYTES2STR = lambda s: s.decode('utf8')

    STR2SYSTEMSTR = _PASS
    SYSTEMSTR2STR = _PASS

    SYSTEMSTR2BYTES = STR2BYTES
    BYTES2SYSTEMSTR = BYTES2STR
    
else:
    STR2UNICODE = lambda s: s.decode('utf8')
    UNICODE2STR = lambda s: s.encode('utf8')

    STR2BYTES = _PASS
    BYTES2STR = _PASS
    
    _SYSENCODING = sys.getfilesystemencoding() or 'utf8'
    if _SYSENCODING.lower() in ('utf8', 'utf_8', 'utf-8'):
        STR2SYSTEMSTR = _PASS
        SYSTEMSTR2STR = _PASS
    else:
        STR2SYSTEMSTR = lambda s: s.decode('utf8').encode(_SYSENCODING)
        SYSTEMSTR2STR = lambda s: s.decode(_SYSENCODING).encode('utf8')
    
    BYTES2SYSTEMSTR = STR2SYSTEMSTR
    SYSTEMSTR2BYTES = SYSTEMSTR2STR

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

def isSpace(b):
    return b in [' ', '\t', '\n', '\r', 32, 9, 10, 13]

def Partition(msg):
    if PY3:
        msg = msg.encode('utf8')

    n = 720

    if len(msg) < n:
        f, b = msg, b''
    else:
        for i in range(n-1, n-101, -1):
            if isSpace(msg[i]):
                f, b = msg[:i+1], msg[i+1:]
                break
        else:
            for i in range(n-1, n-301, -1):
                if PY3:
                    x = msg[i]
                else:
                    x = ord(msg[i])
                if (x >> 6) != 2:
                    f, b = msg[:i], msg[i:]
                    break
            else:
                f, b = msg[:n], msg[n:]
    
    if PY3:
        return f.decode('utf8'), b.decode('utf8')
    else:
        return f, b

def HasCommand(procName):
    return subprocess.call(['which', procName], stdout=subprocess.PIPE) == 0

def StartThread(target, *args, **kwargs):
    threading.Thread(target=target, args=args, kwargs=kwargs).start()

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
            line = BYTES2SYSTEMSTR(line.strip())
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
                sys.stdout.write('\n')

if not PY3:
    import HTMLParser; htmlUnescape = HTMLParser.HTMLParser().unescape
    def HTMLUnescape(s):
        return htmlUnescape(s.decode('utf8')).replace(u'\xa0', u' ').encode('utf8')
else:
    import html.parser; htmlUnescape = html.parser.HTMLParser().unescape
    def HTMLUnescape(s):
        return htmlUnescape(s).replace('\xa0', ' ')

def IsMainThread():
    return threading.current_thread().name == 'MainThread'

if PY3:
    import importlib
    reload = importlib.reload

# import module / import package.module
# Import('module') / Import('package.module')
def Import(moduleName):
    if moduleName in sys.modules:
        reload(sys.modules[moduleName])
    else:
        __import__(moduleName)
    return sys.modules[moduleName]

if not PY3:
    import urllib
    Unquote = urllib.unquote
else:
    import urllib.parse
    Unquote = urllib.parse.unquote

def mydump(fn, d):
    with open(fn, 'wb') as f:
        json.dump(d, f, ensure_ascii=False, indent=4)

if PY3:
    def UniIter(s):
        return zip(map(ord, s), s)
else:
    # s: utf8 byte-string
    def UniIter(s):
        if not s:
            return
        
        x, uchar = ord(s[0]), s[0]
        for ch in s[1:]:
            c = ord(ch)
            if c >> 6 == 0b10:
                x = (x << 6) | (c & 0b111111)
                uchar += ch
            else:
                yield x, uchar
                uchar = ch
                if c >> 7 == 0:
                    x = c
                elif c >> 5 == 0b110:
                    x = c & 0b11111
                elif c >> 4 == 0b1110:
                    x = c & 0b1111
                elif c >> 3 == 0b11110:
                    x = c & 0b111
                else:
                    raise Exception('illegal utf8 string')
        yield x, uchar

# http://pydev.blogspot.com/2013/01/python-get-parent-process-id-pid-in.html
# Python: get parent process id (pid) in windows
# Below is code to monkey-patch the os module to provide a getppid() function
# to get the parent process id in windows using ctypes (note that on Python 3.2,
# os.getppid() already works and is available on windows, but if you're on an
# older version, this can be used as a workaround).
import os

if not hasattr(os, 'getppid'):
    import ctypes

    TH32CS_SNAPPROCESS = long(0x02) if not PY3 else int(0x02)
    CreateToolhelp32Snapshot = ctypes.windll.kernel32.CreateToolhelp32Snapshot
    GetCurrentProcessId = ctypes.windll.kernel32.GetCurrentProcessId

    MAX_PATH = 260

    _kernel32dll = ctypes.windll.Kernel32
    CloseHandle = _kernel32dll.CloseHandle

    class PROCESSENTRY32(ctypes.Structure):
        _fields_ = [
            ("dwSize", ctypes.c_ulong),
            ("cntUsage", ctypes.c_ulong),
            ("th32ProcessID", ctypes.c_ulong),
            ("th32DefaultHeapID", ctypes.c_int),
            ("th32ModuleID", ctypes.c_ulong),
            ("cntThreads", ctypes.c_ulong),
            ("th32ParentProcessID", ctypes.c_ulong),
            ("pcPriClassBase", ctypes.c_long),
            ("dwFlags", ctypes.c_ulong),

            ("szExeFile", ctypes.c_wchar * MAX_PATH)
        ]

    Process32First = _kernel32dll.Process32FirstW
    Process32Next = _kernel32dll.Process32NextW

    def getppid():
        '''
        :return: The pid of the parent of this process.
        '''
        pe = PROCESSENTRY32()
        pe.dwSize = ctypes.sizeof(PROCESSENTRY32)
        mypid = GetCurrentProcessId()
        snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)

        result = 0
        try:
            have_record = Process32First(snapshot, ctypes.byref(pe))

            while have_record:
                if mypid == pe.th32ProcessID:
                    result = pe.th32ParentProcessID
                    break

                have_record = Process32Next(snapshot, ctypes.byref(pe))

        finally:
            CloseHandle(snapshot)

        return result

    os.getppid = getppid
