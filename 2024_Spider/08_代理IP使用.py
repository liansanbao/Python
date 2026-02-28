# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/3/23 15:28
# @Author : 连三保
# @Version: V 1.0
# @File : 08_代理IP使用.py
# @desc : 代理IP的使用

# SSL 安全认证
''' http协议
    https协议 >> http + ssl 加密
   解决方案：requests.get(url, verify=False) 就能避开SSL验证
'''
import random
import requests
from retrying import retry

'''
反爬
   根据IP地位来控制你不能访问
   获取路由器IP来限制你，不让你爬取
   
   解决方案：
   代理IP池
      使用场景：短时间内多次访问同一个服务器 1s/100次
      用户代理池:每一次请求都使用一个不同的UA值，成功伪装身份，骗过服务器
      cookie池：每一次请求都使用一个不同的cookie值，成功伪装身份，骗过服务器
      
      
   代理IP分类：
        1.透明代理：毫无作用，服务器可以简单的检测到你使用了代理IP，并且知道你的真实IP
        2.匿名代理：服务器可以简单的检查到你使用了代理IP，但是不知道你的真实IP
        3.高匿代理：服务器检测不到你使用了代理IP，也无法知道你的真实IP  建议使用这个 https://www.tianqiip.com/manager/whiteListIp
        
        添加IP白名单
            https://ip.orz.tools/
    
   retry是一个三层函数的嵌套，并且返回了内部函数的引用，闭包三层 >> 有参数的装饰器
'''

# 付费版代理IP取得 需要替换一下URL
def getProxies(num: int = 1):
    url = f'http://api.tianqiip.com/getip?secret=msqo66gmf1kowk4r&num={num}&type=txt&port=1&time=15&mr=1&sign=7ac6fe515547dd7a55ea9e6ac1d3b5ae'
    ip_list = []
    response = requests.get(url=url)
    if response.status_code == 200:
        # 出力的IP：110.90.14.41:40011\r\n，需要替换\r\n
        ip_str = response.text.split('\r\n')
        ip_list.extend([ip for ip in ip_str if ip != ''])

    return ip_list

if __name__ == '__main__':
    url = 'http://myip.ipip.net'

    header = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0'
    }

    proxies_list = getProxies(1)
    # proxies_list = ['180.110.120.195:40031', '']

    for value in proxies_list:
        try:
            # 构造代理IP字典
            # 1.1代理IP字典中的键名（协议头）-> 需要更请求的url协议头保持一致
            # 1.2代理IP字典中的键值 -> 协议头://IP地址
            proxies_1 = {'http': f'http://{value}'}

            print(proxies_1)

            # 第二种 代理IP网址里设定的保持一致
            # 2.1代理IP字典中的键名（协议头）-> 需要更请求的url协议头保持一致
            # 2.2代理IP字典中的键值 -> 协议头://IP地址
            # proxies_2 = {'http': 'http://182.202.13.253:40009'}

            # 代理IP池的构造，主要解决IP无效时
            proxies_List = ['', '', '']
            ip = random.choice(proxies_List)

            if value != '':
                response = requests.get(url=url, headers=header, proxies=proxies_1, timeout=3)
            else:
                response = requests.get(url=url, headers=header, timeout=3)

            print(response.text)
        except Exception as ex:
            print(ex)
