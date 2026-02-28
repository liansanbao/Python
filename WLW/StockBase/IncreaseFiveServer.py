# _*_ coding: utf-8 _*_
# @Time : 2025/8/23 星期六 19:56
# @Author : 韦丽
# @Version: V 1.0
# @File : IncreaseFiveServer.py
# @desc : 涨幅(5%)以上数据采集
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

    url = f'https://w7wp557v37c1.xiaomiqiu.com/wlw?table_key=GRIDIST_STOCK&sealData={saleDay}'
    response_data = get(url)
    row_data = []
    if response_data.status_code == 200:
        json_data = json.loads(response_data.text)
        for name in json_data:
            data = [str(value) for value in dict(name).values()]
            row_data.append(data)
    return row_data

def insert(saleDay, data_list):

    tableName = 'GRIDIST_STOCK'
    insert_columns = ['CREATE_DATE', 'F12', 'F14', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7',
                      'F8', 'F9', 'F10', 'F15', 'F16', 'F17', 'F18', 'F23', 'hybk', 'DEPTHDATAURL', 'F10URL', 'REPORTCHARTURL']
    # 日期
    if saleDay == '':
        saleDay = DateTimeUtils.saleDate()

    if data_list:
        # 交易日期
        sale_date = DateTimeUtils.Format_date(ymd=saleDay, format='%Y-%m-%d')
        stock_nos = [f"'{col[1]}'" for col in data_list]
        # 先删除旧数据
        condition = f"CREATE_DATE = '{sale_date}' AND F12 IN ({', '.join(stock_nos)}) "
        # print(f'Delete condition: {condition}')
        return db.process_stock_data_insert(tableName, condition, insert_columns, data_list)

if __name__ == '__main__':
    insert(exec(''))