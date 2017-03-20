# -*- coding: utf-8 -*-

import sys, os
p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if p not in sys.path:
    sys.path.insert(0, p)

import pickle, time, collections

from qqbot.qconf import QConf
from qqbot.qcontactdb import QContactDB, QContactTable, GetCTypeAndOwner
from qqbot.utf8logger import WARN, INFO, DEBUG
from qqbot.basicqsession import BasicQSession, RequestError
from qqbot.common import JsonDumps

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

class QSession(BasicQSession):
    
    def fetchBuddyTable(self):
        buddyTable = QContactTable('buddy')

        result = self.smartRequest(
            url = 'http://s.web2.qq.com/api/get_user_friends2',
            data = {
                'r': JsonDumps({'vfwebqq':self.vfwebqq, 'hash':self.hash})
            },
            Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001&'
                       'callback=1&id=2')
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
                name = d['name'].replace('&nbsp;', ' ').replace('&amp;', '&')
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

        def extractor(result):
            result = result.get('result', result)
            if 'gmarklist' in result:
                markDict = dict((str(d['uin']), str(d['markname'])) \
                           for d in result['gmarklist'])
                return result, markDict

        result, markDict = self.smartRequest(
            url = 'http://s.web2.qq.com/api/get_group_name_list_mask2',
            data = {
                'r': JsonDumps({'vfwebqq':self.vfwebqq, 'hash':self.hash})
            },
            Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001&'
                       'callback=1&id=2'),
            resultExtractor = extractor,
            repeateOnDeny = 3
        )

        qqResult = self.smartRequest(
            url = 'http://qun.qq.com/cgi-bin/qun_mgr/get_group_list',
            data = {'bkn': self.bkn},
            Referer = 'http://qun.qq.com/member.html'
        )
        
        qqDict = collections.defaultdict(list)
        for k in ('create', 'manage', 'join'):
            for d in qqResult.get(k, []):
                name = d['gn'].replace('&nbsp;', ' ').replace('&amp;', '&')
                qqDict[name].append(str(d['gc']))

        for info in result['gnamelist']:
            uin = str(info['gid'])
            name = str(info['name'])
            mark = markDict.get(uin, '')

            qqlist = qqDict.get(name, [])
            if len(qqlist) == 1:
                qq = qqlist.pop()
            else:
                qq = self.fetchGroupQQ(uin)
                for x in qqlist:
                    if qq[-6:] == x[-6:]:
                        qq = x
                        break
                try:
                    qqlist.remove(qq)
                except ValueError:
                    pass

            groupTable.Add(uin=uin, name=name, qq=qq,
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
        memberTable = QContactTable('group-member')

        def extractor(result):
            retcode = result.get('retcode', -1)
            result = result.get('result', result)
            if retcode in (0, 100003, 6, 15) and 'ginfo' in result:
                return result
        
        result = self.smartRequest(
            url = ('http://s.web2.qq.com/api/get_group_info_ext2?gcode=%s'
                   '&vfwebqq=%s&t={rand}') % (group.gcode, self.vfwebqq),
            Referer = ('http://s.web2.qq.com/proxy.html?v=20130916001'
                       '&callback=1&id=1'),
            resultExtractor = extractor,
            repeateOnDeny = 5
        )

        r = self.smartRequest(
            url = 'http://qun.qq.com/cgi-bin/qun_mgr/search_group_members',
            Referer = 'http://qun.qq.com/member.html',
            data = {'gc': group.qq, 'st': '0', 'end': '20',
                    'sort': '0', 'bkn': self.bkn}
        )
        
        qqDict, nickDict = {}, collections.defaultdict(list)
        for m in r['mems']:
            qq, nick, card = \
                str(m['uin']), str(m['nick']), str(m.get('card', ''))
            memb = [qq, nick, card]
            qqDict[qq] = memb
            nickDict[nick].append(memb)
        
        if 'minfo' in result:
            for m, inf in zip(result['ginfo']['members'], result['minfo']):
                uin, nick = str(m['muin']), str(inf['nick'])
                membs = nickDict.get(nick, [])
                if len(membs) == 1:
                    qq, card = membs[0][0], membs[0][2]
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
                memberTable.Add(uin=uin, name=(card or nick),
                                nick=nick, qq=qq, card=card)
  
        else:
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
    
    def fetchSimpleGroupMemberTable(self, group):
        memberTable = QContactTable('group-member')        
        try:
            r = self.smartRequest(
                url = 'http://qun.qq.com/cgi-bin/qun_mgr/search_group_members',
                Referer = 'http://qun.qq.com/member.html',
                data = {'gc': group.qq, 'st': '0', 'end': '20',
                        'sort': '0', 'bkn': self.bkn},
                repeateOnDeny = 5
            )
        except RequestError:
            return memberTable
        except:
            DEBUG('', exc_info=True)
            return memberTable
        else:
            for m in r['mems']:
                qq, nick, card = \
                    str(m['uin']), str(m['nick']), str(m.get('card', ''))
                memberTable.Add(qq=qq, name=(card or nick),
                                nick=nick, card=card)            
            memberTable.lastUpdateTime = time.time()            
            return memberTable

    def fetchDiscussTable(self):
        discussTable = QContactTable('discuss')

        def extractor(result):
            retcode = result.get('retcode', -1)
            result = result.get('result', result)
            if retcode in (0, 100003) and 'dnamelist' in result:
                return result

        result = self.smartRequest(
            url = ('http://s.web2.qq.com/api/get_discus_list?clientid=%s&'
                   'psessionid=%s&vfwebqq=%s&t={rand}') % 
                  (self.clientid, self.psessionid, self.vfwebqq),
            Referer = ('http://d1.web2.qq.com/proxy.html?v=20151105001'
                       '&callback=1&id=2'),
            resultExtractor = extractor,
            repeateOnDeny = 5
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
            else: # 'discuss-member':
                table = self.fetchDiscussMemberTable(owner)
        except RequestError:
            return None
        except:
            DEBUG('', exc_info=True)
            return None
        else:
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
