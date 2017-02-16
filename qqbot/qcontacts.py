# -*- coding: utf-8 -*-

from collections import defaultdict

CTYPES = ('buddy', 'group', 'discuss')
CHSTYPES = ('好友', '群', '讨论组')
TAGS = ('name=', 'qq=', 'uin=', 'nick=', 'mark=')

class QContact:
    def __init__(self, ctype, uin, name, qq='', nick='', mark='', members={}):
        if ctype not in CTYPES:
            raise ValueError('Ilegal contact type: %s' % ctype)
    
        self.ctype = ctype
        self.uin = uin
        self.name = name
        self.qq = qq
        self.nick = nick
        self.mark = mark
        self.members = members
        
        chsType = CHSTYPES[CTYPES.index(ctype)]
        self.shortRepr = '%s"%s"' % (chsType, self.name)

        if ctype != 'discuss':
            self.reprString = "%s: %s, qq=%s, uin=%s" % \
                              (chsType, self.name, self.qq, self.uin)
        else:
            self.reprString = "%s: %s, uin=%s" % \
                              (chsType, self.name, self.uin)
    
    def __repr__(self):
        return self.reprString
    
    def __str__(self):
        return self.shortRepr
    
    def GetMemberName(self, memberUin):
        return self.members.get(memberUin, '##UNKNOWN')

class QContacts:
    def __init__(self):
        self.cLists = dict((k, []) for k in CTYPES)
        self.cDicts = dict((k, defaultdict(list)) for k in CTYPES)
    
    # get buddy|group|discuss x|uin=x|qq=x|name=x
    # Get('buddy', '12343')
    # Get('buddy', 'uin=12343')
    # Get('buddy', uin=12343)
    def Get(self, ctype, *args, **kw):
        if (len(args)+len(kw)) != 1:
            raise TypeError('Wrong argument!')
        
        if ctype not in CTYPES:
            return []
            
        cDict = self.cDicts[ctype]
        if args:
            if not args[0]:
                return []

            cid = str(args[0])
            
            for tag in TAGS:
                if cid.startswith(tag):
                    return cDict.get(cid, [])[:]

            result = []                    
            for tag in TAGS:
                for c in cDict.get(tag+cid, []):
                    if c not in result:
                        result.append(c)
            return result
        else:
            tag, value = kw.items()[0]
            return cDict.get(tag+'='+str(value), [])[:]
    
    def Add(self, *args, **kwargs):
        contact = QContact(*args, **kwargs)
        self.cLists[contact.ctype].append(contact)
        cDict = self.cDicts[contact.ctype]
        for tag in TAGS:
            value = getattr(contact, tag[:-1], '')
            if value:
                cDict[tag+value].append(contact)
        return contact
    
    def List(self, ctype):
        return self.cLists.get(ctype, [])
    
    def Assign(self, contacts):
        self.cLists.update(contacts.cLists)
        self.cDicts.update(contacts.cDicts)
        return self
    
    def __iter__(self):
        for ctype in CTYPES:
            for contact in self.cLists[ctype]:
                yield contact
