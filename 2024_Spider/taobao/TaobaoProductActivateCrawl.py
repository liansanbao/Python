# _*_ coding: utf-8 _*_
# @Time : 2025/8/9 星期六 0:55
# @Author : 韦丽
# @Version: V 1.0
# @File : TaobaoProductActivateCrawl.py
# @desc : 抓取淘宝网商品活动数据，网站：（https://www.taobao.com/）

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
import time

import jsonpath
import requests
from playwright.sync_api import sync_playwright

class TaobaoProductActivateCrawl:
    def __init__(self, url):
        """定义远程调试参数"""
        path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        params = "--remote-debugging-port=9222"
        user_data_dir = r"D:\chrome_userData"  # 自定义目录
        cmd = f'"{path}" {params}'
        subprocess.Popen([path, "--remote-debugging-port=6789", f"--user-data-dir={user_data_dir}"], shell=True)
        # 爬取URL
        self.url = url

    def exec(self):
        """爬虫程序的入口函数"""
        with sync_playwright() as p:
            # 连接本地启动的浏览器
            browser = p.chromium.connect_over_cdp('http://127.0.0.1:6789')
            # 选择默认的浏览器上下文对象
            self.context = browser.contexts[0]
            # 选择默认打开的页面
            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
            # 添加初始化js脚本代码，隐藏webdriver属性，防止检测出来
            js = "Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});"
            self.page.add_init_script(js)

            # 指定访问的URL
            self.page.goto(self.url)
            self.page.wait_for_load_state('load')

            product_list = self.page.locator('//div[@id="content_items_wrapper"]//div//a[@data-spm-protocol="i"]').all()
            print(f'len: {len(product_list)}')
            for a in product_list:
                detal_url = a.get_attribute('href')
                if not detal_url.startswith('https:'):
                    self.detal_url = f"https:{detal_url}"
                else:
                    self.detal_url = detal_url

                print(f"detal_url: {self.detal_url}")

            # 关闭页面
            self.page.close()

    def run_detail_data(self):
        # 选择默认打开的页面
        self.pageDeatil = self.context.new_page()
        # 给playwright添加响应事件的侦听处理函数
        self.pageDeatil.on('response', self.handler_response)

        try:
            self.pageDeatil.goto(self.detal_url, wait_until="domcontentloaded")
        except:
            self.pageDeatil.goto(self.detal_url, wait_until="domcontentloaded")

        self.pageDeatil.wait_for_timeout(2000)

        self.pageDeatil.close()

    # json数据
    def handler_response(self, response):
        request_url = response.url
        # https://h5api.m.taobao.com/h5/mtop.taobao.pcdetail.data.get/1.0/?jsv=2.7.4&appKey=12574478&t=1754672750412&sign=cd1f61bc098afd9600fbf71130935acb&api=mtop.taobao.pcdetail.data.get&v=1.0&isSec=0&ecode=0&timeout=10000&jsonpIncPrefix=pcdetail&ttid=2022%40taobao_litepc_9.17.0&AntiFlood=true&AntiCreep=true&type=jsonp&dataType=jsonp&callback=mtopjsonppcdetail3&data=%7B%22id%22%3A%22937920164396%22%2C%22detail_v%22%3A%223.3.2%22%2C%22exParams%22%3A%22%7B%5C%22abbucket%5C%22%3A%5C%225%5C%22%2C%5C%22id%5C%22%3A%5C%22937920164396%5C%22%2C%5C%22ns%5C%22%3A%5C%221%5C%22%2C%5C%22priceTId%5C%22%3A%5C%22213e055c17546725395342171e1425%5C%22%2C%5C%22skuId%5C%22%3A%5C%225831322641670%5C%22%2C%5C%22spm%5C%22%3A%5C%22a21n57.1.hoverItem.49%5C%22%2C%5C%22utparam%5C%22%3A%5C%22%7B%5C%5C%5C%22aplus_abtest%5C%5C%5C%22%3A%5C%5C%5C%2283267e7c07402b205018ee57e2ada6a3%5C%5C%5C%22%7D%5C%22%2C%5C%22xxc%5C%22%3A%5C%22taobaoSearch%5C%22%2C%5C%22queryParams%5C%22%3A%5C%22abbucket%3D5%26id%3D937920164396%26ltk2%3D1754672713855ux9sdj5rpesjik19uvtj%26ns%3D1%26priceTId%3D213e055c17546725395342171e1425%26skuId%3D5831322641670%26spm%3Da21n57.1.hoverItem.49%26utparam%3D%257B%2522aplus_abtest%2522%253A%252283267e7c07402b205018ee57e2ada6a3%2522%257D%26xxc%3DtaobaoSearch%5C%22%2C%5C%22domain%5C%22%3A%5C%22https%3A%2F%2Fitem.taobao.com%5C%22%2C%5C%22path_name%5C%22%3A%5C%22%2Fitem.htm%5C%22%2C%5C%22pcSource%5C%22%3A%5C%22pcTaobaoMain%5C%22%2C%5C%22refId%5C%22%3A%5C%22qCU%2Fv2eMQNRPc35X2WqRNg3eiUoCIkbsljuV2IMCnhw%3D%5C%22%2C%5C%22nonce%5C%22%3A%5C%22U1DZdqoQI0GGqwaubbsKqw%3D%3D%5C%22%2C%5C%22feTraceId%5C%22%3A%5C%22d27f5db2-d4f9-43ba-b0fd-bb1d48915ba0%5C%22%7D%22%7D&bx-ua=fast-load
        if response.headers.get('content-type') == 'application/json;charset=UTF-8' and request_url.find('mtop.taobao.pcdetail.data.get/1.0/?') != -1:
            print(f'滚动滚动条时的异步请求URL：{request_url}')
            # 获取滚动条滚动时的异步请求响应数据
            str_data = response.body()
            # 转Json数据
            json_data = self.str_to_json(str_data)

            print(f'json_data: {json_data}')

            # thumburl_list = jsonpath.jsonpath(json_data, '$.data.componentsVO.extensionInfoVO.infos')
            # for item in thumburl_list:
            #     title = jsonpath.jsonpath(json_data, '$..title')

            # 图片URL
            thumburl_list = jsonpath.jsonpath(json_data, '$.data.componentsVO.extensionInfoVO.infos..items..text')
            print(f'thumburl_list: {thumburl_list}')

    # 将字符串转Json格式
    def str_to_json(self, str_data):
        str_result = str_data.decode('utf-8')
        # 去掉JSONP包装
        start = str_result.find('(') + 1
        end = str_result.rfind(')')
        json_str = str_result[start:end]
        # 解析Json
        return json.loads(json_str)

