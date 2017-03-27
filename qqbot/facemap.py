# -*- coding: utf-8 -*-

# facemap by @sjdy521
# https://github.com/sjdy521/Mojo-Webqq/blob/master/lib/Mojo/Webqq/Message/Face.pm

# 发送表情示例：
# qq send buddy jack /微笑
# bot.SendTo(contact, '/微笑')

import re

faceMapStr = '''\
    0   惊讶
    1   撇嘴
    2   色
    3   发呆
    4   得意
    5   流泪
    6   害羞
    7   闭嘴
    8   睡
    9   大哭
    10  尴尬
    11  发怒
    12  调皮
    13  呲牙
    14  微笑
    21  飞吻
    23  跳跳
    25  发抖
    26  怄火
    27  爱情
    29  足球
    32  西瓜
    33  玫瑰
    34  凋谢
    36  爱心
    37  心碎
    38  蛋糕
    39  礼物
    42  太阳
    45  月亮
    46  强  
    47  弱
    50  难过
    51  酷  
    53  抓狂
    54  吐  
    55  惊恐
    56  流汗
    57  憨笑
    58  大兵
    59  猪头
    62  拥抱
    63  咖啡
    64  饭
    71  握手
    72  便便
    73  偷笑
    74  可爱
    75  白眼
    76  傲慢
    77  饥饿
    78  困
    79  奋斗
    80  咒骂
    81  疑问
    82  嘘
    83  晕
    84  折磨
    85  衰
    86  骷髅
    87  敲打
    88  再见
    91  闪电
    92  炸弹
    93  刀
    95  胜利
    96  冷汗
    97  擦汗
    98  抠鼻
    99  鼓掌
    100 糗大了
    101 坏笑
    102 左哼哼
    103 右哼哼
    104 哈欠
    105 鄙视
    106 委屈
    107 快哭了
    108 阴险
    109 亲亲
    110 吓
    111 可怜
    112 菜刀
    113 啤酒
    114 篮球
    115 乒乓
    116 示爱
    117 瓢虫
    118 抱拳
    119 勾引
    120 拳头
    121 差劲
    122 爱你
    123 NO
    124 OK
    125 转圈
    126 磕头
    127 回头
    128 跳绳
    129 挥手
    130 激动
    131 街舞
    132 献吻
    133 左太极
    134 右太极
'''

faceMap, p = {}, '('
for line in faceMapStr.strip().split('\n'):
    code, face = line.strip().split()
    code = int(code)
    faceMap[code] = face
    faceMap[face] = code
    p = p + '/' + face + '|'
p = p[:-1] + ')'
pat = re.compile(p)

def FaceReverseParse(pollContent):
    return ''.join(
        (' /%s ' % faceMap[m[1]]) if isinstance(m, list) else str(m)
        for m in pollContent[1:]
    )

def FaceParse(sendContent):
    result = pat.split(sendContent)
    for i in range(1, len(result), 2):
        result[i] = ['face', faceMap[result[i][1:]]]
    s = 0 if result[0] else 1
    result[-1] or result.pop()
    return result[s:]
