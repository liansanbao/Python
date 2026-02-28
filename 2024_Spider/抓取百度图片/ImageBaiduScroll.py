# _*_ coding: utf-8 _*_
# @Time : 2025/4/18 8:53
# @Author : 韦丽
# @Version: V 1.0
# @File : ImageBaiduScroll.py
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
import re
import subprocess

import jsonpath
import requests
from playwright.sync_api import sync_playwright

class ImageBaiduScroll:
    def __init__(self, image_count, inputWord, inputPage=50):
        """定义远程调试参数"""
        path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        params = "--remote-debugging-port=9222"
        cmd = f'"{path}" {params}'
        subprocess.Popen(cmd, shell=True)
        # 图片下载数量统计
        self.image_count = image_count
        self.download_count = 0
        # 设定爬取的页数
        self.inputPage = inputPage + 1
        # 搜索关键字加密
        self.inputWord = inputWord

    def exec(self):
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
            # 给playwright添加响应事件的侦听处理函数
            self.page.on('response', self.handler_response)
            # 指定访问的URL
            self.page.goto('https://image.baidu.com/')
            self.page.wait_for_load_state('networkidle')

            # 搜索框里输入关键字
            self.page.fill('//input[@id="image-search-input"]', self.inputWord)
            # 单击百度一下按钮
            self.page.click('//input[@type="submit"]')
            self.page.wait_for_timeout(2000)
            # 滚动滚动条
            for index in range(1, self.inputPage):
                # 一次向下滚动840个像素
                self.page.evaluate(f'document.documentElement.scrollTop={840*index}')
                self.page.wait_for_timeout(5000)
                print(f'滚动{index}次，一共抓取图片{self.download_count}张！')
                # 当下载次数超过指定数量时， 退出循环
                if self.download_count >= self.image_count:
                    break
                # 抱歉，没有更多图片啦~时，退出循环
                endWordObject = self.page.locator('//div[text()="抱歉，没有更多图片啦～"]').all()
                if endWordObject != None and len(endWordObject) != 0:
                    endword = endWordObject[0].inner_text()
                    if endword == '抱歉，没有更多图片啦～':
                        print(f'{endword} 结束抓取！')
                        break

            # 关闭页面
            self.page.close()

    # json数据
    def handler_response(self, response):
        request_url = response.url
        # https://image.baidu.com/search/acjson?tn=resultjson_com&word=%E7%89%B9%E6%9C%97%E6%99%AE&ie=utf-8&fp=result&fr=&ala=0&applid=&pn=30&rn=30&nojc=0&gsm=1e&newReq=1
        if response.headers.get('content-type') == 'application/json' and request_url.find('acjson?tn=resultjson_com&') != -1:
            print(f'滚动滚动条时的异步请求URL：{request_url}')
            # 获取滚动条滚动时的异步请求响应数据
            str_data = response.body()
            # 转Json数据
            json_data = json.loads(str_data)

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

    # 图片下载
    def downloadImage(self, image_url, image_name):
        index = 1
        # 图片名称为空时，采用搜索关键字代替
        if image_name == '':
            image_name = self.inputWord
        img_path = rf'imgs/{image_name}.jpg'

        # 判断图片是否存在，不存在就使用该图片名称，否则就在原有的图片名称上+'_0001'.jpg
        while os.path.exists(img_path):
            img_path = rf'imgs/{image_name+ f"{index:04d}"}.jpg'
            index += 1

        # print(image_url, img_path)
        # 图片保存
        with open(img_path, 'wb') as f:
            # 统计下载次数
            self.download_count += 1
            f.write(requests.get(url=image_url).content)

if __name__ == '__main__':
    imageBaidu = ImageBaiduScroll(50,'爬虫')
    imageBaidu.exec()
