#-*-coding:utf8-*-
import json,urllib,urllib2
from qqbot import QQBotSlot as qqbotslot, RunBot

def talk(content,userid):
    url = 'http://www.tuling123.com/openapi/api'
    s = urllib2.Request(url)
    da = {"key":"输入图灵机器人给的key值","info":content,"userid":userid}
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
    if content == '--stop':
        bot.SendTo(contact,'我轻轻的走了，正如我轻轻的来。挥一挥衣袖，忘掉我的所有～～')
        bot.Stop()
    else:
        if getattr(member, 'uin', None) == bot.conf.qq:
            return()
        else:
            if member == None:
                bot.SendTo(contact,talk(content,contact.qq))
            elif '@ME' in content:
                bot.SendTo(contact, '@'+member.name+'  '+talk(content,contact.qq))
            else:
                return()
RunBot()
