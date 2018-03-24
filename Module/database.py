#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sqlite3
import Module.config as con

#创建数据库
def create_db(name, *args, **kw):


    return
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
def insert(db_name, table_name, **kw):
    '''INSERT INTO TABLE_NAME [(column1, column2, column3,...columnN)]
        VALUES (value1, value2, value3,...valueN)
    '''
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    col = ",".join(key for key in kw.keys())

    v_list = []
    for i in kw.values():
        if type(i) == str:
            #针对sqlite采取的字符串格式化处理，坑得死人
            #如果字符串本身有单引号（'）的，用空白替换掉，然后再在两端加上单引号（'），不然会报语法错误
            i = "'" + i.replace("'", '') + "'"
        v_list.append(i)
    values = ",".join(str(value) for value in v_list)

    #print(col)
    #print(values)
    cursor.execute("INSERT INTO '%s' (%s) VALUES (%s)" % (table_name, col, values))
    #"insert into regions (id, name) values ('%s', '%s')" % args
    con.logger.debug("已插入数据：%s | %s" % (col, values))
    cursor.close()
    conn.commit()
    conn.close()
    return
#删
def delete(db_name, table_name, condition):
    '''DELETE FROM table_name
    WHERE [condition];
    '''
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    #cursor.execute("delete from '%s' where update_code <> %f" % (type_id, update_code))
    cursor.execute("DELETE FROM '%s' WHERE %s" % (table_name, condition))
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
def select(db_name, table_name, *args, **kw):
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

    for i in args:
        if i == "*":
            col = "*"
        else:
            col = ",".join(args)
    #不明觉厉
    order_list = " ".join(key.replace("_", " ")+" "+value for key, value in kw.items())

    #col = ",".join(key for key in kw.keys())
    rst = cursor.execute("SELECT %s FROM %s " %(col, table_name) + order_list).fetchall()
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
    res = select(db_name, table_name, "*", WHERE = "id = %s" % (ID))
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
