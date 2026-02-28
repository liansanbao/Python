# _*_ coding: utf-8 _*_
# @Time : 2025/8/23 星期六 20:33
# @Author : 韦丽
# @Version: V 1.0
# @File : StockHoldingServer.py
# @desc : 机构持股统计数据采集
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
        saleDay = DateTimeUtils.get_quarter_dates()['end_date']

    url = f'https://w7wp557v37c1.xiaomiqiu.com/wlw?table_key=STOCK_HOLDING&sealData={saleDay}'
    response_data = get(url)
    row_data = []
    if response_data.status_code == 200:
        json_data = json.loads(response_data.text)
        for name in json_data:
            data = [str(value) for value in dict(name).values()]
            row_data.append(data)
    return row_data

def insert(saleDay, data_list):

    tableName = 'STOCK_HOLDING'
    insert_columns = ['STOCK_CODE', 'STOCK_NAME', 'REPORT_DATE', 'INDUSTRY', 'INSTITUTION_COUNT', 'HOLDING_QUANTITY', 'HOLDING_VALUE', 'TOTAL_SHARE_RATIO', 'FLOAT_SHARE_RATIO',
                      'CHANGE_QUANTITY', 'CHANGE_RATIO', 'POSITION_TYPE', 'create_time', 'update_time']
    # 日期
    if saleDay == '':
        saleDay = DateTimeUtils.get_quarter_dates()['end_date']

    if data_list:
        # 交易日期
        sale_date = DateTimeUtils.Format_date(ymd=saleDay, format='%Y-%m-%d')
        stock_nos = [f"'{col[0]}'" for col in data_list]
        # 先删除旧数据
        condition = f"REPORT_DATE = '{sale_date}' AND STOCK_CODE IN ({', '.join(stock_nos)}) "
        # print(f'Delete condition: {condition}')
        return db.process_stock_data_insert(tableName, condition, insert_columns, data_list)

if __name__ == '__main__':
    insert(exec(''))
