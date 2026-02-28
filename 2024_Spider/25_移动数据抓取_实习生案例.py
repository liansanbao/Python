# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/4/2 11:23
# @Author : 连三保
# @Version: V 1.0
# @File : 25_移动数据抓取.py
# @desc :
import os
import re
import time

from lxml import etree
import requests
from fake_useragent import FakeUserAgent
from Base.FrontTools import parser_font


# 请求发送
def request(url):
    header = {
        'User-Agent': FakeUserAgent().random,
        'Cookie':'__jsluid_s=c451719738965d16b77e48b2e2f1580a; utm_source_first=PC; utm_source=PC; utm_campaign=PC; position=pc_default; Hm_lvt_03465902f492a43ee3eb3543d81eba55=1743570561,1744874858; Hm_lpvt_03465902f492a43ee3eb3543d81eba55=1744874858; HMACCOUNT=1EC3CBA735DA52C1'
    }
    time.sleep(2)
    return requests.get(url=url, headers=header)

# 字体文件下载
def downloadWoff(woff_url, woff_name):
    if not os.path.exists(woff_name):
        woff_response = request(woff_url)
        if woff_response.status_code == 200:
            with open(woff_name, 'wb') as write:
                write.write(woff_response.content)


if __name__ == '__main__':
    url = 'https://www.shixiseng.com/interns?keyword=python&city=%E5%85%A8%E5%9B%BD&type=intern'
    response = request(url)
    if response.status_code == 200:
        # 数据
        str_data = response.text

        # 提取字体文件 src:url(https://sxsimg.xiaoyuanzhao.com/static_sxs/dist/desktop/dist/client/fonts/element-icons.313f7da.woff)
        woff_url = 'https://www.shixiseng.com' + re.findall(r'src: url\((.*?)\);', str_data)[0]
        print(woff_url)
        woff_name = 'shixiseng.woff'
        downloadWoff(woff_url, woff_name)

        res = parser_font(woff_name)
        print(f'字体文件{woff_name}内容：{res}')

        # html数据
        html_data = etree.HTML(str_data)

        # 定位包含所有的数据
        divs = html_data.xpath(' //div[@searchtype="intern"]')
        for div in divs:
            # 提取岗位名称
            job_name = div.xpath('.//a[@class="title ellipsis font"]/text()')[0]

            for k, v in res.items():
                job_name = job_name.replace(k, v, -1).replace('v十', 'y', -1)

            # 提取岗位薪资
            money = div.xpath('.//span[@class="day font"]/text()')[0]

            for k, v in res.items():
                money = money.replace(k, v, -1).replace('o','0', -1)

            # 提取公司名称
            company = div .xpath('.//a[@class="title ellipsis"]/text()')[0]

            for k, v in res.items():
                company = company.replace(k, v, -1)

            print(job_name, money, company)