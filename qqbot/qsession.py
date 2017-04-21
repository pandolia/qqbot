# -*- coding: utf-8 -*-

import sys, os
p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if p not in sys.path:
    sys.path.insert(0, p)

import pickle

from qqbot.qconf import QConf
from qqbot.qcontactdb import QContactDB
from qqbot.utf8logger import WARN, INFO, DEBUG
from qqbot.basicqsession import BasicQSession, RequestError
from qqbot.groupmanager import GroupManagerSession

def QLogin(qq=None, user=None):
    conf = QConf(qq, user)
    conf.Display()

    if conf.qq:
        INFO('开始自动登录...')
        picklePath = conf.PicklePath()
        session = QSession()
        try:
            with open(picklePath, 'rb') as f:
                session.__dict__ = pickle.load(f)
        except Exception as e:
            WARN('自动登录失败，原因：%s', e)
        else:
            INFO('成功从文件 "%s" 中恢复登录信息' % picklePath)

            try:
                session.TestLogin()
            except RequestError:
                WARN('自动登录失败，原因：上次保存的登录信息已过期')
            except Exception as e:
                WARN('自动登录失败，原因：%s', e)
                DEBUG('', exc_info=True)                
            else:
                return session, QContactDB(session), conf
            
            try:
                os.remove(session.dbname)
            except:
                pass

    INFO('开始手动登录...')
    session = QSession()
    session.Login(conf)
    picklePath = conf.PicklePath()
    try:
        with open(picklePath, 'wb') as f:
            pickle.dump((session.__dict__), f)
    except Exception as e:
        WARN('保存登录信息及联系人失败：%s %s', (e, picklePath))
    else:
        INFO('登录信息已保存至文件：file://%s' % picklePath)

    return session, QContactDB(session), conf

class QSession(BasicQSession, GroupManagerSession):
    pass

if __name__ == '__main__':
    session, contactdb, conf = QLogin(qq='158297369')
    self = session
    c = contactdb.List('buddy', 'Eva')[0]
