# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/4/3 11:37
# @Author : 连三保
# @Version: V 1.0
# @File : 25_FrontTest.py
# @desc :
import requests
from lxml import etree
import re
from PIL import Image, ImageDraw, ImageFont
from ddddocr import DdddOcr
from fontTools.ttLib import TTFont


def parser_font(fontfile):  # 获取字体文件密文字符和明文字形的关系
    font_obj = TTFont(fontfile)
    cmap_dict = font_obj.getBestCmap()
    ocr = DdddOcr(show_ad=False)
    key_map = {}
    for k, v in cmap_dict.items():
        name = chr(k)
        # 创建一个图像
        img = Image.new('RGB', (200, 200), color='red')
        # 创建一个在图片中绘-g制内容的画笔
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(fontfile, size=150)
        # 在图片中绘制内容
        draw.text(xy=(50, 50), text=name, font=font, fill='pink')
        # 识别字符对应的字形是什么
        value = ocr.classification(img)
        key_map[name] = value
    return key_map

res = parser_font('xss.woff')