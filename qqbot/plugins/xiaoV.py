#-*-coding:utf8-*-
import json,urllib,urllib2
from qqbot import QQBotSlot as qqbotslot, RunBot

def talk(content,userid):
    url = 'http://www.tuling123.com/openapi/api'
    s = urllib2.Request(url)
    da = {"key":"输入你从图灵机器人官网获得的key","info":content,"userid":userid}
    da = urllib.urlencode(da)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    j = eval(opener.open(s,da).read())
#    r = s.post(url,data = data)
#    j = eval(r.text)
    code = j['code']
    if code == 100000:
        recontent = j['text']
    elif code == 200000:
        recontent = j['text']+j['url']
    elif code == 302000 or code ==308000:
        recontent = j['text']+j['list'][0]['info']+j['list'][0]['detailurl']
    elif code == 40004:
        recontent = '小V每天只能回答5000个问题，今天已经很累了，小V要去休息了哦～～'
    elif code == 40002:
        recontent = '您有什么想对小V说的吗？～'
    elif code == 40007:
        recontent = '您输入的数据格式异常，请重新输入！'
    else:
        recontent = '这货还没学会怎么回复这句话'
    return recontent

@qqbotslot

def onQQMessage(bot, contact, member, content):
    if content == '--stopV djg':
        bot.SendTo(contact,'我轻轻的走了，正如我轻轻的来。挥一挥衣袖，忘掉我的所有～～')
        bot.Stop()
    else:
        if getattr(member, 'uin', None) == bot.conf.qq:
            return()
        else:
            if ('部门' in content) and ('电视台' in content):
                bot.SendTo(contact,'电视台目前有企划、记者、编辑、播音、宣传五大部门/可爱，还有神秘的特别行动部哦~/嘘另外多个节目组欢迎探索~')
            elif (content == '小V') or (content == '小v'):
                bot.SendTo(contact,'有人在叫我麽？/可爱大家好！我是大学生新闻中心电视台机器人小V，欢迎17级新同学加入电视台大家庭/可爱电视台招新群号码：651846410')
            elif member == None:    # 私戳
                if '无聊' in content:
                    bot.SendTo(contact,'无聊麽？让小V给你讲个笑话吧/可爱~~'+talk('笑话',contact.qq))
                elif ('党' in content) or ('中国' in content) or ('台湾' in content):
                    bot.SendTo(contact,'小V是热爱祖国的好孩子/可爱让我们不要谈论这些话题了/可爱')
                elif ('谁' in content) and ('最美' in content):
                    bot.SendTo(contact, '是你呀/可爱')
                elif ('夸我' in content):
                    bot.SendTo(contact,'你好好看/小纠结小V好羡慕你')
                else:
                    bot.SendTo(contact,talk(content,contact.qq))
            elif '@ME' in content:  # 有人@我
                if ('党' in content) or ('中国' in content) or ('台湾' in content):
                    bot.SendTo(contact,'小V是热爱祖国的好孩子/可爱让我们不要谈论这些话题了/可爱')
                else:
                    bot.SendTo(contact, '@'+member.name+'  '+talk(content,contact.qq))
            else:
                return()
RunBot()
