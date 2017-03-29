# -*- coding: utf-8 -*-

import sys, os
p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if p not in sys.path:
    sys.path.insert(0, p)

import pickle, time, collections

from qqbot.qconf import QConf
from qqbot.qcontactdb import QContactDB,QContactTable,GetCTypeAndOwner,CTYPES
from qqbot.utf8logger import WARN, INFO, DEBUG, ERROR
from qqbot.basicqsession import BasicQSession, RequestError
from qqbot.common import JsonDumps, HTMLUnescape
from qqbot.groupmanager import GroupManagerSession

def QLogin(qq=None, user=None):
    conf = QConf(qq, user)
    conf.Display()

    if conf.qq:
        INFO('开始自动登录...')
        picklePath = conf.PicklePath()
        session = QSession()
        contactdb = QContactDB(session)
        try:
            contactdb.Restore(picklePath)
        except Exception as e:
            WARN('自动登录失败，原因：%s', e)
        else:
            INFO('成功从文件 "%s" 中恢复登录信息' % picklePath)

            try:
                contactdb.session.TestLogin()
            except RequestError:
                WARN('自动登录失败，原因：上次保存的登录信息已过期')
            except Exception as e:
                WARN('自动登录失败，原因：%s', e)
                DEBUG('', exc_info=True)                
            else:
                return contactdb.session.Copy(), contactdb, conf

    INFO('开始手动登录...')
    session = QSession()
    session.Login(conf)
    contactdb = QContactDB(session, conf.PicklePath())
    contactdb.Dump()
    return session.Copy(), contactdb, conf

def Dump(picklePath, session, contactdb):
    sessionDict = session.__dict__
    contactDict = contactdb.__dict__ if contactdb else None
    try:
        with open(picklePath, 'wb') as f:
            pickle.dump((sessionDict, contactDict), f)
    except Exception as e:
        WARN('保存登录信息及联系人失败：%s %s', (e, picklePath))
    else:
        if contactdb is None:
            INFO('登录信息已保存至文件：file://%s' % picklePath)
        else:
            INFO('登录信息及联系人资料已保存至文件：file://%s' % picklePath)

