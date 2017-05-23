# -*- coding: utf-8 -*-

import sys; PY3 = (sys.version_info[0]==3)

class IlegalUtf8(Exception):
    pass

def getfirst(c):    
    if c >> 7 == 0:
        x = c
    elif c >> 5 == 0b110:
        x = c & 0b11111
    elif c >> 4 == 0b1110:
        x = c & 0b1111
    elif c >> 3 == 0b11110:
        x = c & 0b111
    elif c >> 2 == 0b111110:
        x = c & 0b11
    elif c >> 1 == 0b1111110:
        x = c & 0b1
    else:
        raise IlegalUtf8

    return x

if not PY3:
    # s: utf8 bytes string
    def UniIter(s):
        if not s:
            return
        
        x, uchar = getfirst(ord(s[0])), s[0]
        for ch in s[1:]:
            c = ord(ch)
            if c >> 6 == 0b10:
                x = (x << 6) | (c & 0b111111)
                uchar += ch
            else:            
                yield x, uchar
                x, uchar = getfirst(c), ch
        else:
            yield x, uchar
else:
    # s: unicode string
    def UniIter(s):
        for ch in s:
            yield ord(ch), ch

def calWidth(s, maxWidth=20):
    rst, w = [], 0
    try:
        for x, uchar in UniIter(s):
            if 0x20 <= x <= 0x7e:
                w += 1
            elif 0x4e00 <= x <= 0x9fff:
                w += 2
            else:
                w += 1
                uchar = '*'
            rst.append(uchar)
            if w >= maxWidth:
                break
    except IlegalUtf8:
        w += 1
        rst.append('*')

    return w, ''.join(rst)

class PrettyTable:
    def __init__(self, heads, maxWidth=20):
        self.numColumn = len(heads)
        self.maxWidth = maxWidth
        self.W = [-1] * self.numColumn
        self.M = []
        self.addRow(heads)
    
    def addRow(self, row):
        r = []
        for j in range(self.numColumn):
            w, s = calWidth(row[j], self.maxWidth)
            if w > self.W[j]:
                self.W[j] = w
            r.append( (w, s) )
        self.M.append(r)
    
    def __str__(self):
        level = ['+']
        for w in self.W:
            level.append('-'*(w+2))
            level.append('+')
        level = ''.join(level)

        out = [level]

        for row in self.M:
            line = ['|']
            for j in range(self.numColumn):
                w, s = row[j]
                line.append(' ' + s + ' '*(self.W[j]-w) + ' ')
                line.append('|')
            out.append(''.join(line))
            out.append(level)
    
        return '\n'.join(out)
            

#db = ContactDB('C:\\Users\\xxx\\.qqbot-tmp\\2017-04-26-20-56-24-158297369-contact.db')

#d = ['+' + '-'*32 + '+']
#
#def printAttr(c):
#    for at in ('nick', 'mark', 'card', 'role', 'name'):
#        w, s = calWidth(getattr(c, at, ''))
#        if w:
#            d.append('| ' + s + ' '*(30-w) + ' |')
#            d.append(d[-2])
#
#q = collections.deque(['buddy', 'group', 'discuss'])
#while q:
#    tinfo = q.popleft()
#    cl = db.List(tinfo)
#    map(printAttr, cl)
#    if tinfo in ('group', 'discuss'):
#        q.extend(cl)
#
#f = open('tmp.txt', 'wb')
#f.write('\n'.join(d))
#f.close()

if __name__ == '__main__':
    pt = PrettyTable(['city', 'name'])
    pt.addRow(['普通', '防静电啦发'])
    if not PY3:
        print(str(pt).decode('utf8'))
    else:
        print(pt)
