# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/3/25 6:57
# @Author : 连三保
# @Version: V 1.0
# @File : 10_作业.py
# @desc :
import json
import time

import jsonpath
import requests
from fake_useragent import FakeUserAgent

if __name__ == '__main__':
    header = {
        'User-Agent':f'{FakeUserAgent.random}',
    }
    with open('10_作业.json', 'w', encoding='utf-8') as w:
        result = []

        url = f'https://piaofang.maoyan.com/dashboard-ajax?orderType=0&uuid=195d664f88dc8-0898cbbf1fec4c-26011d51-1fa400-195d664f88dc8&timeStamp=1743059232595&User-Agent=TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEzNC4wLjAuMCBTYWZhcmkvNTM3LjM2&index=595&channelId=40009&sVersion=2&signKey=fcea03e1795280760dfe6d6777643883&WuKongReady=h5'
        # 发送请求
        response = requests.get(url=url, headers=header)

        # 数据处理
        if response.status_code == 200:
            py_data = response.json()
            # 解析电影名称和评分 >> jsonpath
            rank_list = jsonpath.jsonpath(py_data, '$..movieInfo')
            types_list = jsonpath.jsonpath(py_data, '$..boxRate')
            vote_count_list = jsonpath.jsonpath(py_data, '$..splitBoxSplitUnit')

            # 构造字典
            move_dict = zip(rank_list, types_list, vote_count_list)

            for i in move_dict:
                dict_data = {
                    '电影排名':i[0],
                    '电影类型':i[1],
                    '评论人数':i[2]
                }
                result.append(dict_data)

        time.sleep(3)

        # python数据列表 >> json数据
        json_data = json.dumps(result, ensure_ascii=False, indent=2) + ', \n'

        w.write(json_data)

