# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/3/26 15:30
# @Author : 连三保
# @Version: V 1.0
# @File : 13_Playwright携带登录数据.py
# @desc :
from playwright.sync_api import sync_playwright

if __name__ == '__main__':
    with sync_playwright() as p:
        # 要先在本地谷歌浏览器先登录目标网址，然后启动本地浏览器
        # 创建浏览器
        browser = p.chromium.launch(headless=False,
                                    executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                                    args=['--start-maximized'])
        # browser = p.chromium.launch_persistent_context(
        #     executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        #     user_data_dir=r'C:\Users\Administrator\AppData\Local\Google\Chrome\User Data',
        #     headless=False)

        # 3.创建新页面 ** 注意全屏no_viewport=True
        # page = browser.new_page(no_viewport=True)
        page = browser.new_page()

        # 4.发送请求 timeout,referer 跳转，wait_until[load:等待页面完全加载,domcontentloaded:等待DOM内容加载完成，即HTML文档已解析完毕, networkided:]
        try:

            # 添加JS脚本，隐藏webdriver属性，防止检测出来
            # JS = "Object.defineProperties(navigator, {webdriver: {get: ()=> false}});"
            JS = "Object.defineProperties(navigator, {webdriver: {get: ()=> undefined}});"
            page.add_init_script(JS)

            # 设置等待(方式1)
            # page.goto('https://www.so.com/', wait_until='load', timeout=6000)
            # page.goto('https://www.jingdong.com/')
            page.goto('https://piaofang.maoyan.com/dashboard')

            page.wait_for_load_state('load')

            # 定位搜索框并输入关键字
            # page.locator('//input[@id="key"]').fill('华为手机')
            # 点击搜索按钮
            # page.click('//button[text()="搜索"]')

            page.wait_for_timeout(60000)

        except TimeoutError as er:
            print('页面在2秒内还没有加载完成!!!')
