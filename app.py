#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time
from datetime import datetime
import Module.initialization as ini
import Module.handler as hd
import Module.select as se
import Module.config as con
'''
def Now():
	return str(datetime.now())[:19]
'''

if __name__ == "__main__":
	'''
	try:
		con.logger.info('程序运行')
		while 1:

			#定时运行
			run_time = Now()[11:13]
			if run_time == "00" or run_time == "11":
				con.logger.info('开始采集数据')
				hd.get_orders_data()
			time.sleep(3000)
	except Exception as e:
		con.logger.info("程序报错%s" % (e))
	finally:
		con.logger.info("程序结束运行")
	'''
	ini.init_table() #初始化表格
	#ini.init_list() #采集地理数据
	hd.get_orders_data() #采集订单数据
	#se.find_tables(con.order_db, 1234)
	se.out_put() #输出
	#se.route('30000002', '30001688')
