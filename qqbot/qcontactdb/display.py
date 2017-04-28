# -*- coding: utf-8 -*-

import sys, os.path as op
p = op.dirname(op.dirname(op.dirname(op.abspath(__file__))))
if p not in sys.path:
    sys.path.insert(0, p)

from qqbot.qcontactdb.contactdb import rName
from qqbot.qcontactdb.myprettytable import PrettyTable
from qqbot.utf8logger import DEBUG

TAGS = ('qq=', 'name=', 'nick=', 'mark=', 'card=', 'uin=')
CHSTAGS = ('QQ', '名称', '网名', '备注名', '群名片', 'UIN')
CTYPES = {
    'buddy': '好友', 'group': '群', 'discuss': '讨论组',
    'group-member': '成员', 'discuss-member': '成员'
}

EXTAGS = ('role=',)
EXCHSTAGS = ('群内角色',)

class DBDisplayer(object):

    def StrOfList(self, ctype, info1=None, info2=None):
        if ctype in ('buddy', 'group', 'discuss'):
            return self.strOfList(ctype, cinfo=info1)
        elif ctype in ('group-member', 'discuss-member'):
            assert info1
            oinfo, cinfo = info1, info2            
            cl = self.List(ctype[:-7], oinfo)            
            if cl is None:
                return '错误：无法向 QQ 服务器获取联系人资料'
            elif not cl:
                return '错误：%s（%s）不存在' % (CTYPES[ctype[:-7]], oinfo)
            else:
                return '\n\n'.join(self.strOfList(owner,cinfo) for owner in cl)
        else:
            DEBUG(ctype)
            assert False
    
    def strOfList(self, tinfo, cinfo=None):
        cl = self.List(tinfo, cinfo)
        
        if cl is None:
            return '错误：无法向 QQ 服务器获取联系人资料'
        
        if cinfo is None:
            cinfoStr = ''
        else:
            cinfoStr = '（"%s"）' % cinfo

        head = '%s%s：' % (rName(tinfo), cinfoStr)
        
        if not cl:
            return head + '空'

        pt = PrettyTable( ('类型',) + CHSTAGS + EXCHSTAGS )        
        for c in cl:
            pt.addRow(
                [CTYPES[c.ctype]] + \
                [(getattr(c, tag[:-1], '') or '') for tag in (TAGS+EXTAGS)]
            )
        
        return head + '\n' + str(pt)
    
    def ObjOfList(self, ctype, info1=None, info2=None):
        if ctype in ('buddy', 'group', 'discuss'):
            return self.objOfList(ctype, cinfo=info1)
        elif ctype in ('group-member', 'discuss-member'):
            assert info1
            oinfo, cinfo = info1, info2            
            cl = self.List(ctype[:-7], oinfo)
            if cl is None:
                return None, '错误：无法向 QQ 服务器获取联系人资料'
            elif not cl:
                return None, '错误：%s（%s）不存在' % (CTYPES[ctype[:-7]], oinfo)
            else:
                result = []
                for owner in cl:
                    r = self.objOfList(owner, cinfo)
                    result.append({
                        'owner': owner.__dict__,
                        'membs': {'r':r[0], 'e':r[1]}
                    })
                return result, None
        else:
            DEBUG(ctype)
            assert False
    
    def objOfList(self, tinfo, cinfo=None):
        cl = self.List(tinfo, cinfo)        
        if cl is None:
            return None, '错误：无法向 QQ 服务器获取联系人资料'
        else:
            return [c.__dict__ for c in cl], None
