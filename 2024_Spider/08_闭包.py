# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/3/23 21:34
# @Author : 连三保
# @Version: V 1.0
# @File : 08_闭包.py
# @desc : 1.函数嵌套 2.内部函数使用到外部函数的变量 3.外部函数返回内部函数的引用

def outer(m):
    n = 10
    def inner():
        print(m + n)

    return inner

outer(2)()

