# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 21:52:11 2017

@author: huang_cj2
"""


import sys, os
p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if p not in sys.path:
    sys.path.insert(0, p)

from qqbot.common import JsonDumps
from qqbot.basicqsession import RequestError
from qqbot.utf8logger import WARN, INFO, ERROR

def isdigit(s):
    return isinstance(s, str) and s.isdigit()

class GroupManagerSession(object):
    
    def GroupKick(self, groupqq, qqlist, placehold=None):
        r = self.smartRequest(
            url = 'http://qinfo.clt.qq.com/cgi-bin/qun_info/delete_group_member',
            Referer = 'http://qinfo.clt.qq.com/member.html',
            data={'gc': groupqq, 'ul': '|'.join(qqlist), 'bkn': self.bkn},
            expectedCodes=(0,3,11),
            repeatOnDeny=5
        )
        # 新接口不再区分多个用户的踢出状态，多个用户要么全部操作成功，要么全部失败
        return r.get('ec', -1) == 0

    
    def GroupSetAdmin(self, groupqq, qqlist, admin=True):
        # 新接口只支持设置一人，不支持批量操作
        r = self.smartRequest(
            url = 'http://qinfo.clt.qq.com/cgi-bin/qun_info/set_group_admin',
            Referer= 'http://qinfo.clt.qq.com/member.html',
            data = {'src':'qinfo_v2', 'gc':groupqq, 'u':qqlist[0],
                    'op':int(admin), 'bkn':self.bkn},
            expectedCodes = (0, 14),
            repeatOnDeny = 6
        )
        return r.get('ec', -1) == 0

    def GroupShut(self, groupqq, qqlist, t):
        shutlist = JsonDumps([{'uin':int(qq), 't':t} for qq in qqlist])
        self.smartRequest(
            url = 'http://qinfo.clt.qq.com/cgi-bin/qun_info/set_group_shutup',
            Referer = 'http://qinfo.clt.qq.com/qinfo_v3/member.html',
            data = {'gc':groupqq, 'bkn':self.bkn, 'shutup_list':shutlist},
            expectedCodes = (0,),
            repeatOnDeny = 5
        )
        return True

    def GroupSetCard(self, groupqq, qqlist, card):
        self.smartRequest(
            url = 'http://qinfo.clt.qq.com/cgi-bin/qun_info/set_group_card',
            Referer='http://qinfo.clt.qq.com/member.html',
            data = {'gc': groupqq, 'bkn': self.bkn, 'u':qqlist[0], 'name':card}
                   if card else {'gc': groupqq, 'bkn': self.bkn, 'u':qqlist[0]},
            expectedCodes = (0,),
            repeatOnDeny = 5
        )
        return True

class GroupManager(object):
    
    def membsOperation(self, group, membs, tag, func, exArg):
        if not membs:
            return []
        
        err = False
        if group.qq == '#NULL':
            err = True
        
        for m in membs:
            if m.qq == '#NULL':
                err = True
        
        if err:
            return ['错误：群或某个成员的 qq 属性是 "#NULL"'] * len(membs)

        try:
            ok = func(group.qq, [m.qq for m in membs], exArg)
        except RequestError:
            errInfo = '错误：' + tag + '失败（远程请求被拒绝）'
            result = [errInfo.format(m=str(m)) for m in membs]
        except Exception as e:
            WARN('', exc_info=True)
            errInfo = '错误：' + tag + '失败（' + str(e) + '）'
            result = [errInfo.format(m=str(m)) for m in membs]
        else:
            if ok:
                okInfo = '成功：' + tag
                result = [okInfo.format(m=str(m)) for m in membs]
            else:
                errInfo = '错误：' + tag + '失败（权限不够）'
                result = [errInfo.format(m=str(m)) for m in membs]

        for r in result:
            INFO(r) if r.startswith('成功') else ERROR(r)

        return result
    
    def GroupKick(self, group, membs):
        result = self.membsOperation(
            group, membs, ('踢除%s[{m}]' % group), self.groupKick, None
        )
        for r, m in zip(result, membs):
            if r.startswith('成功'):
                self.Delete(group, m)
        return result

    def GroupSetAdmin(self, group, membs, admin=True):
        result = [self.membsOperation(
            group, [memb],
            '%s%s[{m}]为管理员' % ((admin and '设置' or '取消'), group),
            self.groupSetAdmin, admin
        )[0] for memb in membs]
        for r, m in zip(result, membs):
            if r.startswith('成功'):
                if admin:
                    if m.role == '群主':
                        role, role_id = '群主', 0
                    else:
                        role, role_id = '管理员', 1
                else:
                    role, role_id = '普通成员', 2
                self.Modify(group, m, role=role, role_id=role_id)
        return result

    def GroupShut(self, group, membs, t):
        return self.membsOperation(
            group, membs,
            '禁止%s[{m}]发言（%d分钟）' % (group, t/60),
            self.groupShut, t
        )
    
    def GroupSetCard(self, group, membs, card):
        result = [self.membsOperation(
            group, [memb],
            '设置%s[{m}]的群名片（=%s）' % (group, repr(card)),
            self.groupSetCard, card
        )[0] for memb in membs]
        for r, m in zip(result, membs):
            if r.startswith('成功'):
                self.Modify(group, m, card=card, name=(card or m.nick))
        return result