class QSession(BasicQSession, GroupManagerSession):
    
    def fetchBuddyTable(self):
        buddyTable = QContactTable('buddy')

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

        for info in result['info']:
            uin = str(info['uin'])
            nick = str(info['nick'])
            mark = markDict.get(uin, '')
            name = mark or nick
            qqlist = qqDict.get(name, [])
            if len(qqlist) == 1:
                qq = qqlist.pop()
            else:
                qq = self.fetchBuddyQQ(uin)
                try:
                    qqlist.remove(qq)
                except ValueError:
                    pass
                
            buddyTable.Add(uin=uin, name=name, qq=qq, mark=mark, nick=nick)
        
        buddyTable.lastUpdateTime = time.time()
        
        return buddyTable

    def fetchBuddyQQ(self, uin):
        return str(self.smartRequest(
            url = ('http://s.web2.qq.com/api/get_friend_uin2?tuin=%s&'
                   'type=1&vfwebqq=%s&t={rand}') % (uin, self.vfwebqq),
            Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001&'
                       'callback=1&id=2'),
            timeoutRetVal = {'account': ''}
        )['account'])
    
    def fetchBuddyDetailInfo(self, uin):
         return self.smartRequest(
             url = ('http://s.web2.qq.com/api/get_friend_info2?tuin=%s&'
                    'vfwebqq=%s&clientid=%s&psessionid=%s&t={rand}') % \
                   (uin, self.vfwebqq, self.clientid, self.psessionid),
             Referer = ('http://s.web2.qq.com/proxy.html?v=20130916001&'
                        'callback=1&id=1')
         )

    def fetchGroupTable(self):        
        groupTable = QContactTable('group')

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
            repeatOnDeny = 8
        )
        
        markDict = dict((str(d['uin']), str(d['markname'])) \
                   for d in result['gmarklist'])
        
        qqDict = collections.defaultdict(list)
        for k in ('create', 'manage', 'join'):
            for d in qqResult.get(k, []):
                qqDict[HTMLUnescape(d['gn'])].append(str(d['gc']))
        
        unresolved = []
        for info in result['gnamelist']:
            uin = str(info['gid'])
            name = str(info['name'])
            mark = markDict.get(uin, '')

            qqlist = qqDict.get(name, [])
            if len(qqlist) == 1:
                # 没有重名现象
                qq = qqlist[0]
                qqDict.pop(name)
            elif len(qqlist) > 1:
                # 有重名现象
                qq = self.fetchGroupQQ(uin) # 这里返回的qq号可能只有最后6位是对的
                for trueQQ in qqlist[:]:
                    if qq[-6:] == trueQQ[-6:]:
                        qq = trueQQ
                        qqlist.remove(trueQQ)
                        break
            else:
                # 可能是 qun.qq.com 返回的 name 和 w.qq.com 返回的 name 不一致
                # 比如： “x&nbsp;x” 和 “x x” ，尽管经过前面的转义处理，但可能还是
                # 有没有转过来的
                # 也可能是两次请求的空隙期间加入了一个新群（理论上有这种可能）
                unresolved.append( (uin, name, mark) )
                continue

            groupTable.Add(uin=uin, name=(mark or name), nick=name, qq=qq,
                           mark=mark, gcode=str(info['code']))
        
        for uin, name, mark in unresolved:
            qq = self.fetchGroupQQ(uin) # 这里返回的qq号可能只有最后6位是对的

            for xname, qqlist in list(qqDict.items()):
                for trueQQ in qqlist[:]:
                    if qq[-6:] == trueQQ[-6:]:
                        qq = trueQQ
                        if len(qqlist) == 1:
                            qqDict.pop(xname)
                        else:
                            qqlist.remove(qq)
                        break
                else:
                    continue
    
                break
            
            groupTable.Add(uin=uin, name=(mark or name), nick=name, qq=qq,
                           mark=mark, gcode=str(info['code']))
        
        groupTable.lastUpdateTime = time.time()
        
        return groupTable
    
    def fetchGroupQQ(self, uin):
        return str(self.smartRequest(
            url = ('http://s.web2.qq.com/api/get_friend_uin2?tuin=%s&'
                   'type=4&vfwebqq=%s&t={rand}') % (uin, self.vfwebqq),
            Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001&'
                       'callback=1&id=2'),
            timeoutRetVal = {'account': ''}
        )['account'])


    def fetchGroupMemberTable(self, group):
        # 没有现在必要获取成员的 uin，也没有必要现在将 uin 和 qq 绑定起来。
        # 需要的时候再绑定就可以了
        memberTable = QContactTable('group-member')

        r = self.smartRequest(
            url = 'http://qun.qq.com/cgi-bin/qun_mgr/search_group_members',
            Referer = 'http://qun.qq.com/member.html',
            data = {'gc': group.qq, 'st': '0', 'end': '2000',
                    'sort': '0', 'bkn': self.bkn}
        )
        
        for m in r['mems']:
            qq = str(m['uin'])
            nick = HTMLUnescape(str(m['nick']))
            card = HTMLUnescape(str(m.get('card', '')))
            memberTable.Add(name=(card or nick), nick=nick, qq=qq, card=card)
        
        memberTable.lastUpdateTime = time.time()
        
        return memberTable
    
    '''
    def fetchGroupMemberTable(self, group):
        memberTable = QContactTable('group-member')
        
        result = self.smartRequest(
            url = ('http://s.web2.qq.com/api/get_group_info_ext2?gcode=%s'
                   '&vfwebqq=%s&t={rand}') % (group.gcode, self.vfwebqq),
            Referer = ('http://s.web2.qq.com/proxy.html?v=20130916001'
                       '&callback=1&id=1'),
            # expectedCodes = (0, 100003, 6, 15),
            expectedKey = 'ginfo',
            repeatOnDeny = 5
        )

        r = self.smartRequest(
            url = 'http://qun.qq.com/cgi-bin/qun_mgr/search_group_members',
            Referer = 'http://qun.qq.com/member.html',
            data = {'gc': group.qq, 'st': '0',
                    'end': str(len(result['ginfo']['members'])+10),
                    'sort': '0', 'bkn': self.bkn}
        )
        
        qqDict, nickDict = {}, collections.defaultdict(list)
        for m in r['mems']:
            qq, nick, card = \
                str(m['uin']), str(m['nick']), str(m.get('card', ''))
            nick = HTMLUnescape(nick)
            card = HTMLUnescape(card)
            memb = [qq, nick, card]
            qqDict[qq] = memb
            nickDict[nick].append(memb)
        
        if 'minfo' in result:
            # 进入此块，获取群成员列表最多 10 秒（1887个成员）
            for m, inf in zip(result['ginfo']['members'], result['minfo']):
                uin, nick = str(m['muin']), str(inf['nick'])
                membs = nickDict.get(nick, [])
                if len(membs) == 1:
                    qq, card = membs[0][0], membs[0][2]
                    # DEBUG('Resolved: nick=%s,qq=%s,card=%s',nick,qq,card)
                else:
                    qq = self.fetchBuddyQQ(uin)
                    if qq in qqDict:
                        card = qqDict[qq][2]                    
                        try:
                            membs.remove(qqDict[qq])
                        except ValueError:
                            pass
                    else:
                        card = ''
                    # DEBUG('Unresolved: nick=%s,qq=%s,card=%s',nick,qq,card)
                memberTable.Add(uin=uin, name=(card or nick),
                                nick=nick, qq=qq, card=card)
        else:
            # 进入此块，获取群成员列表可能得 5 分钟（1887个成员）
  
            if IsMainThread() and len(result['ginfo']['members']) > 15:
                # 绝对不能让主线程阻塞 5 分钟，因此返回空 table
                return memberTable

            for m in result['ginfo']['members']:                    
                uin = str(m['muin'])
                qq = self.fetchBuddyQQ(uin)
                if qq in qqDict:
                    nick, card = qqDict[qq][1], qqDict[qq][2]
                else:
                    nick, card = '##UNKOWN', ''
                memberTable.Add(uin=uin, name=(card or nick),
                                nick=nick, qq=qq, card=card)
        
        memberTable.lastUpdateTime = time.time()
        
        return memberTable
    '''
    
    def fetchDiscussTable(self):
        discussTable = QContactTable('discuss')

        result = self.smartRequest(
            url = ('http://s.web2.qq.com/api/get_discus_list?clientid=%s&'
                   'psessionid=%s&vfwebqq=%s&t={rand}') % 
                  (self.clientid, self.psessionid, self.vfwebqq),
            Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001'
                       '&callback=1&id=2'),
            # expectedCodes = (0, 100003),
            expectedKey = 'dnamelist',
            repeatOnDeny = 5
        )['dnamelist']

        for info in result:
            discussTable.Add(uin=str(info['did']), name=str(info['name']),
                             qq=str(info['did']))
        discussTable.lastUpdateTime = time.time()
        return discussTable
    
    def fetchDiscussMemberTable(self, discuss):        
        memberTable = QContactTable('discuss-member')
        result = self.smartRequest(
            url = ('http://d1.web2.qq.com/channel/get_discu_info?'
                   'did=%s&psessionid=%s&vfwebqq=%s&clientid=%s&t={rand}') %
                  (discuss.uin, self.psessionid, self.vfwebqq, self.clientid),
            Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001'
                       '&callback=1&id=2')
        )
        for m in result['mem_info']:
            uin = str(m['uin'])
            name = str(m['nick'])
            qq = self.fetchBuddyQQ(uin)
            memberTable.Add(uin=uin, name=name, qq=qq)
        memberTable.lastUpdateTime = time.time()
        return memberTable
    
    def FetchTable(self, tinfo):
        ctype, owner = GetCTypeAndOwner(tinfo)
        try:
            if ctype == 'buddy':
                table = self.fetchBuddyTable()
            elif ctype == 'group':
                table = self.fetchGroupTable()
            elif ctype == 'discuss':
                table = self.fetchDiscussTable()
            elif ctype == 'group-member':
                table = self.fetchGroupMemberTable(owner)
            else:
                table = self.fetchDiscussMemberTable(owner)
        except RequestError:
            table = None
        except:
            DEBUG('', exc_info=True)
            table = None
        
        if table is None:
            if ctype in ('buddy', 'group', 'discuss'):
                ERROR('获取 %s 列表失败', CTYPES[ctype])
            else:
                ERROR('获取 %s 的成员列表失败', owner)
            
        return table
    
    def FetchNewBuddyInfo(self, uin):
        try:
            qq = self.fetchBuddyQQ(uin)
            nick = self.fetchBuddyDetailInfo(uin).get('nick', '')
            binfo = dict(uin=uin, qq=qq, nick=nick, name=nick)
        except RequestError:
            return None
        except:
            DEBUG('', exc_info=True)
            return None
        else:
            return binfo

if __name__ == '__main__':
    session, contactdb, conf = QLogin(user='hcj')
    self = session
