#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import os
import time
from datetime import datetime
import Module.http as http
import Module.config as con
import Module.database as db
import Module.select as se


#Region(星域)>Constellation(星座)>System(星系)
#获取宇宙地理数据
def get_universe_data(father, oneself):
    con.logger.debug('开始获取%s数据' % (oneself))

    #检测是否存在缓存数据文件
    data_file = con.d_path + oneself + '.json'
    if not os.path.exists(data_file):
        #获取所有地理位置的ID，用json解析
        ID = json.loads(http.get(father, oneself, datasource = con.datasource, user_agent = con.user_agent()))
        #将数据保存至json文件
        with open(data_file, 'w', encoding='utf-8') as json_file:
            json.dump(ID, json_file, ensure_ascii = False)
    else:
        #读取已有的Json文件
        with open(data_file, 'r', encoding='utf-8') as json_file:
            ID = json.load(json_file)
    #st.logger.debug('类型：%s, ID列表：%s' % (oneself, ID))

    #计数
    count = 1
    lenth = str(len(ID))

    #遍历ID
    for i in ID:
        if db.TorF(con.uni_db, oneself, str(i)) == False:
            con.logger.info("%s/%s 获取%s的数据……" % (str(count), lenth, str(i)))
            #抓取信息，用json解析
            id_info = json.loads(http.get(father, oneself, str(i), datasource = con.datasource, user_agent = con.user_agent()))
            #print(id_info)
            #调用数据库，将星域信息存储至表中
            con.logger.info('新增数据：%s ID：%s' % (oneself, str(i)))
            if oneself == 'regions':
                #星域 regions, ID, name
                db.insert(con.uni_db, "insert into regions (id, name) values ('%s', '%s')" % (str(i), id_info['name']))
            elif oneself == 'constellations':
                #星座 constellations, ID, name, 所属星域ID
                db.insert(con.uni_db, "insert into constellations (id, name, regions) values ('%s', '%s', '%s')" % (str(i), id_info['name'], str(id_info['region_id'])))
            elif oneself == 'systems':
                #星系 systems, ID, name, 所属星座ID，安全等级
                db.insert(con.uni_db, "insert into systems (id, name, constellations, security_status) values ('%s', '%s', '%s', %.3f)" % (str(i), id_info['name'], str(id_info['constellation_id']), id_info['security_status']))
        else:
            #print('跳过' + str(i))
            con.logger.debug('该%s ID：%s已存在' % (oneself, str(i)))
        count = count + 1
    return
#采集订单数据
def get_orders_data(father = "markets", oneself = "orders"):

    if not os.path.exists(con.re_j):
        get_universe_data("universe", "regions")
    else:
        with open(con.re_j,'r',encoding='utf-8') as json_file:
            order_regions_ID = json.load(json_file)
    #计数
    count = 1
    lenth = str(len(order_regions_ID))
    #生成一串数字作为识别码
    update_code = time.time()

    #按星域ID获取订单
    for i in order_regions_ID:
        con.logger.info("%s/%s 获取%s的订单……" % (str(count), lenth, str(i)))

        #获取该星域里的所有卖单 当order_type 值为“all”时，如不提供type_id则只会输出卖单
        orders_sell = json.loads(http.get(father, str(i), oneself, order_type = 'sell', datasource = con.datasource, user_agent = con.user_agent()))
        #print(orders_sell)
        for n in orders_sell:
            #筛选订单
            filter(n, update_code)
            #print(n)
        con.logger.info("卖单采集完成")

        #获取该星域里的所有买单
        orders_buy = json.loads(http.get(father, str(i), oneself, order_type = 'buy', datasource = con.datasource, user_agent = con.user_agent()))
        for j in orders_buy:
            #筛选订单
            filter(j, update_code)
        con.logger.info("买单采集完成")

        count = count + 1
    con.logger.info("所有订单采集完成")
    se.find_tables(con.order_db, update_code)

    return
