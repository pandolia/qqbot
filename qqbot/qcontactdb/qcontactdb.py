# -*- coding: utf-8 -*-

import sys, os.path as op
p = op.dirname(op.dirname(op.dirname(op.abspath(__file__))))
if p not in sys.path:
    sys.path.insert(0, p)

from qqbot.qcontactdb.contactdb import ContactDB
from qqbot.qcontactdb.display import DBDisplayer
from qqbot.qcontactdb.fetch import Fetch
from qqbot.utf8logger import INFO
from qqbot.common import SYSTEMSTR2STR

import collections, time, re

class QContactDB(DBDisplayer):
    def __init__(self, session):
        self.session = session.Copy()
        dbname = SYSTEMSTR2STR(session.dbname)
        self.db = ContactDB(dbname)
        INFO('联系人数据库文件：%s', dbname)

    def List(self, tinfo, cinfo=None):
        result = self.db.List(tinfo, cinfo)
        if result is None:
            if not self.Update(tinfo):
                return None
            else:
                return self.db.List(tinfo, cinfo)
        else:
            return result

    def Update(self, tinfo):
        contacts = Fetch(self.session, tinfo)
        if contacts is None:
            return False
        else:
            rname = self.db.Update(tinfo, contacts)
            if rname is None:
                return False
            else:
                from qqbot import _bot; _bot.onUpdate(tinfo)
                INFO('已获取并更新 %s', rname)
                return True
    
    def FirstFetch(self):
        q = collections.deque(['buddy', 'group', 'discuss'])
        while q:
            tinfo = q.popleft()
            if self.Update(tinfo) and tinfo in ('group', 'discuss'):
                cl = self.List(tinfo)
                if cl:
                    q.extend(cl)
            time.sleep(1.0)
        
    sysRegex = re.compile('^(' + ')|('.join([
        r'.+\(\d+\) 被管理员禁言.+',
        r'.+\(\d+\) 被管理员解除禁言',
        r'管理员开启了全员禁言，只有群主和管理员才能发言', 
        r'管理员关闭了全员禁言',
		r'http://buluo\.qq\.com/mobile/detail\.html.+'
    ]) + ')$')

    def find(self, tinfo, uin, thisQQ=None, content=None):
        cl = self.List(tinfo, 'uin='+uin)
        if cl is None:
            return None
        elif not cl:
            if getattr(tinfo, 'ctype', None) == 'group':
                if self.sysRegex.match(content):
                    return 'SYSTEM-MESSAGE'
            
            if not isinstance(tinfo, str):
                if getattr(self, 'selfUin', None) == uin:
                    cl2 = self.List(tinfo, 'uin='+thisQQ)
                    if cl2:
                        return cl2[0]
                    else:
                        return None
            
            if self.Update(tinfo):
                cl = self.List(tinfo, 'uin='+uin)
                if not cl:
                    if not isinstance(tinfo, str):
                        self.selfUin = uin
                        cl2 = self.List(tinfo, 'uin='+thisQQ)
                        if cl2:
                            return cl2[0]
                        else:
                            return None
                    return None
                else:
                    return cl[0]
            else:
                return None
        else:
            return cl[0]
    
    def FindSender(self, ctype, fromUin, membUin, thisQQ, content):
        contact = self.find(ctype, fromUin)
        member = None
        nameInGroup = None
        
        if contact is None:
            contact = self.db.NullContact(ctype, fromUin)
            if ctype in ('group', 'discuss'):
                member = self.db.NullContact(contact, membUin)
        elif ctype in ('group', 'discuss'):
            member = self.find(contact, membUin, thisQQ, content)
            if member is None:
                member = self.db.NullContact(contact, membUin)
            if ctype == 'group':
                cl = self.List(contact, 'uin='+thisQQ)
                if cl:
                    nameInGroup = cl[0].name
        
        return contact, member, nameInGroup
