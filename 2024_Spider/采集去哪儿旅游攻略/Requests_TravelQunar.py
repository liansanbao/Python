# _*_ coding: utf-8 _*_
# @Time : 2025/4/19 22:07
# @Author : 韦丽
# @Version: V 1.0
# @File : Requests_TravelQunar.py
# @desc : 使用python采集去哪儿旅游攻略 网站：https://travel.qunar.com/travelbook/list.htm?order=hot_heat

'''
    要求：
        1.爬取攻略库的200页数据
        2.数据内容应该包括：'攻略地点','短评','浏览量','出发日期','天数','人均费用','人物','玩法','详情页'
        3.数据保存：Excel一份，数据存储于MongoDB或MySQL一份
        4.使用一种反爬方法
'''
import time

import pandas
import requests
from lxml import etree
from fake_useragent import FakeUserAgent
from pymongo import MongoClient

# 付费版代理IP取得 需要替换一下URL
def getProxies(num: int = 1):
    url = f'http://api.tianqiip.com/getip?secret=msqo66gmf1kowk4r&num={num}&type=txt&port=1&time=3&mr=1&sign=7ac6fe515547dd7a55ea9e6ac1d3b5ae'
    ip_list = []
    response = requests.get(url=url)
    if response.status_code == 200:
        # 出力的IP：110.90.14.41:40011\r\n，需要替换\r\n
        ip_str = response.text.split('\r\n')
        ip_list.extend([ip for ip in ip_str if ip != ''])

    return ip_list

# get请求发送
def get(url, isDaili: bool=False, proxies_List: dict={}):
    # 4.使用一种反爬方法 UA是随机生成的
    header = {
        'User-Agent': FakeUserAgent().random,
    }

    if isDaili:
        # print(f'URL:{url}, IP代理：{proxies_List}')
        return requests.get(url=url, headers=header, proxies=proxies_List, timeout=2)

    return requests.get(url=url, headers=header)

# text值取得
def getText(li):
    text_list = li
    if text_list != None and len(text_list) != 0:
        return text_list[0]
    return ''

# 获取每页的短评链接
def getDetail_Url():
    detail_Urls = []
    # 1.爬取攻略库的200页数据
    for page in range(1, 3):
        retry_count = 0
        url = f'https://travel.qunar.com/travelbook/list.htm?page={page}&order=hot_heat'
        print(f'第{page}页URL： {url}')
        while retry_count < 10:
            try:
                response = get(url)
                if response.status_code == 204:
                    raise Exception('触发重试')

                # html数据
                html_data = etree.HTML(response.text)
                detail_elements = html_data.xpath('//li/h2/a/@href')
                detail_list = ['https://travel.qunar.com' + str(a) for a in detail_elements]
                detail_Urls.extend(detail_list)
                break
            except:
                retry_count += 1
                # print(f'触发{retry_count}次请求！')
    print(len(detail_Urls))
    return detail_Urls

# 详情页面数据处理
def detailData(detail_Urls):
    detail_data = []
    proxies_Lists_data = []
    # IP代理 ['171.110.94.131:40024', '119.130.165.33:40015'] ['125.109.46.9:40029', '183.141.142.90:40027', '113.76.205.250:40001']
    # proxies_Lists = getProxies(1)
    proxies_Lists = ['']
    proxies_Lists_data.append(proxies_Lists)
    print(f'生成IP代理：{proxies_Lists}')
    start_time = time.time()
    print(f'计时开始时间：{start_time}')
    # 2.数据内容应该包括：'攻略地点','短评','浏览量','出发日期','天数','人均费用','人物','玩法','详情页'
    for no, url in enumerate(detail_Urls):
        retry_count = 1

        rowData = {}
        current_time = time.time()
        if current_time - start_time >= 178:
            print(f'计时结束时间：{current_time}')
            start_time = time.time()
            print(f'计时开始时间：{start_time}')
            # proxies_Lists = getProxies(1)
            proxies_Lists_data.append(proxies_Lists)
            print(f'生成IP代理：{proxies_Lists}')

        while retry_count < 2:
            try:
                response = get(url, False, {'https': f'http://{proxies_Lists[0]}'})
                # html数据
                html_data = etree.HTML(response.text)
                # 攻略地点 strategy_location
                rowData["攻略地点"] = getText(html_data.xpath('//p[@class="b_crumb_cont"]/a[2]/text()'))
                # 短评 short_comment
                rowData["短评"] = getText(html_data.xpath('//div[@class="user_info"]/div/h1/span/text()'))
                # 浏览量 page_view
                rowData["浏览量"] = getText(html_data.xpath('//li[@class="date"]/span[3]/text()'))
                # 出发日期 departure_date
                rowData["出发日期"] = getText(html_data.xpath('//li[@class="f_item when"]/p/span[2]/text()'))
                # 天数 dasys
                rowData["天数"] = getText(html_data.xpath('//li[@class="f_item howlong"]/p/span[2]/text()'))
                # 人均费用 per_capita_cost
                rowData["人均费用"] = getText(html_data.xpath('//li[@class="f_item howmuch"]/p/span[2]/text()'))
                # 人物 character
                rowData["人物"] = getText(html_data.xpath('//li[@class="f_item who"]/p/span[2]/text()'))
                # 玩法 gameplay
                rowData["玩法"] = getText(html_data.xpath('//li[@class="f_item how"]/p/span[2]//text()'))
                # 详情页 details_page
                rowData["详情页"] = url
                if (rowData["攻略地点"] == ''):
                    raise Exception('触发重试')
                print(f'第{no + 1}个详情页URL： {url}, 数据：{rowData}')
                detail_data.append(rowData)
                break
            except Exception as e:
                retry_count += 1
                # print(f'触发{retry_count}次请求！')
        else:
            # 详情页 details_page
            rowData["详情页"] = url
            # print(rowData)
            # detail_data.append(rowData)
    print(f'一共使用了{len(proxies_Lists_data)}个IP代理：{proxies_Lists_data}')
    return detail_data

# 出力execl文件
def save_execl(detail_data):
    df = pandas.DataFrame(detail_data)
    df.to_excel(f'crawl_qunar.xlsx', index=False)

# MongoDB中保存
def save_mongodb(detail_data):
    with MongoClient(host='192.168.1.6', port=27017) as con:  # 实例化mongoclient
        collection = con['travelQunarSpider']['crawl_qunar']
        for py_dict in detail_data:
            with con.start_session() as session:
                session.start_transaction()
                try:
                    # 以详情页作为更新条件，upsert=True不满足就进行插入操作
                    resutl = collection.update_one(
                        {'详情页': py_dict['详情页']},
                        {'$set': py_dict},
                        upsert=True,
                        session=session
                    )
                    print(f'更新件数： {resutl.modified_count}')
                    session.commit_transaction()
                except Exception as e:
                    session.abort_transaction()

# 去哪儿旅游攻略数据采集主处理
def exec():
    # 1.获取详情页链接数据
    detail_Urls = getDetail_Url()
    # 2.获取详情页数据
    detail_data = detailData(detail_Urls)
    print(f'一共采集到{len(detail_data)}件数据')
    # 3.数据保存：Excel一份，数据存储于MongoDB或MySQL一份
    #   execl中保存
    save_execl(detail_data)
    #   MongoDB中保存
    save_mongodb(detail_data)

if __name__ == '__main__':
    exec()
    # response = get('https://www.baidu.com',False, {}, 'https://zvon.org/comp/r/tut-XPath_1.html')
    # print(f'访问结果： {response.url}')
    # import urllib.request
    # response = urllib.request.urlopen('https://python.org')
    # print(response.getcode())