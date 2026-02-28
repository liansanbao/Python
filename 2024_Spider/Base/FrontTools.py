# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/4/3 13:41
# @Author : 连三保
# @Version: V 1.0
# @File : FrontTools.py
# @desc :
# 字体确认工具：https://www.1json.com/front/fonteditor.html
# 字体第三库：pip install fontTools
#           pip install ddddocr
#           pip install pillow
# ImportError: DLL load failed while importing onnxruntime_pybind11_state: 动态链接库(DLL)初始化例程失败。 解决方案：pip install onnxruntime-gpu==1.19.0
from ddddocr import DdddOcr
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

# 获取字体文件密文字符和明文字形的关系
def parser_font(fontfile):
    font_obj = TTFont(fontfile)
    cmap_dict = font_obj.getBestCmap()
    ocr = DdddOcr(show_ad=False)
    key_map = {}
    for k,v in cmap_dict.items():
        name = chr(k)
        # 创建一个图像
        img = Image.new('RGB',(200,200),color='red')
        # 创建一个在图片中绘制内容的画笔
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(fontfile, size=150)
        # 在图片中绘制内容
        draw.text(xy=(50, 50), text=name, font=font, fill='pink')
        # 识别字符对应的字形是什么
        value = ocr.classification(img)
        key_map[name] = value
    return key_map
