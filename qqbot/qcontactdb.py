# -*- coding: utf-8 -*-

import sys, os
p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if p not in sys.path:
    sys.path.insert(0, p)

import collections, time, pickle

from qqbot.common import JsonDumps
from qqbot.utf8logger import INFO, DEBUG, WARN
from qqbot.mainloop import Put, PutTo

TAGS = ('qq=', 'name=', 'nick=', 'mark=', 'card=', 'uin=')
CHSTAGS = ('QQ', '名称', '网名', '备注名', '群名片', 'UIN')
CTYPES = {
    'buddy': '好友', 'group': '群', 'discuss': '讨论组',
    'group-member': '成员', 'discuss-member': '成员'
}

class QContact(object):
    def __init__(self, **kw):
        for tag in TAGS:
            if tag[:-1] not in kw:
                self.__dict__[tag[:-1]] = ''
        self.__dict__.update(kw)
        self.__dict__['shortRepr'] = '%s"%s"' % (CTYPES[self.ctype],self.name)
        self.__dict__['json'] = JsonDumps(self.__dict__, ensure_ascii=False)
    
    def __str__(self):
        return self.shortRepr
    
    def __repr__(self):
        return self.shortRepr

    def __setattr__(self, k, v):
        raise TypeError("readonly attribute")

class QContactTable(object):
    def __init__(self, ctype):
        assert ctype in CTYPES
        self.ctype = ctype
        self.clist = []
        self.cdict = collections.defaultdict(list)
        self.lastUpdateTime = 0    
    
    def IsNull(self):
        return self.lastUpdateTime == 0

    def IsFresh(self):
        return self.lastUpdateTime + 120 >= time.time()

    def Add(self, **kw):
        c = QContact(ctype=self.ctype, **kw)
        self.clist.append(c)
        for tag in TAGS:
            if getattr(c, tag[:-1], ''):
                self.cdict[tag+getattr(c, tag[:-1])].append(c)
        return c

    def Remove(self, c):
        if c in self:
            try:
                self.clist.remove(c)
            except ValueError:
                pass
            for tag in TAGS:
                if getattr(c, tag[:-1], ''):
                    try:                    
                        self.cdict.get(tag+getattr(c, tag[:-1]), []).remove(c)
                    except ValueError:
                        pass
            return c
    
    def SetCard(self, c, card):
        if c in self and c.card != card:
            if c.card:
                self.cdict['card='+c.card].remove(c)
                self.cdict['name='+c.card].remove(c)
            if card:
                self.cdict['card='+card].append(c)
                self.cdict['name='+card].append(c)
                c.__dict__['name'] = card
            else:
                c.__dict__['name'] = c.nick
            c.__dict__['card'] = card

    def List(self, cinfo=None):
        if cinfo is None:
            return self.clist[:]

        for tag in TAGS:
            if cinfo.startswith(tag):
                return self.cdict.get(cinfo, [])[:]

        if cinfo.isdigit():
            return self.cdict.get('qq='+cinfo, [])[:]
        else:
            return self.cdict.get('name='+cinfo, [])[:]

    def __contains__(self, contact):
        return 'uin='+contact.uin in self.cdict
    
    def __iter__(self):
        return self.clist.__iter__()

NullTable = QContactTable('buddy')

def GetCTypeAndOwner(tinfo):
    ctype, owner = tinfo, tinfo
    if ctype in ('buddy', 'group', 'discuss'):
        return ctype, None
    elif isinstance(owner, QContact) and owner.ctype in ('group', 'discuss'):
        return owner.ctype+'-member',  owner
    else:
        DEBUG(tinfo)
        assert False

