# _*_ coding: utf-8 _*_
# @Time : 2025/10/16 星期四 21:30
# @Author : 韦丽
# @Version: V 1.0
# @File : WlwAllServer.py
# @desc : 采集所有的数据
import datetime
import json
import requests
from fake_useragent import FakeUserAgent

from WLW.StockBase import DateTimeUtils
from WLW.StockBase.sqlite_db import SQLiteDB
from WLW.model import DataOpreationModel

db = SQLiteDB()

def post(url, data):
    header = {
        'User-Agent': FakeUserAgent().random
    }
    return requests.post(url=url, headers=header, data=data, timeout=30)

def exec(saleDay:str = ''):
    # 日期
    if saleDay == '':
        saleDay = DateTimeUtils.saleDate()

    # 风险个股数据是否采集判断
    siq_saleDay = saleDay
    yearMonth = datetime.datetime.today().strftime('%Y%m')
    # 交易日期
    yearMonthDom = str(DataOpreationModel.getDataInterval('STOCK_INFO_QUESTION'))
    if yearMonthDom == yearMonth:
        siq_saleDay = ''

    url = f'https://w7wp557v37c1.xiaomiqiu.com/wlwAll?table_key=WLW_ALL'
    data = {
        'D_SALEDAY': saleDay,
        # 'M_SALEDAY': saleDay,
        'I_SALEDAY': saleDay,
        'P_SALEDAY': DateTimeUtils.plateSaleDate(),
        'S_SALEDAY': DateTimeUtils.get_quarter_dates()['end_date'],
        'Q_SALEDAY': siq_saleDay,
        'N_SALEDAY': saleDay
    }
    response_data = post(url, data)
    result = {}
    if response_data.status_code == 200:
        json_data = json.loads(response_data.text)

        for key, items in dict(json_data).items():
            if key == 'total':
                result[key] = items
                continue

            result[key] = [
                [str(v) for v in dict(item).values()]
                for item in items
            ]
            # print(f'key: {key} {len(items)}')

    return [result]
