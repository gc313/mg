#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sqlite3
import Module.config as con

#创建表
def create_tb(db_name, table_name, *args):
    '''CREATE TABLE database_name.table_name(
       column1 datatype  PRIMARY KEY(one or more columns),
       column2 datatype,
       column3 datatype,
       .....
       columnN datatype,)
    '''
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    #组合参数
    col = ",".join(args)
    cursor.execute("CREATE TABLE IF NOT EXISTS '%s' (%s)" % (table_name, col))
    cursor.close()
    conn.commit()
    conn.close()
    return

#增
def insert(db_name, order):
    '''INSERT INTO TABLE_NAME [(column1, column2, column3,...columnN)]
        VALUES (value1, value2, value3,...valueN)
    '''
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    #print(col)
    #print(values)
    cursor.execute(order)
    #"insert into regions (id, name) values ('%s', '%s')" % args
    con.logger.debug("已插入数据")
    cursor.close()
    conn.commit()
    conn.close()
    return
#删
def delete(db_name, order):
    '''DELETE FROM table_name
    WHERE [condition];
    '''
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    #cursor.execute("delete from '%s' where update_code <> %f" % (type_id, update_code))
    cursor.execute(order)
    cursor.close()
    conn.commit()
    conn.close()
    return
#改
def update(db_name, table_name, *args):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS '%s' (%s)" % (table_name, col))
    cursor.close()
    conn.commit()
    conn.close()
    return
#查
def select(db_name, order):
    '''
    SELECT column1, column2, columnN FROM table_name;

    SELECT * FROM table_name;

    SELECT column1, column2, columnN
    FROM table_name
    WHERE [condition1] AND [condition2]...AND [conditionN];

    SELECT column-list
    FROM table_name
    [WHERE condition]
    [ORDER BY column1, column2, .. columnN] [ASC | DESC];

    SELECT column1, column2, columnN
    FROM table_name
    LIMIT [no of rows]

    SELECT column1, column2, columnN
    FROM table_name
    LIMIT [no of rows] OFFSET [row num]
    '''
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    rst = cursor.execute(order).fetchall()
    #.fetchall()返回的是一个列表，里面是元组[(object0-0,object0-1),(object1-0, objecy1-1,...object1-n), ...]
    cursor.close()
    conn.commit()
    conn.close()
    return rst

# 判断数据是否存在
def TorF(db_name, table_name, ID):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    #判断数据是否存在

    res = select(db_name, "select * from '%s' where id = %s" %( table_name, ID))
    #res = cursor.execute("select * from '%s' )
    #res = res.fetchall()
    if len(res) <= 0:
        cursor.close()
        conn.commit()
        conn.close()
        return False
    else:
        cursor.close()
        conn.commit()
        conn.close()
        return True

def check_security(system_id):
    res = select(con.uni_db, "select security_status from 'systems' where id = %s" % (system_id))[0][0]
    if res > 0.459:
        return True
    else:
        return False
