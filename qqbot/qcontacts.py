# -*- coding: utf-8 -*-

import sys, os
p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if p not in sys.path:
    sys.path.insert(0, p)

from collections import defaultdict

from qqbot.messagefactory import Message

CTYPES = ('buddy', 'group', 'discuss', 'member')
CHSTYPES = ('好友', '群', '讨论组', '成员')
TAGS = ('name=', 'qq=', 'uin=', 'nick=', 'mark=')

class QContact(object):
    def __init__(self, ctype, uin, name, **kw):
        if ctype not in CTYPES:
            raise ValueError('Ilegal contact type: %s' % ctype)
    
        self.ctype = ctype
        self.uin = uin
        self.name = name
        self.__dict__.update(kw)
        
        if ctype in ('group', 'discuss'):
            self.memberList = MemberList()
        
        chsType = CHSTYPES[CTYPES.index(ctype)]
        self.shortRepr = '%s"%s"' % (chsType, self.name)

        if hasattr(self, 'qq'):
            self.reprString = "%s: %s, qq=%s, uin=%s" % \
                              (chsType, self.name, self.qq, self.uin)
        else:
            self.reprString = "%s: %s, uin=%s" % \
                              (chsType, self.name, self.uin)
    
    def __repr__(self):
        return self.reprString
    
    def __str__(self):
        return self.shortRepr

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
    
    def Remove(self, contact):
        try:
            self.cList.remove(contact)
        except ValueError:
            pass

        for tag in TAGS:
            value = getattr(contact, tag[:-1], '')
            if value:
                try:
                    self.cDict[tag+value].remove(contact)
                except ValueError:
                    pass
    
    def __iter__(self):
        return self.cList.__iter__()
    
    def __len__(self):
        return len(self.cList)

class BuddyList(QContactList):
    pass

class GroupList(QContactList):
    pass

class DiscussList(QContactList):
    pass

class MemberList(QContactList):
    pass

def listCmp(newList, oldList, bot):
    if bot is None:
        return

    for c in newList:
        cl = oldList.Get(uin=c.uin)
        if not cl:
            bot.Put(Message('new-'+c.ctype, contact=c))
        elif c.ctype in ('group', 'discuss'):
            newML, oldML = c.memberList, cl[0].memberList
            if len(newML) and len(oldML):
                listCmp(newML, oldML, bot)
            elif len(newML) == 0:
                c.memberList = oldML
    
    for c in oldList:
        if not newList.Get(uin=c.uin):
            bot.Put(Message('lost-'+c.ctype, contact=c))

class QContactDB(object):
    def __init__(self):
        self.buddyList = BuddyList()
        self.groupList = GroupList()
        self.discussList = DiscussList()
    
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
            return getattr(self, ctype+'List').Get(*args, **kw)
    
    def List(self, ctype):
        return getattr(self, ctype+'List').cList if ctype in CTYPES else []
    
    def SetBuddyList(self, buddyList, bot):
        listCmp(buddyList, self.buddyList, bot)
        self.buddyList = buddyList

    def SetGroupList(self, groupList, bot):
        listCmp(groupList, self.groupList, bot)
        self.groupList = groupList

    def SetDiscussList(self, discussList, bot):
        listCmp(discussList, self.discussList, bot)
        self.discussList = discussList        
