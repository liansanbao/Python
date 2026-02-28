# _*_ coding: utf-8 _*_
# @Time : 2025/4/18 15:42
# @Author : 韦丽
# @Version: V 1.0
# @File : dangdang_run.py
# @desc : dangdang引擎启动
from scrapy.cmdline import execute

execute(('scrapy crawl dangdang').split())