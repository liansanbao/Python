# _*_ coding: utf-8 _*_
# @Time : 2026/1/1 星期四 20:35
# @Author : 韦丽
# @Version: V 1.0
# @File : maoyanPlaywright.py
# @desc : 猫眼排行榜电影数据采集
import datetime
import os
import re
import sys

import jsonpath
import pandas
import requests
from ddddocr import DdddOcr
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright


def logger_now_date():
    return datetime.datetime.now().strftime("%Y.%m.%d %H:%M:%S.%f")


class MaoyaoPlaywright:
    # 构造函数
    def __init__(self, url):
        self.url = url

    # 数据采集
    def exec(self):
        """爬虫程序的入口函数"""
        with sync_playwright() as p:
            # 连接本地启动的浏览器
            self.browser = p.chromium.launch_persistent_context(
                executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                user_data_dir=r'D:\chrome_userData',  # 在D盘根目录下创建chrome_userData文件夹
                # user_data_dir=r'C:\Users\Administrator\AppData\Local\Google\Chrome\User Data', # 系统默认chrome浏览器数据访问失败
                # proxy = self.proxy_config,
                headless=False)

            try:
                # 选择默认打开的页面
                self.search_page = self.browser.new_page()
                # 添加初始化js脚本代码，隐藏webdriver属性，防止检测出来
                js = "Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});"
                self.search_page.add_init_script(js)
                # 给playwright添加响应事件的侦听处理函数
                self.search_page.on('response', self.maoyan_response)
                """爬虫执行的主要逻辑"""
                try:
                    self.search_page.goto(self.url, wait_until="domcontentloaded")
                except:
                    self.search_page.goto(self.url, wait_until="domcontentloaded")

                self.search_page.wait_for_timeout(4000)

                # 关闭页面
                self.search_page.close()
            except Exception as e:
                print(f"{logger_now_date()} 数据处理中。。。。。。连接失败： {e}")

    # 请求监视
    def maoyan_response(self, response):
        try:
            request_url = response.url
            # 猫眼数据：https://piaofang.maoyan.com/dashboard-ajax?orderType
            if response.headers.get('content-type') == 'application/json; charset=utf-8' and request_url.find(
                    'dashboard-ajax?') != -1:
                # print(f'猫眼数据2: {request_url}')
                # 沪深京A股数据抓取
                self.parseDashboard(response)

        except Exception as ex:
            print(f'{logger_now_date()} 服务器响应处理错误: {str(ex)}')

    # 获取字体文件密文字符和明文字形的关系
    def parser_font(self, fontfile):
        font_obj = TTFont(fontfile)
        cmap_dict = font_obj.getBestCmap()
        ocr = DdddOcr(show_ad=False)
        print(f'字体原生内容： {cmap_dict}')
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

    # 数据采集
    def parseDashboard(self, response):
        json_data = response.json()
        # 字体URL取得
        rank_list = json_data["fontStyle"]
        str_woff = re.findall(r',url\("(.*?)"\);', rank_list)[0]
        woff_url = "https:" + str_woff
        woff_name = str_woff.split('/font/')[1]

        print(f'已下载的字体文件：{woff_url, woff_name}')
        if not os.path.exists(woff_name):
            woff_response = requests.get(woff_url)
            if woff_response.status_code == 200:
                with open(woff_name, 'wb') as write:
                    write.write(woff_response.content)

        res = self.parser_font(woff_name)
        # print(f'字体处理结果：{res}')

        # 主数据编辑
        mainData = json_data['movieList']['data']['list']
        result_list = []
        for item in mainData:
            # print(f'item: {item["movieInfo"]["movieName"]}')
            # 影片名称
            movieName = item["movieInfo"]["movieName"]
            # 上映天数
            releaseInfo = item["movieInfo"]["releaseInfo"]
            # 综合票房
            box_num = item["boxSplitUnit"]["num"]
            box_num = str(box_num).upper().replace('&#X', 'uni', -1).replace(';', '')
            for k, v in res.items():
                box_num = box_num.replace(k, v, -1)

            # 综合票房 单位
            box_unit = item["boxSplitUnit"]["unit"]
            # 票房占比
            boxRate = item["boxRate"]
            # 排片场次
            showCount = item["showCount"]
            # 票房金额
            sumBoxDesc = item["sumBoxDesc"]
            result_list.append([movieName, releaseInfo, sumBoxDesc, f'{box_num}{box_unit}', boxRate, showCount])

        pandas_data = pandas.DataFrame(data=result_list,
                                       columns=['影片名称', '上映天数', '票房金额', '综合票房', '票房占比', '排片场次'])

        # 猫眼实时数据保存
        pandas_data.to_csv('maoyan_2026.csv')


if __name__ == '__main__':
    es = MaoyaoPlaywright('https://piaofang.maoyan.com/dashboard')
    es.exec()
    sys.exit()