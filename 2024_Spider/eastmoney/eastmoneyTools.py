# _*_ coding: utf-8 _*_
# @Time : 2025/4/17 7:30
# @Author : 韦丽
# @Version: V 1.0
# @File : eastmoneyTools.py
# @desc : 东方财富网工具类
import random
from urllib.parse import unquote, quote
import json
import datetime
import akshare as ak
import requests


# 游资有无判断
def youzi(stockNo, datestr):
    try:
        ak.stock_lhb_stock_detail_em(symbol=stockNo, date=datestr, flag="买入")
        youzi = '有'
    except (Exception) as e:
        try:
            ak.stock_lhb_stock_detail_em(symbol=stockNo, date=datestr, flag="卖出")
            youzi = '有'
        except (Exception) as e:
            youzi = '无'
    return youzi

# URL参数解码
def unquote_str(str):
    return unquote(str)

# URL参数加码
def quote_str(str):
    return quote(str)

# str转float
def str_to_float(str):
    result = 0
    try:
        result = float(str)
    except Exception as e:
        pass
    return result

# 生成 13 位毫秒级时间戳
def timestamp_13():
    return int(datetime.datetime.timestamp(datetime.datetime.today()) * 1000)

# 净额数据单位编辑
def amountUnitEdit(strValue, unit: str='元'):
    # 例子：620811552.0 => 亿
    #      76256208.0 => 万
    #      66343.0 => 万
    # print(f'strValue1: {type(strValue)}, {strValue}')
    strValue = str(strValue)
    # print(f'strValue2: {type(strValue)}, {strValue}')
    # 长度为9的情况，可以转换成亿为单位
    if (len(strValue) >= 9):
        # print(f'strValue3: {type(str_to_float(strValue))}, {str_to_float(strValue)}')
        return f'{round(str_to_float(strValue) / 100000000, 2):.2f}亿'
    # 长度为5的情况，可以转换成万为单位
    elif (len(strValue) >= 5):
        # print(f'strValue4: {type(str_to_float(strValue))}, {str_to_float(strValue)}')
        return f'{round(str_to_float(strValue) / 10000, 2):.2f}万'
    else:
        return f'{str_to_float(strValue)}{unit}'

# cb参数值生成
def generate_jquery_callback():
    # 生成随机数部分（模拟 jQuery 随机数）
    rand_part = str(random.random()).replace('0.', '')  # 初始随机数（去掉小数点）
    rand_extra = str(random.randint(0, 99999))  # 补充随机数（可选）
    random_combined = rand_part + rand_extra  # 合并随机数

    # 生成 13 位毫秒级时间戳
    timestamp = timestamp_13()

    # 拼接完整参数
    cb = f"jQuery{random_combined}_{timestamp}"
    return cb

# str转int
def str_to_int(str):
    result = 0
    try:
        result = int(str)
    except Exception as e:
        pass
    return result

# str转float
def str_to_float(str):
    result = 0
    try:
        result = float(str)
    except Exception as e:
        pass
    return result

# 时间format return 09:25:00
def format_hms(hms: str = '000000'):
    # print(type(hms), hms)
    return datetime.datetime.strptime(hms, '%H%M%S').strftime('%H:%M:%S')

# 日期format return 09:25:00
def format_ymdhms(ymdhms: str = '2026-01-07 00:00:00', startF: str = '%Y-%m-%d %H:%M:%S', endF: str = '%Y-%m-%d'):
    # print(type(hms), hms)
    return datetime.datetime.strptime(ymdhms, startF).strftime(endF)

# 付费版代理IP取得 需要替换一下URL
def getProxies(num: int = 1):
    url = f'http://api.tianqiip.com/getip?secret=msqo66gmf1kowk4r&num={num}&type=txt&port=1&time=3&mr=1&sign=706041cda2ff3887e387232294db1783'
    ip_list = []
    response = requests.get(url=url)
    if response.status_code == 200:
        # 出力的IP：110.90.14.41:40011\r\n，需要替换\r\n
        ip_str = response.text.split('\r\n')
        ip_list.extend([ip for ip in ip_str if ip != ''])

    tianqiip_formate = f'{logger_now_date()} 获取的代码IP：{ip_list}'
    print(tianqiip_formate)
    return ip_list

# playwright 专用的IP代理
def playwrightProxy(num):
    proxy_config = {
        "server": f"http://{getProxies(num)[0]}",
        "username": "18217623705",
        "password": "Sanbao_2025"
    }
    print(f'proxy_config: {proxy_config}')
    return proxy_config

# 当日日期取得: 返回yyyy-mm-dd
def now_date(formate: str = '%Y%m%d'):
    return datetime.date.today().strftime(formate)

# Logger时间取得
def logger_now_date():
    return datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S.%f")

# 将字符串转Json格式
def str_to_json(str_data):
    # 如果是bytes类型，先解码为字符串
    if isinstance(str_data, bytes):
        jsonp_str = str_data.decode('utf-8')
    else:
        jsonp_str = str_data
    # 去掉JSONP包装
    start = jsonp_str.find('(') +1
    end = jsonp_str.rfind(')')
    json_str = jsonp_str[start:end]
    # 解析Json
    return json.loads(json_str)

def get_quarter_dates():
    """计算输入日期所在季度的开始和结束日期"""
    nowDate = datetime.date.today()

    year = nowDate.year
    month = nowDate.month

    # 确定季度
    if month in [1, 2, 3]:
        quarter = 4
        start_date = datetime.date(year-1, 10, 1)
        end_date = datetime.date(year-1, 12, 31)
    elif month in [4, 5, 6]:
        quarter = 1
        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year, 3, 31)
    elif month in [7, 8, 9]:
        quarter = 2
        start_date = datetime.date(year, 4, 1)
        end_date = datetime.date(year, 6, 30)
    elif month in [10, 11, 12]:
        quarter = 3
        start_date = datetime.date(year, 7, 1)
        end_date = datetime.date(year, 9, 30)

    return {
        "quarter": quarter,
        "start_date": start_date.strftime("%Y%m%d"),
        "end_date": end_date.strftime("%Y%m%d")
    }

if __name__ == "__main__":
    # result = get_quarter_dates()
    # print(f"第{result['quarter']}季度：[{result['start_date']}, {result['end_date']}]")
    print(datetime.datetime.now().strftime('%H%M%S'))