class QContactDB(object):
    def __init__(self, session, picklePath=None):
        self.session = session
        if picklePath:
            self.picklePath = picklePath
            self.autoSession = session.Copy()
            self.ctables = {
                'buddy': NullTable, # QContactTable('buddy'),
                'group': NullTable, # QContactTable('group'),
                'discuss': NullTable, # QContactTable('discuss'),
                'group-member': {
                    # '234311': QcontactTable('group-member')
                    # ...
                },
                'discuss-member': {
                    # '234311': QcontactTable('discuss-member')
                    # ...
                }
            }
    
    def Dump(self):
        session = self.__dict__.pop('session')
        autoSession = self.__dict__.pop('autoSession')
        picklePath = self.__dict__.pop('picklePath')
        
        try:
            with open(picklePath, 'wb') as f:
                pickle.dump((session.__dict__, self.__dict__), f)
        except Exception as e:
            WARN('保存登录信息失败：%s %s', (e, picklePath))
        else:
            INFO('登录信息已保存至文件：file://%s' % picklePath)
        
        self.session = session
        self.autoSession = autoSession
        self.picklePath = picklePath
    
    def Restore(self, picklePath):
        session = self.session

        with open(picklePath, 'rb') as f:
            session.__dict__, self.__dict__ = pickle.load(f)

        self.session = session
        self.picklePath = picklePath
        self.autoSession = session.Copy()

    def getTable(self, tinfo):
        ctype, owner = GetCTypeAndOwner(tinfo)
        if ctype in ('buddy', 'group', 'discuss'):
            return self.ctables[ctype]
        else:
            return self.ctables[ctype].get(owner.uin, NullTable)
    
    def List(self, tinfo, cinfo=None):
        table = self.getTable(tinfo)
        if table.IsNull():
            table = self.session.FetchTable(tinfo)
            if table and not table.IsNull():
                self.setTable(tinfo, table)
                return table.List(cinfo)
            else:
                return None
        else:
            return table.List(cinfo)

    def Find(self, tinfo, uin, bot=None):
        cl = self.List(tinfo, 'uin='+uin)
        if cl is None:
            return None
        elif not cl:
            return None
            # if tinfo == 'buddy':                
            #     binfo = self.session.FetchNewBuddyInfo(uin)
            #     if binfo:
            #         buddy = self.ctables['buddy'].Add(**binfo)
            #         Put(bot.onNewContact, buddy, None)
            #         return buddy
            #     else:
            #         return None
            # else:
            #     table = self.session.FetchTable(tinfo)
            #     if table:
            #         self.updateTable(tinfo, table, bot)
            #         cl = table.List('uin='+uin)
            #         if cl:
            #             return cl[0]
            #         else:
            #             return None
            #     else:
            #         return None
        else:
            return cl[0]
    
    def setTable(self, tinfo, table):
        ctype, owner = GetCTypeAndOwner(tinfo)
        if ctype in ('buddy', 'group', 'discuss'):
            self.ctables[ctype] = table
            if ctype in ('group', 'discuss'):
                for c in table.List():
                    self.ctables[ctype+'-member'][c.uin] = NullTable
            INFO('已更新 %s 列表', CTYPES[ctype])
        else:
            self.ctables[ctype][owner.uin] = table
            INFO('已更新 %s 的成员列表', owner)
    
    def updateTable(self, tinfo, table, bot):
        oldTable = self.getTable(tinfo)
        if table.lastUpdateTime - oldTable.lastUpdateTime > 3600:
            self.setTable(tinfo, table)
            return
        
        if oldTable.lastUpdateTime >= table.lastUpdateTime:
            return

        ctype, owner = GetCTypeAndOwner(tinfo)
        
        for c in table:
            if c not in oldTable:
                INFO('新增联系人： %s(owner=%s)', c, owner)
                Put(bot.onNewContact, c, owner)
                if c.ctype in ('group', 'discuss'):
                    self.ctables[c.ctype+'-member'][c.uin] = NullTable
        
        for c in oldTable:
            if c not in table:
                INFO('丢失联系人： %s(owner=%s)', c, owner)
                Put(bot.onLostContact, c, owner)
                if ctype in ('group', 'discuss'):
                    self.ctables[ctype+'-member'].pop(c.uin)
        
        if ctype in ('buddy', 'group', 'discuss'):
            self.ctables[ctype] = table
            INFO('已更新 %s 列表', CTYPES[ctype])
        else:
            self.ctables[ctype][owner.uin] = table
            INFO('已更新 %s 的成员列表', owner)
    
    def UpdateForever(self, bot):
        self.autoUpdate(collections.deque(['buddy']), bot)
        
    # dancing with `fetchUpdate`, in main thread
    def autoUpdate(self, tinfoQueue, bot):
        tinfo = tinfoQueue.popleft()

        if tinfo == 'buddy':
            tinfoQueue.append('group')
        elif tinfo == 'group':
            tinfoQueue.append('discuss')
        elif tinfo == 'discuss':
            tinfoQueue.append('member')
        elif tinfo == 'member':
            tinfoQueue.extend(self.ctables['group'].clist)
            tinfoQueue.extend(self.ctables['discuss'].clist)
            tinfoQueue.append('end')
        elif tinfo == 'end':
            self.Dump()
            Put(bot.onFetchComplete)
            tinfoQueue.append('buddy')
        else:
            pass

        needFetch = (tinfo not in ('end', 'member')) and \
                    (not self.getTable(tinfo).IsFresh())
        
        PutTo('auto-fetch',
              self.fetchUpdate, tinfo, needFetch, tinfoQueue, bot)
    
    # dancing with `autoUpdate`, in child thread 'auto-fetch'
    def fetchUpdate(self, tinfo, needFetch, tinfoQueue, bot):
        if needFetch:
            table = self.autoSession.FetchTable(tinfo)
            table and Put(self.updateTable, tinfo, table, bot)

        if tinfo == 'end':
            if bot.conf.fetchInterval < 0:
                INFO('已完成所有联系人资料和资料，不再对联系人列表和资料进行刷新')
                sys.exit(0)
            else:
                time.sleep(bot.conf.fetchInterval)
        else:
             time.sleep(3)
        
        Put(self.autoUpdate, tinfoQueue, bot)
    
    def StrOfList(self, ctype, info1=None, info2=None):
        if ctype in ('buddy', 'group', 'discuss'):
            return self.strOfList(ctype, cinfo=info1)
        elif ctype in ('group-member', 'discuss-member'):
            assert info1
            oinfo, cinfo = info1, info2            
            cl = self.List(ctype[:-7], oinfo)            
            if cl is None:
                return 'QQBot 在向 QQ 服务器请求数据获取联系人资料的过程中发生错误'
            elif not cl:
                return '%s（%s）不存在' % (CTYPES[ctype[:-7]], oinfo)
            else:
                return '\n\n'.join(self.strOfList(owner,cinfo) for owner in cl)
        else:
            DEBUG(ctype)
            assert False
    
    def strOfList(self, tinfo, cinfo=None):
        ctype, owner = GetCTypeAndOwner(tinfo)
        cl = self.List(tinfo, cinfo)
        
        if cl is None:
            return ('错误：QQBot 联系人资料尚未更新完毕(或无法向 QQ 服务器'
                    '获取联系人资料)，请等待 2 ~ 3 分钟后再试')
        
        if cinfo is None:
            cinfoStr = ''
        else:
            cinfoStr = '（"%s"）' % cinfo

        if ctype in ('buddy', 'group', 'discuss'):
            head = '%s列表%s：' % (CTYPES[ctype], cinfoStr)
        else:
            head = '%s 的成员列表%s：' % (owner, cinfoStr)
        
        if not cl:
            return head + '空'
        
        result = [head]
        result.append('=' * 100)
        result.append('\t'.join(('类型',) + CHSTAGS))
        result.append('=' * 100)
        
        for c in cl:
            l = [CTYPES[c.ctype]] + \
                [(getattr(c, tag[:-1], '') or '#') for tag in TAGS]
            result.append('\t'.join(l))

        result.append('=' * 100)

        return '\n'.join(result)

    def DeleteMember(self, group, memb, bot):
        if self.getTable(group).Remove(memb):
            Put(bot.onLostContact, memb, group)

    def SetMemberCard(self, group, memb, card):
        self.getTable(group).SetCard(memb, card)
