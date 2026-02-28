import scrapy
import os
import re

import execjs
import jsonpath
import requests
from PIL import Image, ImageDraw, ImageFont
from ddddocr import DdddOcr
from fontTools.ttLib import TTFont
from ..items import *

class Maoyan365Spider(scrapy.Spider):
    name = "maoyan365"
    allowed_domains = ["piaofang.maoyan.com"]
    # start_urls = ["https://piaofang.maoyan.com"]

    # 获取字体文件密文字符和明文字形的关系
    def parser_font(self, fontfile):
        font_obj = TTFont(fontfile)
        cmap_dict = font_obj.getBestCmap()
        ocr = DdddOcr(show_ad=False)
        self.logger.info(f'字体原生内容： {cmap_dict}')
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
            key_map[v] = value
        return key_map

    # 请求某些参数进行加密
    def getRequestParam(self, userAgent):
        # 1.使用文件的读写拿到js文件里面的代码
        with open(os.path.abspath('maoyan.js'), 'r', encoding='utf-8') as r:
            js_data = r.read()

        # 2.拿到js代码时候，需要进行一个类似编码的操作
        js_obj = execjs.compile(js_data)

        # 3.执行js代码
        result = js_obj.call('getQueryKey', userAgent)

        return result

    def start_requests(self):
        userAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
        param = self.getRequestParam(userAgent)
        self.logger.info(f'生成的JS加密参数： {param}')
        url = 'https://piaofang.maoyan.com/dashboard-ajax?orderType=0&uuid=195d664f88dc8-0898cbbf1fec4c-26011d51-1fa400-195d664f88dc8' \
              '&timeStamp=' + str(param['timeStamp']) + '&User-Agent=' + param['User-Agent'] + '&index=' + str(
            param['index']) + '' \
                              '&channelId=' + str(param['channelId']) + '&sVersion=' + str(
            param['sVersion']) + '&signKey=' + param['signKey'] + '&WuKongReady=h5'

        self.logger.info(f'生成的URL： {url}')
        yield scrapy.Request(
            url,
            callback=self.parse
        )

    def parse(self, response):
        json_data = response.json()
        # print(f'爬取的结果：{json_data}')
        # 字体URL取得
        rank_list = jsonpath.jsonpath(json_data, '$..fontStyle')
        str_woff = re.findall(r',url\("(.*?)"\);', rank_list[0])[0]
        woff_url = "https:" + str_woff
        woff_name = str_woff.split('/font/')[1]

        self.logger.info(f'已下载的字体文件：{woff_url, woff_name}')
        if not os.path.exists(woff_name):
            woff_response = requests.get(woff_url)
            if woff_response.status_code == 200:
                with open(woff_name, 'wb') as write:
                    write.write(woff_response.content)
        res = self.parser_font(woff_name)
        self.logger.info(f'字体处理结果：{res}')
        # 影片名称
        movieName_list = jsonpath.jsonpath(json_data, '$..movieInfo.movieName')
        # 综合票房 boxSplitUnit
        box_num_list = jsonpath.jsonpath(json_data, '$..boxSplitUnit.num')
        box_num_list_up = []
        self.logger.info(f'综合票房字体加密: {box_num_list}')
        for i in box_num_list:
            i = str(i).upper().replace('&#X', 'uni', -1).replace(';', '')
            for k, v in res.items():
                i = i.replace(k, v, -1)

            box_num_list_up.append(i)
        self.logger.info(f'综合票房字体解密: {box_num_list_up}')
        # 票房占比
        boxRate_list = jsonpath.jsonpath(json_data, '$..boxRate')
        # 排片场次
        showCount_list = jsonpath.jsonpath(json_data, '$..showCount')

        result_dict = zip(movieName_list, box_num_list_up, boxRate_list, showCount_list)
        for item in result_dict:
            movie_item = MaoyanItem()
            # 影片名称
            movie_item['movieName'] = item[0]
            # 综合票房
            movie_item['num'] = item[1] + '万'
            # 票房占比
            movie_item['boxRate'] = item[2]
            # 排片场次
            movie_item['showCount'] = item[3]
            # 猫眼实时数据保存
            yield movie_item

