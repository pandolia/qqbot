# -*- coding: utf-8 -*-

import sqlite3, traceback

TAGS = ('qq=', 'name=', 'nick=', 'mark=', 'card=', 'uin=')

CTYPES = {
    'buddy': '好友', 'group': '群', 'discuss': '讨论组',
    'group-member': '成员', 'discuss-member': '成员'
}

class QContact(object):
    def __init__(self, *fields):
        for k, field in zip(self.fields, fields):
            self.__dict__[k] = field
        self.__dict__['ctype'] = self.__class__.ctype

    def __repr__(self):
        return '%s“%s”' % (self.chs_type, self.name)

    def __setattr__(self, k, v):
        raise TypeError("QContact object is readonly")

class Buddy(QContact):
    columns = '''\
        qq VARCHAR(12),
        uin VARCHAR(12) PRIMARY KEY,
        nick VARCHAR(80),
        mark VARCHAR(80),
        name VARCHAR(80)
    '''

class Group(QContact):
    columns = '''\
        qq VARCHAR(12),
        uin VARCHAR(12) PRIMARY KEY,
        nick VARCHAR(80),
        mark VARCHAR(80),
        name VARCHAR(80),
        gcode VARCHAR(12)
    '''

class Discuss(QContact):
    columns = '''\
        uin VARCHAR(12) PRIMARY KEY,
        name VARCHAR(80)
    '''

class GroupMember(QContact):
    columns = '''\
        qq VARCHAR(12),
        uin VARCHAR(12) PRIMARY KEY,
        nick VARCHAR(80),
        mark VARCHAR(80),
        card  VARCHAR(80),
        name VARCHAR(80),
        join_time INTEGER,
        last_speak_time INTEGER,
        role VARCHAR(12),
        role_id INTEGER,
        is_buddy INTEGER,
        level INTEGER,
        levelname VARCHAR(36),
        point INTEGER
    '''

class DiscussMember(QContact):
    columns = '''\
        qq VARCHAR(12),
        uin VARCHAR(12) PRIMARY KEY,
        name VARCHAR(80)
    '''

contactMaker = {}

for cls in [Buddy, Group, Discuss, GroupMember, DiscussMember]:
    cls.ctype = cls.__name__.lower().replace('member', '-member')
    cls.chs_type = CTYPES[cls.ctype]
    cls.fields = [row.strip().split(None, 1)[0]
                  for row in cls.columns.strip().split('\n')]
    contactMaker[cls.ctype] = cls

def tName(tinfo):
    if tinfo in ('buddy', 'group', 'discuss'):
        return tinfo
    else:
        assert tinfo.uin.isdigit()
        return tinfo.ctype+'_member_'+tinfo.uin

def rName(tinfo):
    if tinfo in ('buddy', 'group', 'discuss'):
        return CTYPES[tinfo]+'列表'
    else:
        return str(tinfo)+'的成员列表'

def tType(tinfo):
    if tinfo in ('buddy', 'group', 'discuss'):
        return tinfo
    else:
        return tinfo.ctype + '-member'

def tMaker(tinfo):
    return contactMaker[tType(tinfo)]