#筛选
#条件：订单在高安--->单价在某个区间以内--->订单数量大于XXXXX---->剩余时间大于一天
def filter(order_data, update_code):
    location_id = order_data["location_id"]
    #判断是空间站还是其他构造体
    #空间站id类似于61000005，其他构造体id类似于1024766918117，信息获取方式和空间站不一样，先放弃
    if location_id > 99999999:
        return

    #判断地点是否在高安表中
    if db.TorF(con.uni_db, 'H_sec_location', str(location_id)) == True:
        #进入订单处理
        con.logger.debug("空间站ID：%s 已在高安表中" % (str(location_id)))
        con.logger.debug("进入订单处理")
        add_orders(order_data, update_code)

    else:
        #判断地点是否在低安表中
        if db.TorF(con.uni_db, 'L_sec_location', str(location_id)) == True:
            #跳过，分析下一个订单
            con.logger.debug("空间站ID：%s 在低安星系表中，不采集数据" % (str(location_id)))
        else:
            #向服务器获取地点所在的星系安等信息
            con.logger.info("获取空间站（ID：%s）所在星系安等信息" % (str(location_id)))

            location_info = json.loads(http.get("universe", "stations", str(location_id), datasource = con.datasource, user_agent = con.user_agent()))
            sys_ID = str(location_info["system_id"])
            #-------------------------------------------
            #判断星系安全等级
            if db.check_security(sys_ID) == True:

                db.insert(con.uni_db, "insert into H_sec_location (id, name, systems) values ('%s', '%s', '%s')" % (str(location_id), location_info["name"].replace("'", ''), sys_ID))
                #高安星系，进入订单处理
                con.logger.debug("高安星系，进入订单处理")
                add_orders(order_data, update_code)
                #print('下一步')

            else:
                #将信息加到低安表中
                con.logger.debug("将信息加到低安表中")
                db.insert(con.uni_db, "insert into L_sec_location (id, name, systems) values ('%s', '%s', '%s')" % (str(location_id), location_info["name"].replace("'", ''), sys_ID))
    return

#进一步处理订单
def add_orders(order_data, update_code):
    con.logger.debug("订单信息：%s" % order_data)
    '''
      {
    "order_id": 5091885057,
    "type_id": 21728,
    "location_id": 60003760,
    "volume_total": 1,
    "volume_remain": 1,
    "min_volume": 1,
    "price": 600000,
    "is_buy_order": false,
    "duration": 90,
    "issued": "2018-02-21T20:08:48Z",
    "range": "region"
  }
    '''
    #判断物品信息是否在types表中
    if db.TorF(con.uni_db, "types", str(order_data["type_id"])) == False:
        #向服务器获取名字
        #print(url)
        en_name = json.loads(http.get("universe", "types", str(order_data["type_id"]), datasource = con.datasource, language = "en-us", user_agent = con.user_agent()))['name']
        zh_name = json.loads(http.get("universe", "types", str(order_data["type_id"]), datasource = con.datasource, language = "zh", user_agent = con.user_agent()))['name']
        volume = json.loads(http.get("universe", "types", str(order_data["type_id"]), datasource = con.datasource, language = "en-us", user_agent = con.user_agent()))['volume']
        #将名字加入数据库
        con.logger.debug("将名字加入数据库")
        db.insert(con.uni_db, "insert into types (id, en_name, zh_name, volume) VALUES ('%s', '%s', '%s', %f)" % (str(order_data["type_id"]), en_name.replace("'", ''), zh_name, volume))
    #订单剩余时间小于2天的放弃
    #剩余时间 = 订单持续时间 - （当前UTC时间 - 下单时间）
    lim = order_data["duration"] - int((datetime.utcnow() - datetime.strptime(order_data["issued"],"%Y-%m-%dT%H:%M:%SZ")).days)
    if lim < 2:
        con.logger.debug("订单期限太短，放弃")
        return
    #订单剩余量小于1000的放弃
    if order_data["volume_remain"] < 10000:
        con.logger.debug("订单数量太少，放弃")
        return

    db.create_tb(con.order_db, str(order_data["type_id"]),
        "order_id varchar(20) primary key",
        "type_id varchar(20)",
        "location varchar(20)",
        "volume_remain integer",
        "min_volume integer",
        "price real",
        "b_or_s integer",
        "lim integer",
        "update_code real")
    #检索该表，如果有update_code列数据和目前的update_code不一致的数据，就删掉
    db.delete(con.order_db, "delete from '%s' where update_code <> %f" % (str(order_data["type_id"]), update_code))

    #判断买/卖单
    if order_data["is_buy_order"] == True:
        con.logger.debug("买单")
        b_or_s = 1
    else:
        con.logger.debug("卖单")
        b_or_s = 0
    #插入数据
    db.insert(con.order_db, '''insert into '%s' (order_id, type_id, location, volume_remain, min_volume, price, b_or_s,lim, update_code
    ) VALUES ('%s', '%s', '%s', %d, %d, %.2f, %d, %d, %f)''' % (str(order_data["type_id"]), str(order_data["order_id"]), str(order_data["type_id"]),
        str(order_data["location_id"]),
        order_data["volume_remain"],
        order_data["min_volume"],
        order_data["price"],
        b_or_s,
        lim,
        update_code
        ))

    return
