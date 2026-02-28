# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/3/23 22:12
# @Author : 连三保
# @Version: V 1.0
# @File : 08_装饰器.py
# @desc :

# 装饰器函数
def check(fn):
    def inner():
        print('请先登录。。。。。')
        fn()
    return inner

# 有参数的装饰器
def option(fn):
    def innert(s, b):
        print('开始了。。。。。')
        print(s, b)
        fn(s, b)
    return innert


# 发表评论
@check
def fabiao():
    print('发表评论。。。。。')

@option
def options(s, b):
    print(s, b)



fabiao()
options(2,3)