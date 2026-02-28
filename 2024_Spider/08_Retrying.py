# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/3/23 21:03
# @Author : 连三保
# @Version: V 1.0
# @File : 08_Retrying.py
# @desc : retry 是一个三层函数的嵌套，并且返回了内部函数的引用，闭包三层 >> 有参数的装饰器
import requests
from retrying import retry


class Retrying_08:
    def __init__(self):
        # 模拟网络波动
        self.url = 'xxxx.com'
        self.num = 0

    @retry(stop_max_attempt_number=3)
    def send_requests(self):
        self.num += 1
        print(f'请求次数：{self.num}')
        requests.get(self.url)

    def run(self):
        try:
            self.send_requests()
        except Exception as e:
            print(e)


if __name__ == '__main__':
    re = Retrying_08()
    re.run()