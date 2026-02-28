import json

import requests
from fake_useragent import FakeUserAgent

from WLW.StockBase import DateTimeUtils
from WLW.StockBase.sqlite_db import SQLiteDB

# SHowWLW执行时的设定
from WLW.Tools.LoggingEx import logger

db = SQLiteDB()

def getData(year: str = '1988'):
    selectSql = f"""select year, month, strftime('%Y%m%d', holidays) , holidays_content from China_Holidays where year = {year}"""
    return db.process_stock_data_select(selectSql)

def getDataCount(year: str = ''):
    sql = f"""select count() from China_Holidays where year = {year}"""
    data = db.process_stock_data_select(sql)
    if len(data) == 1:
        return data[0][0]
    return 0

def insert(year, data_list):
    # 数据插入
    insert_columns = [
        'year',
        'month',
        'holidays',
        'holidays_content'
    ]

    # 数据操作
    if data_list:
        tableName = 'China_Holidays'
        # 先删除旧数据
        condition = f" year  = {year} "
        return db.process_stock_data_insert(tableName, condition, insert_columns, data_list)

def get(url):
    header = {
        'User-Agent': FakeUserAgent().random
    }
    return requests.get(url=url, headers=header)

def exec(saleDay:str = ''):
    # 日期
    if saleDay == '':
        nowdate = DateTimeUtils.saleDate()
        saleDay = DateTimeUtils.Format_date(ymd=nowdate, format='%Y')

    url = f'http://46zllpjb6g5c.xiaomiqiu.com/wlw?table_key=China_Holidays&sealData={saleDay}'
    response_data = get(url)
    row_data = []
    if response_data.status_code == 200:
        json_data = json.loads(response_data.text)
        for name in json_data:
            data = [str(value) for value in dict(name).values()]
            row_data.append(data)

        logger.info(f'row_data: {row_data}')
    return row_data



if __name__ == '__main__':
    print(getData(year='2025'))