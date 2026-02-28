# _*_ coding: utf-8 _*_
# @Time : 2025/4/17 20:28
# @Author : 韦丽
# @Version: V 1.0
# @File : ImageBaidu.py
# @desc : 抓取百度图片，网站：（https://image.baidu.com/）

'''
要求：
1.最少五百张
2.保存的图片名以网站中所给的图片名为准
3.可以搜索下载指定关键字的图片类型
4.所有图片单独存放在一个imgs文件夹下
'''
import json
import os
import random
import re
import subprocess

import jsonpath
from lxml import etree

import requests
from fake_useragent import FakeUserAgent
from urllib.parse import quote
from playwright.sync_api import sync_playwright

class ImageBaidu:
    # URL参数编码
    def quote_str(self, str):
        return quote(str)

    # gsm参数生成
    def getGSM(self):
        numStr = '0123456789'
        wordStr = 'abcdefghijklmnopqrstuvwxyz'
        allStr = numStr + wordStr
        # 随机选择3或4位长度
        length = random.choice([3,4])
        # 确保至少一个字母
        code = [
            random.choice(wordStr)
        ]
        # 填充剩余位数
        for _ in range(length - 1):
            code.append(random.choice(allStr))

        # 打乱顺序后 组成字符串
        random.shuffle(code)
        return ''.join(code)

    def __init__(self, image_count, inputWord, inputPage=50):
        # 请求header
        self.header = {
            'User-Agent':FakeUserAgent().random,
            'Cookie':'BIDUPSID=E5425CEDF39D4C9B450C1E22552EF4E2; PSTM=1742716398; BAIDUID=D990C857DAF3081DC091C948A912D842:FG=1; H_WISE_SIDS_BFESS=110085_633617_644372_644900_645266_645447_645428_645170_646157_646063_645434_646404_646421_646466_646360_646358_646499_646522_646728_646769_646780_646775_646771_646778_646826_647079_647064; MAWEBCUID=web_DZAHvtOqysBfPNUcLblRJVZTPZccCHjYraCDmDUKpGbmACvjtI; BAIDUID_BFESS=D990C857DAF3081DC091C948A912D842:FG=1; ZFY=RnrrBKPfJOVeIzvRoKpHdYpBt8VN8Qc6lNrLO7QAp:BM:C; H_PS_PSSID=61027_61672_62325_62336_62484_62637_62677_62848_62865_62881_62889_62928_62917_62922_62967; H_WISE_SIDS=62325_62637_62848_62865_62967_62998; arialoadData=false; ab_sr=1.0.1_Zjc0ZGMzNWE5MTE2ZTJkMmU4YmMwNzQxZGZlMzIyM2VjZjVlZmZlN2NmNDY2NTVhYmJmZTJhNGZmZjEzZTk5YjhkMDc2ZDFmOGExNTg2MTlkM2M4ZWVhZGI0MmIyN2NjNjU3ZjZhMWM0NGQ0MGY5ZjZlOGFmZThkNzMxYmIyMWQ2MDc2NzlkNmRlZWYzMTUwODk0YmRlNTU5YWM1ZGI3MjFjYTE4Y2RjZjg3Y2FhMDY5ZWRmODBiYTRlOTdlNTgyMzU0ZjZiNmRiNmNmZmY5MmNiMmIyZTg3ZGE0NzdlZDc='
        }
        # 搜索关键字加密
        self.inputWord = inputWord
        self.word = self.quote_str(self.inputWord)
        """定义远程调试参数"""
        path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        params = "--remote-debugging-port=6789"
        cmd = f'"{path}" {params}'
        subprocess.Popen(cmd, shell=True)
        # 图片下载数量统计
        self.image_count = image_count
        self.download_count = 0
        # 设定爬取的页数
        self.inputPage = inputPage

    def exec(self):
        url_base = 'https://image.baidu.com/'

        """爬虫程序的入口函数"""
        with sync_playwright() as p:
            # 连接本地启动的浏览器
            browser = p.chromium.connect_over_cdp('http://127.0.0.1:6789')
            # 选择默认的浏览器上下文对象
            context = browser.contexts[0]
            # 选择默认打开的页面
            self.page = context.pages[0] if context.pages else context.new_page()
            # 添加初始化js脚本代码，隐藏webdriver属性，防止检测出来
            js = "Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});"
            self.page.add_init_script(js)
            for page in range(1, self.inputPage):
                '''
                https://image.baidu.com/search/acjson?tn=resultjson_com&word=%E7%BE%8E%E4%B8%BD%E4%B8%AD%E5%9B%BD&ie=utf-8&fp=result&fr=&ala=0&applid=&pn=510&rn=30&nojc=0&gsm=1fe&newReq=1
                https://image.baidu.com/search/acjson?tn=resultjson_com&word=%E7%BE%8E%E4%B8%BD%E4%B8%AD%E5%9B%BD&ie=utf-8&fp=result&fr=&ala=0&applid=&pn=540&rn=30&nojc=0&gsm=21c&newReq=1
                参数说明：
                    url: 画面中滚动滚动条时，发出的异步请求
                    Word：就是搜索关键字，需要编码一下
                    pn: 分页参数
                    gsm:随机数3或4位
                '''
                self.url = f'{url_base}search/acjson?tn=resultjson_com&word={self.word}&ie=utf-8&fp=result&fr=&ala=0&applid=&pn={30 * page}&rn=30&nojc=0&gsm={self.getGSM()}&newReq=1'
                print(f'第{page}页 URL：{self.url}')
                # 指定访问的URL
                self.page.goto(self.url)
                # 等待3秒钟
                self.page.wait_for_timeout(5000)
                html_data = etree.HTML(self.page.content())
                str_data = html_data.xpath('//pre/text()')[0]
                json_data = json.loads(str_data)
                # 确认响应数据是否成功，失败了退出循环；说明图片已经没有了
                errno = jsonpath.jsonpath(json_data, '$..errno')[0]
                if errno != 0:
                    print(f'第{page}页 没有数据了，结束抓取。')
                    break
                # 图片URL
                thumburl_list = jsonpath.jsonpath(json_data, '$..thumburl')
                # 图片标题
                titleShow_list = jsonpath.jsonpath(json_data, '$..titleShow')
                result = zip(thumburl_list, titleShow_list)
                for item in result:
                    # https://img2.baidu.com/it/u=485911710,3702009548\u0026fm=253\u0026fmt=auto\u0026app=138\u0026f=JPEG?w=667\u0026h=500
                    # 替换thumburl值中的\u0026为&
                    str_url = str(item[0]).replace('\u0026', '&')
                    # 删除图片标题中的特殊字符,只保留汉字
                    imgs_name = re.sub(r'[^\u4e00-\u9fa5]', '', str(item[1]))
                    # 图片下载
                    self.downloadImage(str_url, imgs_name)

                print(f'截止到第{page}页 一共抓取图片{self.download_count}张！')
                # 当下载次数超过指定数量时， 退出循环
                if self.download_count >= self.image_count:
                    break

            # 关闭页面
            self.page.close()

    # 图片下载
    def downloadImage(self, image_url, image_name):
        # 判断图片是否存在，不存在就使用该图片名称，否则就在原有的图片名称上+'_0001'.jpg
        if image_name == '':
            image_name = self.inputWord
        img_path = rf'imgs/{image_name}.jpg'
        index = 1
        while os.path.exists(img_path):
            img_path = rf'imgs/{image_name+ f"{index:04d}"}.jpg'
            index += 1

        # print(image_url, img_path)
        # 图片保存
        with open(img_path, 'wb') as f:
            # 下载次数统计
            self.download_count += 1
            f.write(requests.get(url=image_url, headers=self.header).content)

if __name__ == '__main__':
    imageBaidu = ImageBaidu(500,'美丽中国')
    imageBaidu.exec()