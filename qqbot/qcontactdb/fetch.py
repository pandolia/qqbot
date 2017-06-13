# -*- coding: utf-8 -*-

import sys, os.path as op
p = op.dirname(op.dirname(op.dirname(op.abspath(__file__))))
if p not in sys.path:
    sys.path.insert(0, p)

from qqbot.qcontactdb.contactdb import rName, tType

from qqbot.qconf import QConf
from qqbot.utf8logger import WARN, ERROR, INFO
from qqbot.basicqsession import BasicQSession, RequestError
from qqbot.common import JsonDumps, HTMLUnescape, PY3, STR2BYTES, BYTES2STR

import collections, os

def fetchBuddyTable(self):

    result = self.smartRequest(
        url = 'http://s.web2.qq.com/api/get_user_friends2',
        data = {
            'r': JsonDumps({'vfwebqq':self.vfwebqq, 'hash':self.hash})
        },
        Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001&'
                   'callback=1&id=2'),
        expectedKey = 'marknames',
        repeatOnDeny = 4
    )

    markDict = dict((str(d['uin']), str(d['markname']))
                    for d in result['marknames'])
    
    qqResult = self.smartRequest(
        url = 'http://qun.qq.com/cgi-bin/qun_mgr/get_friend_list',
        data = {'bkn': self.bkn},
        Referer = 'http://qun.qq.com/member.html'
    )

    qqDict = collections.defaultdict(list)
    for blist in list(qqResult.values()):
        for d in blist.get('mems', []):
            name = HTMLUnescape(d['name'])
            qqDict[name].append(str(d['uin']))
    
    buddies, unresolved = [], []

    for info in result['info']:
        uin = str(info['uin'])
        nick = str(info['nick'])
        mark = markDict.get(uin, '')        
        name = mark or nick
        qqlist = qqDict.get(name, [])
        if len(qqlist) == 1:
            qq = qqlist[0]
        else:
            qq = '#NULL'
            unresolved.append('好友“%s”(uin=%s)' % (name, uin))
        
        # 各属性的顺序绝对不能变
        buddies.append([qq, uin, nick, mark, name])
    
    if unresolved:
        unresolved.sort()
        WARN('因存在重名或名称中含特殊字符，无法绑定以下好友的真实QQ号，请修改其备'
             '注名，保证备注名的唯一性且不带特殊字符：\n\t%s', '\n\t'.join(unresolved))
    
    return buddies

def getManaulGroupQQDict():
    
    mgQQDict = collections.defaultdict(list)
    
    from qqbot import QQBot; fn = QQBot._bot.conf.absPath('groupqq')

    if not os.path.exists(fn):
        return mgQQDict

    try:
        with open(fn, 'rb') as f:
            s = f.read()
    except Exception as e:
        ERROR('无法读取群 QQ 文件 %s ， %s', fn, e)
        return mgQQDict
    
    try:
        s = BYTES2STR(s)
    except Exception as e:
        ERROR('群 QQ 文件 %s 编码错误， %s', fn, e)
        return mgQQDict    

    try:
        for line in s.split('\n'):
            if not line.startswith('#') and (',' in line):
                qq, nick = line.rstrip('\r').split(',', 1)
                mgQQDict[nick].append(qq)
    except Exception as e:
        ERROR('群 QQ 文件 %s 格式错误， %s', fn, e)
        return mgQQDict
    
    INFO('成功从文件 %s 中读取群的实际 QQ 号码', fn)

    return mgQQDict

def fetchGroupTable(self):

    qqResult = self.smartRequest(
        url = 'http://qun.qq.com/cgi-bin/qun_mgr/get_group_list',
        data = {'bkn': self.bkn},
        Referer = 'http://qun.qq.com/member.html'
    )

    result = self.smartRequest(
        url = 'http://s.web2.qq.com/api/get_group_name_list_mask2',
        data = {
            'r': JsonDumps({'vfwebqq':self.vfwebqq, 'hash':self.hash})
        },
        Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001&'
                   'callback=1&id=2'),
        expectedKey = 'gmarklist',
        repeatOnDeny = 6
    )
    
    markDict = dict((str(d['uin']), str(d['markname'])) \
                    for d in result['gmarklist'])
    
    qqDict = collections.defaultdict(list)
    for k in ('create', 'manage', 'join'):
        for d in qqResult.get(k, []):
            qqDict[HTMLUnescape(d['gn'])].append(str(d['gc']))
    
    qqDict2 = getManaulGroupQQDict()
    
    groups, unresolved = [], []
    for info in result['gnamelist']:
        uin = str(info['gid'])
        nick = str(info['name'])
        mark = markDict.get(uin, '')
        gcode = str(info['code'])
        
        if PY3:
            nick = nick.replace('\xa0', ' ')
            mark = mark.replace('\xa0', ' ')

        name = mark or nick

        qqlist = qqDict.get(nick, [])
        if len(qqlist) == 1:
            qq = qqlist[0]
        else:
            qqlist = qqDict2.get(nick, [])
            if len(qqlist) == 1:
                qq = qqlist[0]
            else:
                qq = '#NULL'
                unresolved.append('群“%s”（uin=%s）' % (name, uin))

        groups.append([qq, uin, nick, mark, name, gcode])        
    
    if unresolved:
        unresolved.sort()
        WARN('因存在重名或名称中含特殊字符，无法绑定以下'
             '群的真实QQ号：\n\t%s', '\n\t'.join(unresolved))
    
    return groups

