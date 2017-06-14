好友的属性（ Buddy 对象）
-----------------------------------------------

- `b.ctype` : str 对象，联系人类型，永远为 'buddy'

- `b.qq` : str 对象，好友的 QQ ，当无法获取时为 '#NULL'

- `b.uin` : str 对象，好友的 uin ，每次登录时分配的一个随机 id 

- `b.nick` : str 对象，好友的昵称，当无法获取时为 '#NULL'

- `b.mark` : str 对象，好友的备注名，当无法获取时为 '#NULL'

- `b.name` ： str 对象，当设置了备注名时为备注名，否则为昵称，当无法获取时为 'uin'+b.uin


群的属性（ Group 对象）
-----------------------------------------------

- `g.ctype` : str 对象，联系人类型，永远为 'group'

- `g.qq` : str 对象，群的 QQ ，当无法获取时为 '#NULL'

- `g.uin` : str 对象，群的 uin ，每次登录时分配的一个随机 id 

- `g.nick` : str 对象，群的原始名称，当无法获取时为 '#NULL'

- `g.mark` : str 对象，群的备注名，当无法获取时为 '#NULL'

- `g.name` ： str 对象，当设置了备注名时为备注名，否则为原始名，当无法获取时为 'uin'+g.uin

- `g.gcode` ： str 对象，群的 gcode （获取群成员时需要用到此值），当无法获取时为 '#NULL'


讨论组的属性（ Discuss 对象）
-----------------------------------------------

- `d.ctype` : str 对象，联系人类型，永远为 'discuss'

- `d.uin` : str 对象，讨论组的 uin ，每次登录时分配的一个随机 id 

- `d.name` : str 对象，讨论组的名称 ，当无法获取时为 'uin'+d.uin


群成员的属性（ GroupMember 对象）（by @SuperMarioSF , pandolia）
------------------------------------------------------------------

- `m.ctype` : str 对象，联系人类型，永远为 'group-member'

- `m.qq` : str 对象，成员的 QQ ，当无法获取时为 '#NULL'

- `m.uin` : str 对象，成员的 uin ，每次登录时分配的一个随机 id 

- `m.nick` : str 对象，成员的昵称，当无法获取时为 '#NULL'

- `m.mark` : str 对象，成员的备注名，当无法获取时为 '#NULL'

- `m.card` : str 对象，成员的群名片，当无法获取时为 '#NULL'

- `m.name` ： str 对象，当设置了群名片时为群名片，否则为昵称，当无法获取时为 'uin'+m.uin

- `m.join_time` : int 对象，成员入群时间
   - 此处的入群时间的数值可能为 0 ，在 QQ 中显示为 “ 2012 年 5 月以前”
   - 不为 0 的值为 Unix 时间戳
   - 当无法获取时为 -1

- `m.last_speak_time` : int 对象，成员最后发言时间
   - 此处的最后发言时间的数值可能为 0 ，在 QQ 中表示为 “从未发言”
   - 不为 0 的值为 Unix 时间戳
   - 当无法获取时为 -1

- `m.role` ： str 对象，成员角色，可能的取值为 '群主'、'管理员'、'普通成员' ，当无法获取时为 '#NULL'

- `m.role_id` : int 对象，成员角色 id ，可能的取值:  0, 1, 2 ，当无法获取时为 -1

- `m.is_buddy` ：int 对象，该成员是否是自己的好友（取值：1,0），当无法获取时为 -1

- `m.level` :  int 对象，成员等级级别，当无法获取时为 -1

- `m.levelname` : str 对象，成员等级级别名，当无法获取时为 '#NULL'

- `m.point` : int 对象，成员等级分数
   - m.level 与这个分数有关， QQ 的群活跃等级 PK 中有这个数值的参与
   - 当无法获取时为 -1


讨论组成员的属性（ DiscussMember 对象）
-----------------------------------------------

- `m.ctype` : str 对象，联系人类型，永远为 'discuss'

- `m.qq` : str 对象，成员的 QQ ，当无法获取时为 '#NULL'

- `m.uin` : str 对象，成员的 uin ，每次登录时分配的一个随机 id 

- `m.name` : str 对象，成员的昵称 ，当无法获取时为 'uin'+m.uin


Unix时间戳的处理（by @SuperMarioSF ）
--------------------------------------------

`m.last_speak_time` 、`m.join_time` 返回的是Unix时间戳，但实际应用中我们可能希望得到一个已经格式化处理好的时间格式。
Unix时间戳是一个整数。表示了UTC时间的1970年1月1日凌晨0:00:00（对应北京时间1970年1月1日早8点）到所要表示的时间的已经经过的秒数。因此Unix时间戳是一个int类型的值。

#### 使用 time 库进行时间处理

`time` 库中有跨平台通用的时间相关的处理方法。

```python
#!/usr/bin/python3
import time

# 产生一个新的Unix时间戳: 北京时间 2017年1月1日早8点
# time.strptime() 返回 struct_time 类型数据，包含了从输入和格式中格式化后的时间。(并不处理时区转换)
# time.mktime() 返回 float 类型数据，表示的是浮点数形式的Unix时间戳。接受的是一个表示本地时间的 struct_time 类型。
unixTimeStamp = int(time.mktime(time.strptime('2017-01-01 08:00:00','%Y-%m-%d %H:%M:%S')))

#显示Unix时间戳。要注意此处的时间戳是整数类型。
print('Timestamp: \t' + str(unixTimeStamp))
#第一种形式，返回Unix系统常见的时间表示方法。
print('ASCIITime: \t' + time.asctime(time.localtime(unixTimeStamp)))
#第二种形式，自定义输出格式。详见 time.strftime() 的帮助信息。
print('Formatted: \t' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(unixTimeStamp)))


```

上述示例的返回值为:
```
Timestamp: 	1483228800
ASCIITime: 	Sun Jan  1 08:00:00 2017
Formatted: 	2017-01-01 08:00:00
```
