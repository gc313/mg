#!/usr/bin/python3
# -*- coding: utf-8 -*-
import Module.initialization as ini
import Module.handler as hd
import Module.select as se
import Module.config as con

if __name__ == "__main__":

    #ini.init_table() #初始化表格
    #ini.init_list() #采集地理数据
    hd.get_orders_data() #采集订单数据
    #se.find_tables(con.order_db, 123456)
    se.out_put() #输出
    #se.route('30000002', '30001688')
