#!/usr/bin/python3
# -*- coding: utf-8 -*-

import Module.database as db
import Module.handler as hd
import Module.config as con

#初始化
def init_table():

    #建立数据表  db_name, table_name, *args
    #-----UNIVERSE.db-----
    #星域表
    db.create_tb(con.uni_db, "regions", "id varchar(20) primary key", "name varchar(20)")
    #星座表
    db.create_tb(con.uni_db, "constellations", "id varchar(20) primary key", "name varchar(20)", "regions varchar(20)")
    #星系表
    db.create_tb(con.uni_db, "systems", "id varchar(20) primary key", "name varchar(20)", "constellations varchar(20)", "security_status real")
    #高安空间站表
    db.create_tb(con.uni_db, "H_sec_location", "id varchar(20) primary key", "name varchar(20)", "systems varchar(20)")
    #低安空间站表
    db.create_tb(con.uni_db, "L_sec_location", "id varchar(20) primary key", "name varchar(20)", "systems varchar(20)")
    #物品表
    db.create_tb(con.uni_db, "types", "id varchar(20) primary key", "en_name varchar(125)", "zh_name varchar(125)", "volume real")
    #------ORDERS.db-----
    #交易策略表
    db.create_tb(con.order_db, "contrast",
    "id integer primary key autoincrement", #id
    "type_id varchar(20)", #物品id
    "en_name varchar(80)", #英文名
    "zh_name varchar(80)", #中文名
    "volume real", #体积（打包后）
    "sell_location_name varchar(20)",  #出售点
    "sell_system_name varchar(20)", #星系名
    "sell_price real", #售价
    "sell_volume_remain integer", #库存
    "sell_order_lim integer", #卖单期限
    "buy_location_name varchar(20)", #收购点
    "buy_system_name varchar(20)", #星系名
    "buy_price real", #收购价
    "buy_volume_remain integer", #需求量
    "buy_order_lim integer", #买单期限
    "rate_of_return real", #收益率
    "profit_unit real", #单位利润
    "profit_total real", #利润总额
    "total_cost real", #资金占用量
    "distance integer", #距离
    "score real", #评估
    "update_code real" #校验码
    )

    return

def init_list():
    #获取星域数据
    hd.get_universe_data("universe", "regions")
    #获取星座数据
    hd.get_universe_data("universe", "constellations")
    #获取星系数据
    hd.get_universe_data("universe", "systems")
    return
