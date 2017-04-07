群内成员的扩展属性（by @SuperMarioSF , pandolia）
------------------------------------------------

对于群内成员对象（ ctype 等于 'group-member' 的 QContact 对象），除了常规的 ctype/qq/uin/nick/mark/card/name 属性之外，还具有一些扩展属性，以下为各扩展属性的含义（所有属性都保存为 str 对象）：

    m.role : 成员角色
             可能的取值: '群主', '管理员', '普通成员'

    m.join_time : 成员入群时间
                  此处的入群时间的数值可能为 0 ，在 QQ 中显示为 “ 2012 年 5 月以前”
                  不为 0 的值为 Unix 时间戳

    m.last_speak_time : 成员最后发言时间。
                        此处的最后发言时间的数值可能为 0 ，在 QQ 中表示为 “从未发言”
                        不为 0 的值为 Unix 时间戳

    m.qage : 成员的 Q 龄（账户注册使用的时间，按年计算）
    
    m.level : 成员等级级别
    
    m.levelname : 成员等级级别名

    m.point : 成员等级分数
              成员等级级别与这个分数有关， QQ 的群活跃等级 PK 中有这个数值的参与
