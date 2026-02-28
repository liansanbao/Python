# _*_ coding: utf-8 _*_
# @Time : 2025/4/14 15:35
# @Author : 韦丽
# @Version: V 1.0
# @File : douban_redis_run.py
# @desc :
from scrapy.cmdline import execute

execute(('scrapy crawl douban').split())