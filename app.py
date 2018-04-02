#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time
from datetime import datetime
import Module.initialization as ini
import Module.handler as hd
import Module.select as se
import Module.config as con
import Module.sendmail as mail

if __name__ == "__main__":

#采用crontab定时运行
	try:
		con.logger.info("主程序运行")
		ini.init_table() #初始化表格
		#ini.init_list() #采集地理数据
		hd.get_orders_data() #采集订单数据
		#se.find_tables(con.order_db, 1234) #测试用
		se.out_put() #输出
		#se.route('30000002', '30001688') #测试用
	except Exception as e:
		con.logger.warning("程序报错:%s" % (e))
		con.logger.exception("程序报错")
		traceback.print_exc(file = open("error.txt","w+"))
		mail.Sendmail("程序报错:%s" % (e))
	finally:
		con.logger.info("程序结束运行")
	#ini.init_table() #初始化表格
	#ini.init_list() #采集地理数据
	#hd.get_orders_data() #采集订单数据
	#se.find_tables(con.order_db, 1234) #测试用
	#se.out_put() #输出
