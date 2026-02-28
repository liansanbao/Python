# _*_ coding: utf-8 _*_
# @Time : 2025/6/23 0023 23:09
# @Author : 韦丽
# @Version: V 1.0
# @File : RequestsWLW.py
# @desc : 风险个股数据采集

import json
import requests
from fake_useragent import FakeUserAgent

def get(url):
    header = {
        'User-Agent': FakeUserAgent().random
    }
    return requests.get(url=url, headers=header)

def EditData(url):
    response_data = get(url)
    row_data = []
    if response_data.status_code == 200:
        json_data = json.loads(response_data.text)
        for name in json_data:
            data = (str(value) for value in dict(name).values())
            row_data.append(data)
        print(f'row_data: {row_data}')
    return row_data


if __name__ == '__main__':
    EditData('http://46zllpjb6g5c.xiaomiqiu.com/wlw?table_key=STOCK_INFO_QUESTION')