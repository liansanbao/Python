# _*_ coding: utf-8 _*_
# @Time : 2025/8/23 星期六 20:16
# @Author : 韦丽
# @Version: V 1.0
# @File : PlateFundServer.py
# @desc : 板块资金数据采集
import json
import requests
from fake_useragent import FakeUserAgent

from WLW.StockBase import DateTimeUtils
from WLW.StockBase.sqlite_db import SQLiteDB
from WLW.Tools.LoggingEx import logger

db = SQLiteDB()

def get(url):
    header = {
        'User-Agent': FakeUserAgent().random
    }
    return requests.get(url=url, headers=header, timeout=30)

def exec(saleDay:str = ''):
    try:
        # 日期
        if saleDay == '':
            saleDay = DateTimeUtils.saleDate()

        url = f'https://w7wp557v37c1.xiaomiqiu.com/wlw?table_key=HYZJL_CRAWL&sealData={saleDay}'
        response_data = get(url)
        row_data = []
        if response_data.status_code == 200:
            json_data = json.loads(response_data.text)
            for name in json_data:
                data = [str(value) for value in dict(name).values()]
                row_data.append(data)
        return row_data
    except Exception as ex:
        logger.error(f'ERROR: {str(ex)}')

# 数据采集时数据删除
def delete(saleDay):
    tableName = 'HYZJL_CRAWL'
    # 先删除旧数据
    sale_date = DateTimeUtils.Format_date(ymd=saleDay, format='%Y-%m-%d')
    condition = f"strftime('%Y-%m-%d', CREATE_DATE) = '{sale_date}' "
    db.process_stock_data_delete(tableName, condition)

# 系统退出时，动态数据删除
def deleteType(saleDay: str = ''):
    tableName = 'HYZJL_CRAWL'
    # 日期
    if saleDay == '':
        saleDay = DateTimeUtils.saleDate()
    # 先删除旧数据
    sale_date = DateTimeUtils.Format_date(ymd=saleDay, format='%Y-%m-%d')
    condition = f"ActivateType = 0 and strftime('%Y-%m-%d', CREATE_DATE) < '{sale_date}' "
    db.process_stock_data_delete(tableName, condition)

def insert(saleDay, data_list):

    tableName = 'HYZJL_CRAWL'
    insert_columns = ['CREATE_DATE', 'F12', 'F14', 'F2', 'F3', 'F62', 'F184', 'F66', 'F69',
                      'F72', 'F75', 'F78', 'F81', 'F84', 'F87', 'F204', 'F205', 'ActivateType', 'hyType']
    # 日期
    if saleDay == '':
        saleDay = DateTimeUtils.saleDate()

    if data_list:
        # 交易日期
        # sale_date = DateTimeUtils.Format_date(ymd=saleDay, format='%Y-%m-%d')
        # stock_nos = [f"'{col[1]}'" for col in data_list]
        # 先删除旧数据
        # condition = f"CREATE_DATE = '{sale_date}' AND F12 IN ({', '.join(stock_nos)}) "
        # print(f'Delete condition: {condition}')
        return db.process_stock_data_insert(tableName, "", insert_columns, data_list)

if __name__ == '__main__':
    insert(exec(''))