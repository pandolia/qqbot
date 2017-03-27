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
from qqbot.utf8logger import WARN

def isdigit(s):
    return isinstance(s, str) and s.isdigit()

class GroupManagerSession(object):

    # def GroupInvite(self, groupqq, qqlist):
    #     assert isdigit(groupqq)
    #     assert all(map(isdigit, qqlist))
    #     self.smartRequest(
    #         url = 'http://qun.qq.com/cgi-bin/qun_mgr/add_group_member',
    #         Referer = 'http://qun.qq.com/member.html',
    #         data = {'gc':groupqq,'ul':'|'.join(qqlist),'bkn':str(self.bkn)},
    #         expectedCodes = (0,),
    #         repeatOnDeny = 5
    #     )
    
    def GroupKick(self, groupqq, qqlist, placehold=None):
        assert isdigit(groupqq)
        assert all(map(isdigit, qqlist)) and qqlist
        return map(str, self.smartRequest(
            url='http://qun.qq.com/cgi-bin/qun_mgr/delete_group_member',
            Referer='http://qun.qq.com/member.html',
            data={'gc':groupqq,'ul':'|'.join(qqlist),'flag':0,'bkn':self.bkn},
            expectedCodes=(0,),
            repeatOnDeny=5
        ).get('ul', []))    
    
    def GroupSetAdmin(self, groupqq, qqlist, admin=True):
        assert isdigit(groupqq)
        assert all(map(isdigit, qqlist)) and qqlist
        self.smartRequest(
            url = 'http://qun.qq.com/cgi-bin/qun_mgr/set_group_admin',
            Referer = 'http://qun.qq.com/member.html',
            data = {'gc':groupqq, 'ul':'|'.join(qqlist),
                    'op':int(admin), 'bkn':self.bkn},
            expectedCodes = (0,14),
            repeatOnDeny = 6
        )
        return qqlist

    def GroupShut(self, groupqq, qqlist, t):
        assert isdigit(groupqq)
        assert all(map(isdigit, qqlist)) and qqlist
        assert isinstance(t, int) and t >=60
        shutlist = JsonDumps([{'uin':int(qq), 't':t} for qq in qqlist])
        self.smartRequest(
            url = 'http://qinfo.clt.qq.com/cgi-bin/qun_info/set_group_shutup',
            Referer = 'http://qinfo.clt.qq.com/qinfo_v3/member.html',
            data = {'gc':groupqq, 'bkn':self.bkn, 'shutup_list':shutlist},
            expectedCodes = (0,),
            repeatOnDeny = 5
        )
        return qqlist

    def GroupSetCard(self, groupqq, qqlist, card):
        assert isdigit(groupqq)
        assert all(map(isdigit, qqlist)) and qqlist
        assert isinstance(card, str)
        self.smartRequest(
            url = 'http://qun.qq.com/cgi-bin/qun_mgr/set_group_card',
            Referer = 'http://qun.qq.com/member.html',
            data = {'gc': groupqq, 'bkn': self.bkn, 'u':qqlist[0], 'name':card}
                   if card else {'gc': groupqq, 'bkn': self.bkn, 'u':qqlist[0]}, 
            expectedCodes = (0,),
            repeatOnDeny = 5
        )
        return qqlist

class GroupManager(object):
    
    def membsOperation(self, group, membs, tag, func, exArg):
        if not membs:
            return []

        try:
            kickedQQ = func(group.qq, [m.qq for m in membs], exArg)
        except RequestError:
            errInfo = '错误：' + tag + '失败（远程请求被拒绝）'
            return [errInfo.format(m=str(m)) for m in membs]
        except Exception as e:
            WARN('', exc_info=True)
            errInfo = '错误：' + tag + '失败（' + str(e) + '）'
            return [errInfo.format(m=str(m)) for m in membs]
        else:
            result = []
            okInfo = '成功：' + tag
            errInfo = '错误：' + tag + '失败（权限不够）'
            for m in membs:
                if m.qq in kickedQQ:
                    result.append(okInfo.format(m=str(m)))
                else:
                    result.append(errInfo.format(m=str(m)))
            return result
    
    def GroupKick(self, group, membs):
        result = self.membsOperation(
            group, membs, ('踢除%s[{m}]' % group), self.groupKick, None
        )
        for r,m in zip(result, membs):
            if r.startswith('成功'):
                self.deleteMember(group, m, self)
        return result

    def GroupSetAdmin(self, group, membs, admin=True):
        return self.membsOperation(
            group, membs,
            '%s%s[{m}]为管理员' % ((admin and '设置' or '取消'), group),
            self.groupSetAdmin, admin
        )

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
        for r,m in zip(result, membs):
            if r.startswith('成功'):
                self.setMemberCard(group, m, card)
        return result
