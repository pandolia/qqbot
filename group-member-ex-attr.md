群内成员的扩展属性（by @SuperMarioSF , pandolia）
------------------------------------------------

对于群内成员对象（ ctype 等于 'group-member' 的 QContact 对象），除了常规的 ctype/qq/uin/nick/mark/card/name 属性之外，还具有一些扩展属性，以下为各扩展属性的含义（所有属性都保存为 str 对象）：

- `m.role` : 成员角色
   可能的取值: '群主', '管理员', '普通成员'

- `m.join_time` : 成员入群时间
   此处的入群时间的数值可能为 0 ，在 QQ 中显示为 “ 2012 年 5 月以前”
   不为 0 的值为 Unix 时间戳

- `m.last_speak_time` : 成员最后发言时间。
   此处的最后发言时间的数值可能为 0 ，在 QQ 中表示为 “从未发言”
   不为 0 的值为 Unix 时间戳

- `m.qage` : 成员的 Q 龄（账户注册使用的时间，按年计算）

- `m.level` : 成员等级级别

- `m.levelname` : 成员等级级别名

- `m.point` : 成员等级分数
   成员等级级别与这个分数有关， QQ 的群活跃等级 PK 中有这个数值的参与


Unix时间戳的处理
----------------

`m.last_speak_time` 、`m.join_time` 返回的是Unix时间戳，但实际应用中我们可能希望得到一个已经格式化处理好的时间格式。
Unix时间戳是一个整数。表示了UTC时间的1970年1月1日凌晨0:00:00（对应北京时间1970年1月1日早8点）到所要表示的时间的已经经过的秒数。因此Unix时间戳是一个int类型的值。
但需要注意的是，从QQbot返回的信息都是str类型，因此使用之前需要进行转换。

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
