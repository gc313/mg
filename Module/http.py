#!/usr/bin/python3
# -*- coding: utf-8 -*-
import urllib.request
import time
import Module.config as con

def get(*args, **kw):
    #加不来header，手动构建URL
    #增加将不是字符串的参数都转换为字符串的代码
    head = con.api_url
    body = "/".join(args) + "/"
    #超棒的写法，我要好好记住,把键：值从kw里取出来组合后用&隔开
    tail = "&".join(key+"="+str(value) for key, value in kw.items())
    URL = head + body + '?' + tail


    #请求网页
    con.logger.debug('请求网页%s' % (URL))
    req = urllib.request.Request(URL)

    #初始化重试次数
    retry = 0
    while 1:
        try:
            #获取数据
            con.logger.debug('开始请求数据')
            with urllib.request.urlopen(req, timeout = 30) as resp:
                resp = resp.read().decode('utf-8')
            return resp
        except Exception as e:
            #发生异常时重试
            con.logger.warning('连接异常：%s' % e)
            retry = retry + 1
            if retry > 10:
                con.logger.error('无法从服务器获取数据，开始下一个请求。')
                return
                #os._exit(0)
            else:
                con.logger.warning('重试第 %s 次' % retry)
                time.sleep(10)
    return
