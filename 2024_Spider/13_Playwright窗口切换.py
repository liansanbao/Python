# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/3/25 22:50
# @Author : 连三保
# @Version: V 1.0
# @File : 13_Playwright窗口切换.py
# @desc :
from playwright.sync_api import sync_playwright

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
            # 设置等待(方式1)
            # page.goto('https://www.so.com/', wait_until='load', timeout=6000)
            page.goto('https://www.eastmoney.com/')

            # 设置等待时间
            page.wait_for_timeout(2000)
            # 点击链接，打开新窗口，访问第二个页面，数据中心， 当前页面索引为1
            page.locator('//div[@class="hq_con_data"]/div/a[text()="数据中心"]').click()
            # 设置等待时间
            page.wait_for_timeout(2000)

            # 窗口切换
            # 1.获取当前所有页面的索引
            window_list = content.pages
            # 2.获取数据中心页面的索引
            newPage = window_list[1]

            print(page.title())
            print(newPage.title())


        except TimeoutError as er:
            print('页面在2秒内还没有加载完成!!!')
