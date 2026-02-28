# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/4/3 12:31
# @Author : 连三保
# @Version: V 1.0
# @File : Playwright_ShiXiSheng.py
# @desc :
import os
import re

import requests
from playwright.sync_api import sync_playwright
from lxml import etree
from Base.FrontTools import parser_font

## 字体库安装 pip install fontTools
## 字体确认工具：https://www.1json.com/front/fonteditor.html

if __name__ == '__main__':
    with sync_playwright() as p:
        # 创建浏览器
        browser = p.chromium.launch(headless=False,
                                    executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                                    args=['--start-maximized'])

        # 创建上下文
        content = browser.new_context(no_viewport=True)

        # 3.创建新页面 ** 注意全屏no_viewport=True
        # page = browser.new_page(no_viewport=True)
        page = content.new_page()

        # 4.发送请求 timeout,referer 跳转，wait_until[load:等待页面完全加载,domcontentloaded:等待DOM内容加载完成，即HTML文档已解析完毕, networkided:]
        try:

            # 添加JS脚本，隐藏webdriver属性，防止检测出来
            # JS = "Object.defineProperties(navigator, {webdriver: {get: ()=> false}});"
            JS = "Object.defineProperties(navigator, {webdriver: {get: ()=> undefined}});"

            page.add_init_script(JS)

            # 设置等待(方式1)
            # page.goto('https://www.so.com/', wait_until='load', timeout=6000)
            page.goto('https://www.shixiseng.com/interns?keyword=python&city=%E5%85%A8%E5%9B%BD&type=intern')

            # 设置等待load(方式1)
            page.wait_for_load_state('load')

            # print(page.content())
            # html数据
            html_data = etree.HTML(page.content())

            if not os.path.exists('xss.woff'):
                # 提取字体文件
                woff_url = 'https://www.shixiseng.com' + re.findall(r'src: url\((.*?)\);', page.content())[0]
                print(woff_url)
                woff_response = requests.get(woff_url)
                with open('xss.woff', 'wb') as write:
                    write.write(woff_response.content)

            res = parser_font('xss.woff')

            # 定位包含所有的数据
            divs = html_data.xpath(' //div[@searchtype="intern"]')
            for div in divs:
                # 提取岗位名称
                job_name = div.xpath('.//a[@class="title ellipsis font"]/text()')[0]
                for k, v in res.items():
                    job_name = job_name.replace(k, v, -1).replace('v十', 'y', -1)

                # 提取岗位薪资
                money = div.xpath('.//span[@class="day font"]/text()')[0]
                for k, v in res.items():
                    money = money.replace(k, v, -1).replace('o','0', -1)

                # 提取公司名称
                company = div.xpath('.//a[@class="title ellipsis"]/text()')[0]
                for k, v in res.items():
                    company = company.replace(k, v, -1)

                print(job_name, money, company)

            page.wait_for_timeout(6000)

        except TimeoutError as er:
            print('页面在2秒内还没有加载完成!!!')
