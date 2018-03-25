#!/usr/bin/python3
# -*- coding: utf-8 -*-
#这个模块的代码基本都是抄的，还没完全搞懂它的意思

#导入发邮件所需模块
import smtplib
import email.mime.multipart
import email.mime.text

from datetime import date
def Text(text):

	return

def Sendmail(message):

	today = str(date.today())
	from_addr = "big_sister@yeah.net"
	paswd = "raspberry3b"
	to_addr = "gc313@qq.com"
	smtp_server = "smtp.yeah.net"


	msg = email.mime.multipart.MIMEMultipart()
	msg["From"] = "市场观察员"
	msg["To"] = to_addr
	msg["Subject"] = "市场观测报告" + today
	content = str(message)
	txt = email.mime.text.MIMEText(content, "html", "utf-8")
	#print(txt)
	#print('------------------------------------')
	msg.attach(txt)
	#print(msg)

	server = smtplib.SMTP()
	server.connect(smtp_server, "25")
	server.login(from_addr, paswd)
	server.sendmail(from_addr, [to_addr], str(msg))
	server.quit()
if __name__ == "__main__":
    Sendmail("来自电路板的问候！")
