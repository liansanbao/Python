# _*_ coding: utf-8 _*_
# @Time : 2025/4/12 19:41
# @Author : 韦丽
# @Version: V 1.0
# @File : 31_图片管道介绍.py
# @desc :

'''
抓取图片
    1.得到图片URL
    2.发送请求
    3.保存

    如果利用scrapy里面的图片管道，可以简化上面步骤，管道是用来保存数据

    使用图片管道
    xxx.jpg 图片管道中保存图片URL的键值对的键值是固定的  >> image_urls
    自定义图片保存字段 >> IMAGES_RESULT_FIELD

    图片的保存路径需要设置 IMAGES_STORE

'''