class ContactDB(object):
    def __init__(self, dbname=':memory:'):
        self.conn = sqlite3.connect(dbname)
        self.conn.text_factory = str
        self.cursor = self.conn.cursor()
    
    def Update(self, tinfo, contacts):
        tname, tmaker = tName(tinfo), tMaker(tinfo)
        
        try:
            if self.exist(tname):
                self.cursor.execute("DELETE FROM '%s'" % tname)
            else:
                sql = ("CREATE TABLE '%s' (" % tname) + tmaker.columns + ')'
                self.cursor.execute(sql)
            
            if contacts:
                w = ','.join(['?']*len(tmaker.fields))
                sql = "INSERT INTO '%s' VALUES(%s)" % (tname, w)
                self.cursor.executemany(sql, contacts)
        except:
            self.conn.rollback()
            traceback.print_exc()
            return None
        else:
            self.conn.commit()
            return rName(tinfo)
    
    def List(self, tinfo, cinfo=None):
        tname, tmaker = tName(tinfo), tMaker(tinfo)

        if not self.exist(tname):
            return None
            
        if cinfo is None:
            items = self.selectAll(tname)
        elif cinfo == '':
            items = []
        else:
            like = False
            if cinfo.isdigit():
                column = 'qq'
            else:
                for tag in TAGS:
                    if cinfo.startswith(tag):
                        column = tag[:-1]
                        cinfo = cinfo[len(tag):]
                        break
                    if cinfo.startswith(tag[:-1]+':like:'):
                        column = tag[:-1]
                        cinfo = cinfo[(len(tag)+5):]
                        if not cinfo:
                            return []
                        like = True
                        break
                else:
                    if cinfo.startswith(':like:'):
                        cinfo = cinfo[6:]
                        if not cinfo:
                            return []
                        if cinfo.isdigit():
                            column = 'qq'
                        else:
                            column = 'name'
                        like = True
                    else:
                        column = 'name'
                
            if column not in tmaker.fields:
                return []

            items = self.select(tname, column, cinfo, like)
        
        return [tmaker(*item) for item in items]
    
    def exist(self, tname):
        self.cursor.execute(
            ("SELECT tbl_name FROM sqlite_master "
             "WHERE type='table' AND tbl_name='%s'") % tname
        )
        return bool(self.cursor.fetchall())

    def select(self, tname, column, value, like=False):
        if not like:
            sql = "SELECT * FROM '%s' WHERE %s=?" % (tname, column)
        else:
            value = '%' + value + '%'
            sql = "SELECT * FROM '%s' WHERE %s like ?" % (tname, column)
        self.cursor.execute(sql, (value,))
        return self.cursor.fetchall()

    def selectAll(self, tname):
        self.cursor.execute("SELECT * FROM '%s'" % tname)
        return self.cursor.fetchall()
    
    def Delete(self, tinfo, c):
        tname = tName(tinfo)
        try:
            self.cursor.execute("DELETE FROM '%s' WHERE uin=?" % tname, [c.uin])
        except:
            self.conn.rollback()
            traceback.print_exc()
            return False
        else:
            self.conn.commit()
            return True
    
    def Modify(self, tinfo, c, **kw):
        tname, tmaker = tName(tinfo), tMaker(tinfo)
        colstr, values = [], []

        for column, value in kw.items():
            assert column in tmaker.fields
            colstr.append("%s=?" % column)
            values.append(value)
            c.__dict__[column] = value

        values.append(c.uin)

        sql = "UPDATE '%s' SET %s WHERE uin=?" % (tname, ','.join(colstr))
        try:
            self.cursor.execute(sql, values)
        except:
            self.conn.rollback()
            traceback.print_exc()
            return False
        else:
            self.conn.commit()
            return True

    @classmethod
    def NullContact(cls, tinfo, uin):
        tmaker = tMaker(tinfo)
        fields = []
        for row in tmaker.columns.strip().split('\n'):
            field, ftype = row.strip().split(None, 1)
            if field == 'uin':
                val = uin
            elif field == 'name':
                val = 'uin' + uin
            elif ftype.startswith('VARCHAR'):
                val = '#NULL'
            else:
                val = -1
            fields.append(val)
        return tmaker(*fields)

if __name__ == '__main__':
    db = ContactDB()
    db.Update('buddy', [
        ['qq1', 'uin1', 'nick昵称1', 'mark备注1', 'name名称1'],
        ['qq2', 'uin2', 'nick昵称2', 'mark备注2', 'name名称2']
    ])
    bl = db.List('buddy')
    print((bl, bl[0].__dict__))
    
    print(db.List('buddy', 'nick=nick昵称2'))
    print(db.List('buddy', 'name名称1'))

    db.Update('group', [
        ['123456', 'uin849384', '昵称1', '备注1', '名称1', 'gcode1'],
        ['456789', 'uin823484', '昵称2', '备注2', '名称2', 'gcode2']
    ])
    
    print(db.List('group', '12345'))
    g = db.List('group', '123456')[0]
    
    db.Update(g, [
        ['123456', 'uin849384', '昵称1', '备注1', '名片1', '名称1', 123456, 78944, '成员',
         2, 0, 100, 'tucao', 100],
        ['123456', 'uin845684', '昵称2', '备注2', '名片2', '名称2', 123456, 78944, '成员',
         2, 0, 100, 'tucao', 100]  
    ])
    
    print(db.List(g, 'name:like:名称'))
    print(db.List(g, '123456'))
    print(db.List(g, '名称2'))
    print(db.List(g, ':like:名称'))
    print(db.List(g, ':like:1'))