# by @waylonwang, pandolia
def fetchGroupMemberTable(self, group):
    
    result = self.smartRequest(
        url = ('http://s.web2.qq.com/api/get_group_info_ext2?gcode=%s'
               '&vfwebqq=%s&t={rand}') % (group.gcode, self.vfwebqq),
        Referer = ('http://s.web2.qq.com/proxy.html?v=20130916001'
                   '&callback=1&id=1'),
        expectedKey = 'minfo',
        repeatOnDeny = 5
    )

    cardDict = collections.defaultdict(list)
    nickDict = collections.defaultdict(list)    
    if group.qq != '#NULL':
        r = self.smartRequest(
            url='http://qinfo.clt.qq.com/cgi-bin/qun_info/get_group_members_new',
            Referer='http://qinfo.clt.qq.com/member.html',
            data={'gc': group.qq, 'u': self.uin , 'bkn': self.bkn}
        )        
        
        for m in r['mems']:
            qq = str(m['u'])
            nick = HTMLUnescape(m['n'])
            card = HTMLUnescape(r.get('cards', {}).get(qq, ''))
            mark = HTMLUnescape(r.get('remarks', {}).get(qq, ''))            
            name = card or nick
            
            join_time = r.get('join', {}).get(qq, 0)
            last_speak_time = r.get('times', {}).get(qq, 0)
            is_buddy = m['u'] in r.get('friends', [])
    
            if r['owner'] == m['u'] :
                role, role_id = '群主', 0
            elif m['u'] in r.get('adm', []):
                role, role_id = '管理员', 1
            else:
                role, role_id = '普通成员', 2
    
            level = r.get('lv', {}).get(qq, {}).get('l', 0)
            levelname = HTMLUnescape(r.get('levelname', {}).get('lvln' + str(level), ''))
            point = r.get('lv', {}).get(qq, {}).get('p', 0)
            
            memb = [qq, None, nick, mark, card, name, join_time, last_speak_time,
                    role, role_id, is_buddy, level, levelname, point]
            
            if card:
                cardDict[STR2BYTES(card)[:18]].append(memb)
    
            nickDict[nick].append(memb)
    
    membss, unresolved = [], []
    ucDict = dict((str(it['muin']), it['card']) for it in result.get('cards', {}))
    for m, inf in zip(result['ginfo']['members'], result['minfo']):
        uin, nick = str(m['muin']), str(inf['nick'])
        card = ucDict.get(uin, '')        
        if not PY3:
            card = card.replace('\xc2\xa0', ' ')
            nick = nick.replace('\xc2\xa0', ' ')
        else:
            card = card.replace('\xa0', ' ')
            nick = nick.replace('\xa0', ' ')
        name = card or nick
        
        membs = nickDict.get(nick, [])
        if len(membs) == 1:
            memb = membs[0]
        else:
            membs = cardDict.get(STR2BYTES(card)[:18], [])
            if len(membs) == 1:
                memb = membs[0]
            else:
                memb = None
        
        if memb is None:
            unresolved.append('成员“%s”（uin=%s）' % (name, uin))
            memb = ['#NULL', uin, nick, '#NULL', card, name, -1, -1,
                    '#NULL', -1, -1, -1, '#NULL', -1]
        else:
            memb[1] = uin
        
        membss.append(memb)

    if unresolved:
        unresolved.sort()
        WARN('因存在重名或名称中含特殊字符，无法绑定 %s 中以下'
             '成员的真实QQ号：\n\t%s', group, '\n\t'.join(unresolved))
    
    return membss

def fetchDiscussTable(self):
    result = self.smartRequest(
        url = ('http://s.web2.qq.com/api/get_discus_list?clientid=%s&'
               'psessionid=%s&vfwebqq=%s&t={rand}') % 
              (self.clientid, self.psessionid, self.vfwebqq),
        Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001'
                   '&callback=1&id=2'),
        expectedKey = 'dnamelist',
        repeatOnDeny = 5
    )['dnamelist']        
    discusses = []
    for info in result:
        discusses.append([str(info['did']), str(info['name'])])
    return discusses

def fetchDiscussMemberTable(self, discuss):
    result = self.smartRequest(
        url = ('http://d1.web2.qq.com/channel/get_discu_info?'
               'did=%s&psessionid=%s&vfwebqq=%s&clientid=%s&t={rand}') %
              (discuss.uin, self.psessionid, self.vfwebqq, self.clientid),
        Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001'
                   '&callback=1&id=2')
    )
    qqDict = dict((m['mem_uin'], m['ruin']) for m in result['info']['mem_list'])
    membs = []
    for m in result['mem_info']:
        membs.append([str(qqDict[m['uin']]), str(m['uin']), str(m['nick'])])
    return membs

def Fetch(self, tinfo):
    rname, ttype = rName(tinfo), tType(tinfo)
    INFO('正在获取 %s ...', rname)
    try:
        if ttype == 'buddy':
            table = fetchBuddyTable(self)
        elif ttype == 'group':
            table = fetchGroupTable(self)
        elif ttype == 'discuss':
            table = fetchDiscussTable(self)
        elif ttype == 'group-member':
            table = fetchGroupMemberTable(self, tinfo)
        else:
            table = fetchDiscussMemberTable(self, tinfo)
    except RequestError:
        table = None
    except:
        ERROR('', exc_info=True)
        table = None
    
    if table is None:
        ERROR('获取 %s 失败', rname)

    return table

if __name__ == '__main__':
    from qqbot.qconf import QConf
    from qqbot.basicqsession import BasicQSession
    
    self = BasicQSession()
    conf = QConf(['-q', '158297369'])
    conf.Display()
    self.Login(conf)
