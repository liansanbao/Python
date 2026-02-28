# _*_ coding: utf-8 _*_
# @Time : 2025/4/14 19:48
# @Author : 韦丽
# @Version: V 1.0
# @File : RedisTest.py
# @desc : 将scrapy-redis 采集的数据进行解码输出
import json

# 单次连接（适合简单场景）
import redis as redis

with redis.Redis(host='192.168.1.6', port=6379, db=0, password='') as r:
    select_list = r.lrange('douban:items', 0, -1)

    # 进行解码操作
    for item in select_list:
        print(f'解码之前的数据：{item}')
        data = json.loads(item)
        print(f'解码之后的数据：{data}')

# r = redis.Redis(host='192.168.1.17', port=6379, db=0, password='')
#
# # r.lpush('lian', 'san', 'bao') 列表操作
#
# # 取出douban:items 列表所有的元素
# select_list = r.lrange('douban:items', 0, -1)
#
# # 进行解码操作
# for item in select_list:
#     print(f'解码之前的数据：{item}')
#     data = json.loads(item)
#     print(f'解码之后的数据：{data}')
#
# # 关闭连接
# r.close()