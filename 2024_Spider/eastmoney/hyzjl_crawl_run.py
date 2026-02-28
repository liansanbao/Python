# _*_ coding: utf-8 _*_
# @Time : 2025/4/17 8:46
# @Author : 韦丽
# @Version: V 1.0
# @File : hyzjl_crawl_run.py
# @desc :
import subprocess
import time

from scrapy.cmdline import execute

# 单次运行可行
# execute(('scrapy crawl hyzjl_crawl').split())
while True:
    # 每隔10运行一次
    subprocess.run(['scrapy', 'crawl', 'hyzjl_crawl'])
    time.sleep(30)
