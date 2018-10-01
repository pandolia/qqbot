#!/usr/bin/python
#-*-coding:utf8-*-
import json,urllib,urllib2
from qqbot import QQBotSlot as qqbotslot, RunBot

import time 
import jieba
import jieba.analyse


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
        recontent = '小雷锋每天只能回答5000个问题，今天已经很累了，小雷锋要去休息了哦～～'
    elif code == 40002:
        recontent = '您有什么想对小雷锋说的吗？～'
    elif code == 40007:
        recontent = '您输入的数据格式异常，请重新输入！'
    else:
        recontent = '这货还没学会怎么回复这句话'
    return recontent

@qqbotslot

def onQQMessage(bot, contact, member, content):
    
    jieba.load_userdict("/home/qqbot/dictName.txt")
    # 聊天记录部分
    localtime = time.asctime( time.localtime(time.time()) )
    strTime = time.strftime("%b-%d", time.localtime())
    RecordFile = open("/home/qqbot/record/"+strTime+".txt","ab")
    ltime = time.strftime("%H:%M:%S", time.localtime())
    RecordFile.write(localtime + '\n' + str(contact) + ' ' + str(member) + ':  ' + content + '\n')
    BotAnswer = '' # 记录机器人回复内容，便于储存聊天记录

    # 开关自动回复部分 先读后写
    DonList = open("/home/qqbot/friendList.txt", "r+")
    dont = DonList.read()
    strDont = dont.split('#')
    DonList.close()
    DontList = open("/home/qqbot/friendList.txt", "w+")
    if (content == "开启自动回复"):
        if member == None:
            strDont.remove(str(contact))
            bot.SendTo(contact, "小雷锋自动回复已开启")
            return;
        else:
            strDont.remove(str(contact) + str(member))
            return;
    elif member == None:
        for tmpDont in strDont:
            if tmpDont == str(contact):
                DontList.write(dont)
                return;
    else:
        for tmpDont in strDont:
            if tmpDont == str(contact)+str(member):
                DontList.write(dont)
                return;
    if (content == "关闭自动回复") or ('@ME' in content and '闭嘴' in content):
        if member == None:
            strDont.append(str(contact))
            bot.SendTo(contact, str(contact) + " 小雷锋自动回复已关闭，如需开启请发送“开启自动回复”")
            for tmpWriDon in strDont:
                if tmpWriDon != '':
                    DontList.write(tmpWriDon+'#')
            return;
        else:
            strDont.append(str(contact) + str(member))
            for tmpWriDon in strDont:
                if tmpWriDon != '':
                    DontList.write(tmpWriDon+'#')
            if ('闭嘴' in content):
                bot.SendTo(contact, str(member) + " 好吧/小纠结小雷锋自动回复已关闭，如需开启请发送“开启自动回复”")
            return;
    for tmpWriDon in strDont:
        if tmpWriDon != '':
            DontList.write(tmpWriDon+'#')
    DontList.close()

    # 自动聊天部分
    if bot.isMe(contact, member):
        return()
    if content == '--stop':
        BotAnswer = '我轻轻的走了，正如我轻轻的来。挥一挥衣袖，忘掉我的所有～～'
        bot.SendTo(contact, BotAnswer)
        RecordFile.write(BotAnswer + '\n')
        bot.Stop()
    else:
        if '小V' in str(member) or '小v' in str(member) or '瓜大电视台' in str(member) or 'QQ小冰' in str(member):  # 防止机器人打架
            return;
        if getattr(member, 'uin', None) == bot.conf.qq:  # 防止自嗨
            return()
        else:
            QAfile = open(r"/home/qqbot/qa.txt","r")    # 读取问题库
            strQA = QAfile.read()
            stQA = strQA.split("Q")
            QAfile.close()
            tmp = 0

            if (not content=='') and (tmp < 6) and (len(content) > 3) and (member != None) and (len(content) < 30) \
            and (not content=='没有') and (not content=='西工大') and (not content == '可以') and (('问' in content) or ('知道' in content) or ('？' in content)):
                contentSep = jieba.analyse.extract_tags(content, allowPOS=('ns', 'n', 'nz'))    # 通过jieba分词获得句中一些关键词
                for cont in stQA:
                    cont_q = cont.split('A')
                    tSep = 0                            
                    for tmpSep in contentSep:
                        if (tmpSep.encode('UTF-8') in cont_q[0]) and (not tmpSep.encode('UTF-8') == '电话'):    # 判断句中关键词是否在问题中
                            tSep = tSep + 1
                    if tSep > 0 and tmp < 6:
                        BotAnswer += 'Q' + cont + '\n'
                        bot.SendTo(contact, 'Q' + cont)
                        tmp = tmp+1
                if tmp > 0: # 存在可能符合需要的问题
                    bot.SendTo(contact, '小雷锋机器程序还在完善中/可爱如需关闭请@小雷锋同时说闭嘴/小纠结')
                
            if tmp==0 and member == None:   # 私聊模式，因为webqq限制只支持双向好友
                if '无聊' in content:
                    tmpAns = talk('笑话',contact.qq)
                    bot.SendTo(contact,'无聊麽？让小雷锋给你讲个笑话吧/可爱~~'+tmpAns)
                    BotAnswer += '无聊麽？让小雷锋给你讲个笑话吧/可爱~~'+tmpAns+'\n'
                elif ('党' in content) or ('中国' in content) or ('台湾' in content):
                    bot.SendTo(contact,'小雷锋是热爱祖国的好孩子/可爱让我们不要谈论这些话题了/可爱')
                    BotAnswer+='小雷锋是热爱祖国的好孩子/可爱让我们不要谈论这些话题了/可爱'+'\n'
                elif ('谁' in content) and ('最美' in content):
                    bot.SendTo(contact, '是你呀/可爱')
                    BotAnswer+='是你呀/可爱'+'\n'
                elif (('你' in content) or ('小雷锋' in content)) and (('创造' in content) or ('制' in content) or ('做' in content)):
                    bot.SendTo(contact,'是美丽帅气的小雷锋团队让我来到这个世界的哦/可爱/可爱')
                    BotAnswer+='是美丽帅气的小雷锋团队让我来到这个世界的哦/可爱/可爱'+'\n'
                elif ('夸我' in content):
                    bot.SendTo(contact,'你好好看/小纠结小雷锋好羡慕你')
                    BotAnswer += '你好好看/小纠结小雷锋好羡慕你'+'\n'
                elif ('小V' in str(contact)):
                    return;
                else:
                    if (not content=='') and (tmp < 6) and (len(content) > 3):
                        contentSep = jieba.analyse.extract_tags(content, allowPOS=('ns', 'n', 'nz'))
                        for cont in stQA:
                            cont_q = cont.split('A')
                            tSep = 0                            
                            for tmpSep in contentSep:
                                if (tmpSep.encode('UTF-8') in cont_q[0]) and (not tmpSep.encode('UTF-8') == '电话'):
                                    tSep = tSep + 1
                            if tSep > 0:
                                BotAnswer += 'Q' + cont + '\n'
                                bot.SendTo(contact, 'Q' + cont)
                                tmp = tmp+1
                        
                    if tmp > 0:
                        bot.SendTo(contact, '小雷锋机器程序还在完善中/可爱如果需要关闭请发送“关闭自动回复”\n如果想要提出修改意见或者加入我们请联系QQ：1024898890')
                    if tmp == 0:
                        tmpAns2 = talk(content,contact.qq)
                        bot.SendTo(contact,tmpAns2)
                        BotAnswer += tmpAns2 + '\n'
            #elif contact.qq == '416562613' and contact.ctype == 'group':
            #    bot.SendTo(contact, talk(content,contact.qq))
            elif ('瓜大小雷锋' in str(contact)) and ('Q' in content) and ('A' in content) and ((':' in content) or ('：' in content)) and str(content).count('Q') == 1:
                # 小雷锋运营群可以直接添加问题库QA
                addQAFile = open("/home/qqbot/qa.txt","ab")
                addQAFile.write('\n' + content)
                bot.SendTo(contact, 'QA添加成功！')
                bot.SendTo(contact, content)
                addQAFile.close()
            elif tmp==0 and ('@ME' in content):
                if ('党' in content) or ('中国' in content) or ('台湾' in content):
                    bot.SendTo(contact,'小雷锋是热爱祖国的好孩子/可爱让我们不要谈论这些话题了/可爱')
                    BotAnswer+='小雷锋是热爱祖国的好孩子/可爱让我们不要谈论这些话题了/可爱'+'\n'
                elif ('母亲' in content) or ('妈妈' in content):
                    bot.SendTo(contact, '不告诉你，略略略')
                    BotAnswer += '不告诉你，略略略' + '\n'
                elif ('小V' in str(member)):
                    return;
                else:
                    tmpAns3 = talk(content,contact.qq)
                    bot.SendTo(contact, '@'+member.name+'  '+tmpAns3)
                    BotAnswer += '@'+member.name+'  '+tmpAns3 + '\n'
            else:
                return()
    RecordFile.write(BotAnswer + '\n')
    RecordFile.close()


RunBot()    # 启动qqbot，如果是插件模式请注释掉此行