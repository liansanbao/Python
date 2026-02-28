# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/3/27 17:30
# @Author : 连三保
# @Version: V 1.0
# @File : start.py
# @desc :
from scrapy.cmdline import execute

execute(('scrapy crawl movie').split())