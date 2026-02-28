# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/3/23 14:03
# @Author : 连三保
# @Version: V 1.0
# @File : Requests_Cookie.py
# @desc : 爬虫复习:requests.session() 针对先登录之后进行操作
import json
import time

import requests


# 网络请求处理
def getRequests(url : str=''):
    if url == '':
        return None

    # header 设定
    header = {
        'Cookie':'Hm_lvt_9c5f07b6ce20e3782eac91ed47d1421c=1742712184; Hm_lpvt_9c5f07b6ce20e3782eac91ed47d1421c=1742712184; HMACCOUNT=1EC3CBA735DA52C1',
        # 回话记录设定
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0'
    }
    return requests.get(url=url, headers=header)

# post请求不需要带Cookie
def postRequests(url:str = '', form:list=[]):
    # header 设定
    header = {
        # 回话记录设定
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0'
    }

    session = requests.session()
    return session.post(url=url, headers=header, data=from_data)
    # return requests.post(url=url, headers=header, data=from_data)

if __name__ == '__main__':
    # 爬取的URL
    url = 'https://www.bg90.cc/user/login.html'

    from_data = {
        'action':'login',
        'username':'18217623705',
        'password':'bg90+2025'
    }

    # Response = getRequests(url)
    # Response = postRequests(url, from_data)

    # header 设定
    header = {
        # 回话记录设定
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0'
    }

    session = requests.session()
    session.post(url=url, headers=header, data=from_data)

    # coookie 输出
    print(session.cookies)

    time.sleep(6)

    notify = session.get('https://www.biqu05.cc/user/action.html?action=bookcase&t=1742713948376', headers=header)
    str_data = notify.text

    print(json.loads(str_data))





