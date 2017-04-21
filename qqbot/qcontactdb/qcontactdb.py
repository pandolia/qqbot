# -*- coding: utf-8 -*-

import sys, os.path as op
p = op.dirname(op.dirname(op.dirname(op.abspath(__file__))))
if p not in sys.path:
    sys.path.insert(0, p)

from qqbot.qcontactdb.contactdb import ContactDB
from qqbot.qcontactdb.display import DBDisplayer
from qqbot.qcontactdb.fetch import Fetch
from qqbot.utf8logger import INFO

import collections, time

class QContactDB(DBDisplayer):
    def __init__(self, session):
        self.session = session.Copy()
        self.db = ContactDB(session.dbname)

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

    def find(self, tinfo, uin):
        cl = self.List(tinfo, 'uin='+uin)
        if cl is None:
            return None
        elif not cl:
            self.Update(tinfo)
            cl = self.List(tinfo, 'uin='+uin)
            if not cl:
                return None
            else:
                return cl[0]
        else:
            return cl[0]
    
    def FindSender(self, ctype, fromUin, membUin, thisQQ):
        contact = self.find(ctype, fromUin)
        member = None
        nameInGroup = None
        
        if contact is None:
            contact = self.db.NullContact(ctype, fromUin)
            if ctype in ('group', 'discuss'):
                member = self.db.NullContact(contact, membUin)
        elif ctype in ('group', 'discuss'):
            member = self.find(contact, membUin)
            if member is None:
                member = self.db.NullContact(contact, membUin)
            if ctype == 'group':
                cl = self.List(contact, thisQQ)
                if cl:
                    nameInGroup = cl[0].name
        
        return contact, member, nameInGroup
