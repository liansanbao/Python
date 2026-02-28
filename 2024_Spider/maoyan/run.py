# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/4/1 21:28
# @Author : 连三保
# @Version: V 1.0
# @File : run.py
# @desc :
import subprocess
import time

from scrapy.cmdline import execute

# execute(('scrapy crawl maoyan365').split()) 单次运行可行
while True:
    # 每隔10运行一次
    subprocess.run(['scrapy', 'crawl', 'maoyan365'])
    time.sleep(30)
