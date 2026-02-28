# _*_ coding: utf-8 _*_
# @Time : 2025/8/13 星期三 16:00
# @Author : 韦丽
# @Version: V 1.0
# @File : playwright.py
# @desc :

import json
import subprocess
import time
from typing import List, Dict

import asyncio
import jsonpath
from playwright.async_api import async_playwright

class TaobaoProductActivateCrawl:
    def __init__(self):
        """定义远程调试参数"""
        path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        user_data_dir = r"D:\chrome_userData"  # 自定义目录

        # 终止已有chrome进程
        # subprocess.run(['taskkill', '/f', '/im', 'chrome.exe'], shell=True)
        # time.sleep(3)  # 确保进程完全终止

        subprocess.Popen([path,
                          "--remote-debugging-port=9222",
                          f"--user-data-dir={user_data_dir}",
                          "--no-first-run",
                          "--disable-extensions",
                          "--disable-background-networking",
                          "--disable-component-update",
                          "--no-default-browser-check"
                          ], shell=True)

    async def exec(self, url, proxy) -> List[Dict]:
        self.page = None
        try:
            """爬虫程序的入口函数"""
            async with async_playwright() as p:
                # 连接本地启动的浏览器
                browser = await p.chromium.connect_over_cdp('http://127.0.0.1:9222', timeout=30000)

                print(f'1111 url: {url}')
                # 选择默认的浏览器上下文对象
                # self.context = self.browser.contexts[0] if self.browser.contexts else await self.browser.new_context()
                if not browser.contexts:
                    self.context = await browser.new_context()
                else:
                    self.context = browser.contexts[0]
                # 代理IP
                # if proxy:
                #     await self.context.set_extra_http_headers({
                #         'Proxy-Authorization': f'Basic {proxy}'
                #     })
                # 选择默认打开的页面
                self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()
                # 添加初始化js脚本代码，隐藏webdriver属性，防止检测出来
                js = "Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});"
                await self.page.add_init_script(js)

                # 给playwright添加响应事件的侦听处理函数
                self.page.on('response', lambda response: asyncio.create_task(self.handler_response(response)))

                # 指定访问的URL
                await self.page.goto(url, timeout=60000)
                await self.page.wait_for_load_state('load')

                await self.page.wait_for_selector('body', state='attached')

                # 关闭页面
                await self.page.close()
        except Exception as ex:
            # 关闭页面
            if self.page:
                await self.page.close()
            print(f'TaobaoProductActivateCrawl: {str(ex)}')
            raise


    # json数据
    async def handler_response(self, response):
        request_url = response.url
        # https://h5api.m.taobao.com/h5/mtop.taobao.pcdetail.data.get/1.0/?jsv=2.7.4&appKey=12574478&t=1754672750412&sign=cd1f61bc098afd9600fbf71130935acb ...
        if response.headers.get('content-type') == 'application/json;charset=UTF-8' and request_url.find('mtop.taobao.pcdetail.data.get/1.0/?') != -1:
            # 获取滚动条滚动时的异步请求响应数据
            str_data = await response.body()
            # 转Json数据
            json_data = await self.str_to_json(str_data)
            # 图片URL
            thumburl_list = jsonpath.jsonpath(json_data, '$.data.componentsVO.extensionInfoVO.infos..items..text')
            print(f'thumburl_list: {thumburl_list}')

    # 将字符串转Json格式
    async def str_to_json(self, str_data):
        # 确保传入的是bytes类型
        if isinstance(str_data, bytes):
            str_result = str_data.decode('utf-8')
        else:
            str_result = str(str_data)
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
    tpac = TaobaoProductActivateCrawl()
    tpac.exec('https://s.taobao.com/search?page=2&q=%E7%94%B5%E8%84%91%E6%95%B4%E6%9C%BA&spm=a21bo.jianhua%2Fa.201867-main.d2_2.3de02a89OHEQWl&tab=all', None)