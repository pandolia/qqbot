# -*- coding: utf-8 -*-

import sys, os
p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if p not in sys.path:
    sys.path.insert(0, p)

import pickle

from qqbot.qcontactdb import QContactDB
from qqbot.utf8logger import WARN, INFO, DEBUG
from qqbot.basicqsession import BasicQSession, RequestError
from qqbot.groupmanager import GroupManagerSession
from qqbot.common import SYSTEMSTR2STR

def QLogin(conf):
    if conf.qq:
        INFO('开始自动登录...')
        picklePath = conf.PicklePath()
        session = QSession()
        try:
            with open(picklePath, 'rb') as f:
                session.__dict__ = pickle.load(f)
            session.dbname = conf.absPath(session.dbbasename)
        except Exception as e:
            WARN('自动登录失败，原因：%s', e)
        else:
            INFO('成功从文件 "%s" 中恢复登录信息' % SYSTEMSTR2STR(picklePath))

            try:
                session.TestLogin()
            except RequestError:
                WARN('自动登录失败，原因：上次保存的登录信息已过期')
            except Exception as e:
                WARN('自动登录失败，原因：%s', e)
                DEBUG('', exc_info=True)                
            else:
                return session, QContactDB(session)
            
            if os.path.exists(session.dbname):
                try:
                    os.remove(session.dbname)
                except OSError:
                    pass
                except:
                    WARN('', exc_info=True)

    INFO('开始手动登录...')
    session = QSession()
    session.Login(conf)
    picklePath = conf.PicklePath()
    try:
        with open(picklePath, 'wb') as f:
            pickle.dump((session.__dict__), f)
    except Exception as e:
        WARN('保存登录信息及联系人失败：%s %s', (e, SYSTEMSTR2STR(picklePath)))
    else:
        INFO('登录信息已保存至：%s' % SYSTEMSTR2STR(picklePath))

    return session, QContactDB(session)

class QSession(BasicQSession, GroupManagerSession):
    pass

if __name__ == '__main__':    
    from qqbot.qconf import QConf
    conf = QConf(['-q', '158297369'])
    conf.Display()
    session, contactdb = QLogin(conf)
    self = session
    c = contactdb.List('buddy', 'Eva')[0]
