# _*_ coding: utf-8 _*_
# @Time : 2025/6/24 0024 20:15
# @Author : 韦丽
# @Version: V 1.0
# @File : WaringStockServer.py
# @desc : 风险个股数据采集

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

    url = f'https://w7wp557v37c1.xiaomiqiu.com/wlw?table_key=STOCK_INFO_QUESTION&sealData={saleDay}'
    response_data = get(url)
    row_data = []
    if response_data.status_code == 200:
        json_data = json.loads(response_data.text)
        for name in json_data:
            data = [str(value) for value in dict(name).values()]
            row_data.append(data)

    return row_data

def insert(data_list):
    insert_columns = ['STOCK_NO', 'STOCK_NA', 'STOCK_TYPE', 'STOCK_TYPE_LNAME', 'U_DATE', 'C_DATE', 'AN_QUAN_FENG', 'SUO_SHU_HANG_YE', 'YU_JING_TYPE', 'YU_JING_XIANG_QI']
    tableName = 'STOCK_INFO_QUESTION'
    if data_list:
        # 股票NO
        stock_nos = [f"'{col[0]}'" for col in data_list]
        # 风险种类
        stock_types = [f"'{col[2]}'" for col in data_list]
        # 先删除旧数据
        condition = f"STOCK_NO IN ({', '.join(stock_nos)}) AND STOCK_TYPE IN ({', '.join(stock_types)})"
        db.process_stock_data_insert(tableName, condition, insert_columns, data_list)

def insertServere(data_list):
    insert_columns = ['STOCK_NO', 'STOCK_NA', 'STOCK_TYPE', 'STOCK_TYPE_LNAME', 'U_DATE', 'C_DATE', 'AN_QUAN_FENG', 'SUO_SHU_HANG_YE', 'YU_JING_TYPE', 'YU_JING_XIANG_QI']
    tableName = 'STOCK_INFO_QUESTION'
    if data_list:
        # 先删除旧数据
        condition = f" 1 = 1"
        db.process_stock_data_insert(tableName, condition, insert_columns, data_list)

if __name__ == '__main__':
    insert(exec())