if __name__ == '__main__':
    # 电脑：https://s.taobao.com/search?page=2&q=%E7%94%B5%E8%84%91%E6%95%B4%E6%9C%BA&spm=a21bo.jianhua%2Fa.201867-main.d2_2.3de02a89OHEQWl&tab=all
    #      https://s.taobao.com/search?page=3&q=%E7%94%B5%E8%84%91%E6%95%B4%E6%9C%BA&spm=a21bo.jianhua%2Fa.201867-main.d2_2.3de02a89OHEQWl&tab=all
    #      https://s.taobao.com/search?page=4&q=%E7%94%B5%E8%84%91%E6%95%B4%E6%9C%BA&spm=a21bo.jianhua%2Fa.201867-main.d2_2.3de02a89OHEQWl&tab=all
    # 家电：https://s.taobao.com/search?page=1&q=%E5%AE%B6%E7%94%B5&spm=a21bo.jianhua%2Fa.201867-main.d4_first.3de02a89OHEQWl&tab=all
    #      https://s.taobao.com/search?page=2&q=%E5%AE%B6%E7%94%B5&spm=a21bo.jianhua%2Fa.201867-main.d4_first.3de02a89OHEQWl&tab=all
    #      https://s.taobao.com/search?page=3&q=%E5%AE%B6%E7%94%B5&spm=a21bo.jianhua%2Fa.201867-main.d4_first.3de02a89OHEQWl&tab=all
    tpac = TaobaoProductActivateCrawl('https://s.taobao.com/search?page=2&q=%E7%94%B5%E8%84%91%E6%95%B4%E6%9C%BA&spm=a21bo.jianhua%2Fa.201867-main.d2_2.3de02a89OHEQWl&tab=all')
    tpac.exec()


