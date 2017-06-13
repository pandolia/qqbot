# -*- coding: utf-8 -*-

# 从 2017 年 6 月 7 日之前的联系人数据库文件中导出群的 QQ 和群名称，并输出文件 groupqq
# 使用方法： python getgroupqq.py xxx.db

import sqlite3, sys, os
    
comment = '''\
# 由于获取群实际 QQ 号的接口 http://qun.qq.com/cgi-bin/qun_mgr/get_group_list 被关
# 闭，导致无法绑定群的实际 QQ 号及其成员的实际 QQ 号。目前临时的解决办法是手工绑定，在本文件
# 中手工按行输入群号及群名，以逗号隔开，不要有空格。
'''

if __name__ == '__main__':
    
    dbname = sys.argv[1]
    outfile = os.path.join(os.path.dirname(dbname), 'groupqq')
    conn = sqlite3.connect(dbname)
    conn.text_factory = str
    cursor = conn.cursor()
    cursor.execute("SELECT qq,nick FROM 'group'")
    groups = cursor.fetchall()
    cursor.close()
    conn.close()
    
    out = comment + '\n'.join(','.join(g) for g in groups)
    
    if sys.version_info[0] == 3:
        out = out.encode('utf8')
    
    with open(outfile, 'wb') as f:
        f.write(out)
