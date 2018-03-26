#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import Module.config as con
import Module.database as db
import Module.http as http
import Module.sendmail as mail

def find_tables(db_name, update_code):
    con.logger.info("开始处理订单")
    #数据校验，删除以往数据
    #db.delete(db_name, "delete from contrast where update_code <> %f" % (update_code))
    #获取表名
    table_names = db.select(db_name, "select name from sqlite_master where type='table' order by name")
    #通过表名逐个表梳理数据
    for i in table_names:
        #print(i)
        t_name = i[0]
        #笨办法,剔除不需要的表
        if t_name != "contrast" and t_name != "sqlite_sequence":
            contrast(db_name, t_name, update_code)
    return
#获取数据进行比较
def contrast(db_name, table_name, update_code):

    con.logger.debug("比较数据%s" % (table_name))
    #获取物品信息

    type_volume = db.select(con.uni_db, "select volume from 'types' where id = '%s'" % (table_name))[0][0] #体积
    type_en_name = db.select(con.uni_db, "select en_name from 'types' where id = '%s'" % (table_name))[0][0]
    type_zh_name = db.select(con.uni_db, "select zh_name from 'types' where id = '%s'" % (table_name))[0][0]

    #筛选出卖单
    sell_order = db.select(db_name, "select * from '%s' where b_or_s = 0 order by price" % (table_name))

    for i in sell_order:
        con.logger.debug("筛选卖单")
        type_id = i[1] #物品ID
        sell_location_name, sell_system = db.select(con.uni_db, "select name, systems from 'H_sec_location' where id = '%s'" % (i[2]))[0] #出售地址和所在星系
        sell_system_name = db.select(con.uni_db, "select name from 'systems' where id = '%s'" % (sell_system))[0][0]
        sell_price = i[5] #卖价
        sell_volume_remain = i[3] #库存
        sell_order_lim = i[7] #订单期限

        #筛选出买单
        buy_order = db.select(db_name, "select * from '%s' where b_or_s = 1 order by price DESC" % (table_name))
        for n in buy_order:
            con.logger.debug("筛选买单")
            buy_location_name, buy_system = db.select(con.uni_db, "select name, systems from 'H_sec_location' where id = '%s'" % (n[2]))[0] #收购地址和所在星系
            buy_system_name = db.select(con.uni_db, "select name from 'systems' where id = '%s'" % (buy_system))[0][0]
            buy_price = n[5] #收购价
            buy_volume_remain = n[3] #需求量
            buy_order_lim = n[7] #订单期限

            #计算
            #sell_price为我向别人购买的价格（别人的卖单），buy_price为我向别人出售的价格（别人的买单）
            rate_of_return = (buy_price - sell_price) / sell_price #收益率
            profit_unit = buy_price - sell_price #单位利润
            profit_total = (buy_price - sell_price) * min(buy_volume_remain, sell_volume_remain) #理论利润总额
            total_cost = sell_price * min(buy_volume_remain, sell_volume_remain) #资金占用量
            distance = 1 #距离
            score =profit_unit / type_volume #策略评分（待完善）
            #收益率小于某个数直接跳出循环
            if rate_of_return < 0.10:
                con.logger.debug("低利润，排除")
                break
            #判断有无安全路径
            if route(str(sell_system), str(buy_system)) == False:
                con.logger.debug("无安全路线，排除")
                break
            #将交易策略加入数据表
            db.insert(db_name, '''insert into contrast (
            id,
            type_id,
            en_name,
            zh_name,
            volume,
            sell_location_name,
            sell_system_name,
            sell_price,
            sell_volume_remain,
            sell_order_lim,
            buy_location_name,
            buy_system_name,
            buy_price,
            buy_volume_remain,
            buy_order_lim,
            rate_of_return,
            profit_unit,
            profit_total,
            total_cost,
            distance,
            score,
            update_code
            ) VALUES (null, '%s', '%s', '%s', %f, '%s', '%s', %.2f, %d, %d,
            '%s', '%s', %.2f, %d, %d, %f, %f, %f, %f, %d, %f, %f)''' % (
            type_id,
            type_en_name.replace("'", ''),
            type_zh_name.replace("'", ''),
            type_volume,
            sell_location_name.replace("'", ''),
            sell_system_name.replace("'", ''),
            sell_price,
            sell_volume_remain,
            sell_order_lim,
            buy_location_name.replace("'", ''),
            buy_system_name.replace("'", ''),
            buy_price,
            buy_volume_remain,
            buy_order_lim,
            rate_of_return,
            profit_unit,
            profit_total,
            total_cost,
            distance,
            score,
            update_code
            ))

            con.logger.debug("物品ID：%s 交易策略已存入" % (table_name))

    return
#判断有无安全路径
def route(origin_id, destin_id):
    rt = json.loads(http.get("route", origin_id, destin_id, avoid = '0', flag = "secure", datasource = con.datasource, user_agent = con.user_agent()))
    distance = len(rt)
    print(distance)
    print(rt)
    for i in rt:
        sec = db.check_security(str(i))
        if sec == True:
            pass
        else:
            con.logger.debug("路径中有低安星系")
            return False
    return True
#输出最终结果
def out_put():
    con.logger.info("输出结果")
    #result = cursor.execute("select * from contrast order by profit_total DESC limit 10")
    result = db.select(con.order_db, "select * from contrast order by score DESC limit 10")
    #con.logger.debug(result)
    message = []
    for i in result:
        message.append({
        "type_id" : i[1],
        "name" : "%s(%s)" % (i[2], i[3]),
        "volume" : i[4],
        "sell_location_name" : "%s(%s)(%d)" % (i[5], i[6], i[9]),
        "sell_price" : i[7],
        "sell_volume_remain" : i[8],
        "buy_location_name" : "%s(%s)(%d)" % (i[10], i[11], i[14]),
        "buy_price" : i[12],
        "buy_volume_remain" : i[13],
        "rate_of_return" : i[15],
        "profit_unit" : i[16],
        "profit_total" : i[17],
        "total_cost" : i[18],
        "distance" : i[19],
        "score" : i[20]
        })
        con.logger.info('''
        物品ID：%s,
        名称：%s(%s),
        打包体积：%f,
        出售点：%s(%s)(%d),
        售价：%.2f,
        库存：%d |
        收购点：%s(%s)(%d),
        收购价：%.2f,
        需求量：%d |
        收益率：%.3f,
        单位利润：%.2f,
        利润总额：%.2f,
        占用资金：%.2f,
        距离：%d,
        评估：%.2f
        ''' % (i[1], i[2], i[3], i[4], i[5], i[6], i[9], i[7], i[8],
        i[10], i[11], i[14], i[12], i[13],
        i[15], i[16], i[17], i[18], i[19], i[20]))
    con.logger.debug("发送邮件")
    Text(message)
    return
#文本处理
def Text(text):
    txt = ""
    for i in text:
        txt = txt + "物品ID：%s,名称：%s,打包体积：%f,出售点：%s,售价：%.2f,库存：%d | 收购点：%s,收购价：%.2f,需求量：%d | 收益率：%.3f,单位利润：%.2f,利润总额：%.2f,占用资金：%.2f,距离：%d,评估：%.2f" % (i["type_id"],
        i["name"],i["volume"],i["sell_location_name"],i["sell_price"], i["sell_volume_remain"],i["buy_location_name"],i["buy_price"],i["buy_volume_remain"],i["rate_of_return"],i["profit_unit"],i["profit_total"],i["total_cost"],i["distance"],i["score"]) + "<br>"
    mail.Sendmail(text)
    return
