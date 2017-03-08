# -*- coding: utf-8 -*-

import sys, os
p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if p not in sys.path:
    sys.path.insert(0, p)

from collections import defaultdict

from qqbot.utf8logger import INFO
from qqbot.messagefactory import Message

CTYPES = ('buddy', 'group', 'discuss')
CHSTYPES = ('好友', '群', '讨论组')
TAGS = ('name=', 'qq=', 'uin=', 'nick=', 'mark=')

class QContact(object):
    def __init__(self, ctype, uin, name, qq='', mark='', nick='',
                 members={}, gcode=''):
        if ctype not in CTYPES:
            raise ValueError('Ilegal contact type: %s' % ctype)
    
        self.ctype = ctype
        self.uin = uin
        self.name = name
        self.qq = qq
        self.mark = mark
        self.nick = nick
        self.members = members
        self.gcode = gcode
        
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

class BuddyList(QContactList):
    pass

class GroupList(QContactList):
    pass

class DiscussList(QContactList):
    pass

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
    
    def SetBuddies(self, buddies, bot):
        if bot is None:            
            self.buddyList = buddies
            INFO('已更新好友列表')
            return

        newBuddies, lostBuddies = [], []

        for b in buddies:
            bl = self.buddyList.Get(uin=b.uin)
            if not bl:
                newBuddies.append(b)                
            # else:
            #    b.detail = bl[0].detail
        
        for b in self.buddyList:
            bl = buddies.Get(uin=b.uin)
            if not bl:
                lostBuddies.append(b)
                
        self.buddyList = buddies
        INFO('已更新好友列表')
        
        for b in newBuddies:
            bot.Process(Message('new-buddy', buddy=b))
        
        for b in lostBuddies:
            bot.Process(Message('lost-buddy', buddy=b))

    def SetGroups(self, groups, bot):
        if bot is None:
            self.groupList = groups
            INFO('已更新群列表')
            return

        newGroups, lostGroups = [], []

        for g in groups:
            gl = self.groupList.Get(uin=g.uin)
            if not gl:
                newGroups.append(g)                
            else:
                g.members = gl[0].members
        
        for g in self.groupList:
            gl = groups.Get(uin=g.uin)
            if not gl:
                lostGroups.append(g)
                
        self.groupList = groups
        INFO('已更新群列表')
        
        for g in newGroups:
            bot.Process(Message('new-group', group=g))
        
        for g in lostGroups:
            bot.Process(Message('lost-group', group=g))

    def SetDiscusses(self, discusses, bot):
        if bot is None:
            self.discussList = discusses
            INFO('已更新讨论组列表')
            return

        newDiscusses, lostDiscusses = [], []

        for d in discusses:
            dl = self.discussList.Get(uin=d.uin)
            if not dl:
                newDiscusses.append(d)                
            else:
                d.members = dl[0].members
        
        for d in self.discussList:
            dl = discusses.Get(uin=d.uin)
            if not dl:
                lostDiscusses.append(d)
                
        self.discussList = discusses
        INFO('已更新群列表')
        
        for d in newDiscusses:
            bot.Process(Message('new-discuss', discuss=d))
        
        for d in lostDiscusses:
            bot.Process(Message('lost-discuss', discuss=d))

    def SetGroupMembers(self, group, members, bot):
        group.members = members
        INFO('已更新 %s 的成员列表', group)
        return

    def SetDiscussMembers(self, discuss, members, bot):
        discuss.members = members
        INFO('已更新 %s 的成员列表', discuss)

    # def SetBuddyDetailInfo(self, buddy, detail, bot):
    #     buddy.__dict__.update(detail)
    #     INFO('已更新 %s 的详细信息', buddy)
