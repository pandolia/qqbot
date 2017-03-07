# -*- coding: utf-8 -*-

import sys, os
p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if p not in sys.path:
    sys.path.insert(0, p)

from collections import defaultdict

from qqbot.utf8logger import INFO

CTYPES = ('buddy', 'group', 'discuss')
CHSTYPES = ('好友', '群', '讨论组')
TAGS = ('name=', 'qq=', 'uin=', 'nick=', 'mark=')

class QContact(object):
    def __init__(self, ctype, uin, name, qq='', mark='', **kwargs):
        if ctype not in CTYPES:
            raise ValueError('Ilegal contact type: %s' % ctype)
    
        self.ctype = ctype
        self.uin = uin
        self.name = name
        self.qq = qq
        self.__dict__.update(kwargs)
        
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
    
    # def GetMemberName(self, memberUin):
    #     return self.members.get(memberUin, '##UNKNOWN')

class QContactList(object):
    def __init__(self):
        self.cList, self.cDict = [], defaultdict(list)
        self.ctype = self.__class__.__name__[:-4].lower()
    
    # get buddy|group|discuss x|uin=x|qq=x|name=x
    # Get('12343')
    # Get('uin=12343')
    # Get(uin=12343)
    def Get(self, *args, **kw):
        if (len(args)+len(kw)) != 1:
            raise TypeError('Wrong argument!')

        if args:
            if not args[0]:
                return []

            cid = str(args[0])
            
            for tag in TAGS:
                if cid.startswith(tag):
                    return self.cDict.get(cid, [])[:]

            result = []                    
            for tag in TAGS:
                for c in self.cDict.get(tag+cid, []):
                    if c not in result:
                        result.append(c)
            return result
        else:
            tag, value = kw.popitem()
            return self.cDict.get(tag+'='+str(value), [])[:]
    
    def Add(self, *args, **kwargs):
        contact = QContact(self.ctype, *args, **kwargs)
        self.cList.append(contact)
        for tag in TAGS:
            value = getattr(contact, tag[:-1], '')
            if value:
                self.cDict[tag+value].append(contact)
        return contact
    
    def __iter__(self):
        return self.cList.__iter__()

class BuddyList(QContactList):
    pass

class GroupList(QContactList):
    pass

class DiscussList(QContactList):
    pass

class QContactDB(object):
    def __init__(self):
        self.buddy = BuddyList()
        self.group = GroupList()
        self.discuss = DiscussList()
    
    # get buddy|group|discuss x|uin=x|qq=x|name=x
    # Get('buddy', '12343')
    # Get('buddy', 'uin=12343')
    # Get('buddy', uin=12343)
    def Get(self, ctype, *args, **kw):
        if (len(args)+len(kw)) != 1:
            raise TypeError('Wrong argument!')        
        elif ctype not in CTYPES:
            return []
        else:            
            return getattr(self, ctype).Get(*args, **kw)
    
    def List(self, ctype):
        return getattr(self, ctype).cList if ctype in CTYPES else []
    
    def SetBuddies(self, buddies):
        self.buddy = buddies
        INFO('已更新好友列表')

    def SetGroups(self, groups):
        self.group = groups
        INFO('已更新群列表')

    def SetDiscusses(self, discusses):
        self.discuss = discusses
        INFO('已更新讨论组列表')

    def SetGroupMembers(self, group, members):
        group.members = members
        INFO('已更新 %s 的成员列表', group)

    def SetDiscussMembers(self, discuss, members):
        discuss.members = members
        INFO('已更新 %s 的成员列表', discuss)

    def SetBuddyDetailInfo(self, buddy, detail):
        buddy.__dict__.update(detail)
        INFO('已更新 %s 的详细信息', buddy)
