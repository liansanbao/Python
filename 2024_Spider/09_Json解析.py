# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/3/24 8:18
# @Author : 连三保
# @Version: V 1.0
# @File : 09_Json解析.py
# @desc :
import json

ss = {'name':'Lockly', 'age':22}

with open('09_json.json', 'w') as w:
    json.dump(ss, w, ensure_ascii=False)

with open('09_json.json', 'r') as r:
    print(json.load(r))

