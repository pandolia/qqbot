# -*- coding: utf-8 -*-

import sys, os
p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if p not in sys.path:
    sys.path.insert(0, p)

import sys, logging

from qqbot.common import PY3

def equalUtf8(coding):
    return coding is None or coding.lower() in ('utf8', 'utf-8', 'utf_8')

class CodingWrappedWriter(object):
    def __init__(self, coding, writer):
        self.flush = getattr(writer, 'flush', lambda : None)
        
        wcoding = getattr(writer, 'encoding', None)
        wcoding = 'gb18030' if (wcoding in ('gbk', 'cp936')) else wcoding

        if not equalUtf8(wcoding):
            self._write = lambda s: writer.write(
                s.decode(coding).encode(wcoding, 'ignore')
            )
        else:
            self._write = writer.write
    
    def write(self, s):
        self._write(s)
        self.flush()

if not PY3:
    # utf8Stdout.write("中文") <==> 
    # sys.stdout.write("中文".decode('utf8').encode(sys.stdout.encoding))
    utf8Stdout = CodingWrappedWriter('utf8', sys.stdout)
else:
    # reference http://blog.csdn.net/jim7424994/article/details/22675759
    import io
    if hasattr(sys.stdout, 'buffer') and (not equalUtf8(sys.stdout.encoding)):
        if sys.stdout.encoding in ('gbk', 'cp936'):
            coding = 'gb18030'
        else:
            coding = 'utf-8'
        utf8Stdout = io.TextIOWrapper(sys.stdout.buffer, encoding=coding)
    else:
        utf8Stdout = sys.stdout

def Utf8Logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler(utf8Stdout)
        fmt = '[%(asctime)s] [%(levelname)s] %(message)s'
        datefmt = '%Y-%m-%d %H:%M:%S'
        ch.setFormatter(logging.Formatter(fmt, datefmt))
        logger.addHandler(ch)
    return logger

logging.getLogger("").setLevel(logging.CRITICAL)

utf8Logger = Utf8Logger('Utf8Logger')

def SetLogLevel(level):
    utf8Logger.setLevel(getattr(logging, level.upper()))

def DisableLog():
    utf8Logger.disabled = True

def EnableLog():
    utf8Logger.disabled = False

_thisDict = globals()

for name in ('CRITICAL', 'ERROR', 'WARN', 'INFO', 'DEBUG'):
    _thisDict[name] = getattr(utf8Logger, name.lower())

if PY3:
    RAWINPUT = input
else:
    def RAWINPUT(msg):
        utf8Stdout.write(msg)
        s = raw_input('').rstrip()
        if not equalUtf8(sys.stdin.encoding):
            s = s.decode(sys.stdin.encoding).encode('utf8')
        return s        

def PRINT(s, end='\n'):
    utf8Stdout.write(s+end)
    utf8Stdout.flush()

def test():
    s = RAWINPUT("请输入一串中文：")
    PRINT(s)
    INFO(s)
    CRITICAL(s)

if __name__ == '__main__':
    test()
    