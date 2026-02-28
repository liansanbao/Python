# _*_ coding: utf-8 _*_
# @Time : 2025/6/24 0024 21:57
# @Author : 韦丽
# @Version: V 1.0
# @File : ZhuLiZiJinServer.py
# @desc : 涨停板数据采集
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

    url = f'https://w7wp557v37c1.xiaomiqiu.com/wlw?table_key=DAILYLIMIT_CRAWL&sealData={saleDay}'
    response_data = get(url)
    row_data = []
    if response_data.status_code == 200:
        json_data = json.loads(response_data.text)
        for name in json_data:
            data = [str(value) for value in dict(name).values()]
            row_data.append(data)
    return row_data

def insert(saleDay, data_list):
    tableName = 'STOCK_INFO_WLW'
    insert_columns = [
        'STOCK_DATE',
        'STOCK_NO',
        'STOCK_NAME',
        'ZUI_XING_JIA',
        'ZHANG_DIE_FU',
        'YOU_ZI_YOU_WU',
        'CHENG_JIAO_E',
        'LIU_TONG_SHI_ZHI',
        'ZONG_SHI_ZHI',
        'HUAN_SHOU_LV',
        'FENG_BAN_JIN_E',
        'FIRST_FENG_BAN_TIME',
        'LAST_FENG_BAN_TIME',
        'ZHA_BAN_CI_SHU',
        'ZHANG_TING_TOTAL',
        'LIAN_BAN_SHU',
        'SUO_SHU_HANG_YE',
        'LIMIT_TITLE',
        'LIMIT_WHY',
        'CONCEPT',
        'DEPTHDATAURL',
        'F10URL',
        'REPORTCHARTURL'
        ]
    # 日期
    if saleDay == '':
        saleDay = DateTimeUtils.saleDate()

    if data_list:
        # 交易日期
        sale_date = DateTimeUtils.Format_date(ymd=saleDay, format='%Y-%m-%d')
        stock_nos = [f"'{col[1]}'" for col in data_list]
        # 先删除旧数据
        condition = f"STOCK_DATE = '{sale_date}' AND STOCK_NO IN ({', '.join(stock_nos)}) "
        # print(f'Delete condition: {condition}')
        return db.process_stock_data_insert(tableName, condition, insert_columns, data_list)

if __name__ == '__main__':
    list = exec('20250715')
    for item in list:
        print(f'item: {item}')
