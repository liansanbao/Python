# _*_ coding: utf-8 _*_
# @Time : 2025/8/23 星期六 19:56
# @Author : 韦丽
# @Version: V 1.0
# @File : IncreaseFiveServer.py
# @desc : A股公告数据采集
import json
import requests
from fake_useragent import FakeUserAgent

from WLW.StockBase import DateTimeUtils
from WLW.StockBase.sqlite_db import SQLiteDB

db = SQLiteDB()

def get(url):
    header = {
        'User-Agent': FakeUserAgent().random
    }
    return requests.get(url=url, headers=header, timeout=30)

def exec(saleDay:str = ''):
    # 日期
    if saleDay == '':
        saleDay = DateTimeUtils.saleDate()

    url = f'https://w7wp557v37c1.xiaomiqiu.com/wlw?table_key=A_NOTICES&sealData={saleDay}'
    response_data = get(url)
    row_data = []
    if response_data.status_code == 200:
        json_data = json.loads(response_data.text)
        for name in json_data:
            data = [str(value) for value in dict(name).values()]
            row_data.append(data)
    return row_data

def insert(saleDay, data_list):

    tableName = 'NOTICE_CRAWL'
    insert_columns = ['ART_CODE', 'STOCK_CODE', 'STOCK_NAME', 'NOTICE_DATE', 'NOTICE_TYPE', 'NOTICE_TITLE', 'NOTICE_INFO_URL', 'INDUSTRY', 'create_time', 'update_time']
    # 日期
    if saleDay == '':
        saleDay = DateTimeUtils.saleDate()

    if data_list:
        # 公告code
        art_codes = [f"'{col[0]}'" for col in data_list]
        # 先删除旧数据
        condition = f"ART_CODE IN ({', '.join(art_codes)}) "
        # print(f'Delete condition: {condition}')
        return db.process_stock_data_insert(tableName, condition, insert_columns, data_list)

if __name__ == '__main__':
    insert(exec(''))