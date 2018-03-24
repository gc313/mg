#!/usr/bin/python3
# -*- coding: utf-8 -*-

import Module.config as con
import Module.database as db
import Module.http as http

def find_tables(db_name, update_code):
    con.logger.info("开始处理订单")
    #数据校验，删除以往数据
    db.delete(db_name, "contrast", "update_code <> %f" % (update_code))
    #获取表名
    table_names = db.select(db_name, "sqlite_master", where = "type='table' orger by name")
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
    type_volume = db.select(db.uni_db, "types", "volume", where = "id = %s" % (table_name))[0][0] #体积
    type_en_name = db.select(db.uni_db, "types", "en_name", where = "id = %s" %(table_name))[0][0]
    type_zh_name = db.select(db.uni_db, "types", "zh_name", where = "id = %s" %(table_name))[0][0]

    #筛选出卖单
    sell_order = db.select(db_name, table_name, "*", where = "b_or_s = 0 order by price")

    for i in sell_order:
        type_id = i[1] #物品ID
        sell_location_name, sell_system = db.select(db.uni_db, "H_sec_location", "name, systems", where = "id = %s" % (i[2]))[0] #出售地址和所在星系
        sell_system_name = db.select(db.uni_db, "systems", "name", where = "id = %s" % (sell_system))
        sell_price = i[5] #卖价
        sell_volume_remain = i[3] #库存
        sell_order_lim = i[7] #订单期限

        #筛选出买单
        buy_order = db.select(db_name, table_name, "*", where = "b_or_s = 1 order by price DESC")
        for n in buy_order:
            buy_location_name, buy_system = db.select(db.uni_db, "H_sec_location", "name, systems", where = "id = %s" % (n[2]))[0] #收购地址和所在星系
            buy_system_name = db.select(db.uni_db, "systems", "name", where = "id = %s" % (buy_system))
            buy_price = n[5] #收购价
            buy_volume_remain = n[3] #需求量
            buy_order_lim = n[7] #订单期限

            #计算
            #sell_price为我向别人购买的价格（别人的卖单），buy_price为我向别人出售的价格（别人的买单）
            rate_of_return = (buy_price - sell_price) / sell_price #收益率
            profit_unit = buy_price - sell_price #单位利润
            profit_total = (buy_price - sell_price) * min(buy_volume_remain, sell_volume_remain) #理论利润总额
            total_cost = sell_price * min(buy_volume_remain, sell_volume_remain) #资金占用量
            distance = 0 #距离
            score =(profit_unit + min(buy_volume_remain, sell_volume_remain)) / type_volume  #策略评分（待完善）
            #收益率小于某个数直接跳出循环
            if rate_of_return < 0.15:
                con.logger.debug("低利润，排除")
                break
            #判断有无安全路径
            if route(origin_id, destin_id) == False:
                break
            #将交易策略加入数据表
            db.insert(db_name, "contrast",
            id = "null",
            type_id = type_id,
            en_name = type_en_name,
            zh_name = type_zh_name,
            volume = type_volume,
            sell_location_name = sell_location_name,
            sell_system_name = sell_system_name,
            sell_price = sell_price,
            sell_volume_remain = sell_volume_remain,
            sell_order_lim = sell_order_lim,
            buy_location_name = buy_location_name,
            buy_system_name = buy_system_name,
            buy_price = buy_price,
            buy_volume_remain = buy_volume_remain,
            buy_order_lim = buy_order_lim,
            rate_of_return = rate_of_return,
            profit_unit = profit_unit,
            profit_total = profit_total,
            total_cost = total_cost,
            distance = distance,
            score = score,
            update_code = update_code
            )

    con.logger.debug("物品ID：%s 交易策略已存入" % (table_name))
    return
#判断有无安全路径
def route(origin_id, destin_id):
    route = json.loads(http.get("route", origin_id, destin_id, avoid = 0, flag = "secure", datasource = con.datasource, user_agent = con.user_agent())
    return
#输出最终结果
def out_put():
    con.logger.info("输出结果")
    #result = cursor.execute("select * from contrast order by profit_total DESC limit 10")
    result = db.selete(con.order_db, "contrast", "*", order_by = "score DESC", limit = "10").fetchall()
    con.logger.debug(result)
    for i in result:
        con.logger.info('''
        物品ID：%d,
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
        利润总额: %.2f,
        占用资金: %.2f,
        距离：%d,
        评估：%.2f
        ''' % (i[1], i[2], i[3], i[4], i[5], i[6], i[9], i[7], i[8],
        i[10], i[11], i[14], i[12], i[13],
        i[15], i[16], i[17], i[18], i[19], i[20]))
    return
