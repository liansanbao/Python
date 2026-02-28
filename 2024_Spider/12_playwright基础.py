# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/3/25 19:51
# @Author : 连三保
# @Version: V 1.0
# @File : 12_playwright基础.py
# @desc : playwright 简单使用

# 导包 #同步
from playwright.sync_api import sync_playwright
# 异步
# from playwright.async_api import async_playwright

if __name__ == '__main__':
    # 单一页面爬取
    # 1.启动 playwright driver 进程
    # with sync_playwright() as p:
    #     # 2.创建浏览器对象(playwright自带的) headless = False 设置为有界面
    #     # browser = p.chromium.launch(headless=False)
    #     # browser = p.firefox.launch(headless=False)
    #
    #     # 2.2 使用自定义的浏览器 ** 注意全屏args=['--start-maximized'],headless=False设置有界面
    #     browser = p.chromium.launch(headless=False, executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe', args=['--start-maximized'])
    #
    #     # 3.创建新页面 ** 注意全屏no_viewport=True
    #     page = browser.new_page(no_viewport=True)
    #
    #     # 4.发送请求 timeout,referer 跳转，wait_until[load:等待页面完全加载,domcontentloaded:等待DOM内容加载完成，即HTML文档已解析完毕, networkided:]
    #     try:
    #         page.goto('https://movie.douban.com/j/chart/top_list?type=13&interval_id=100%3A90&action=&start=0&limit=20',
    #                   wait_until='load', timeout=2000)
    #
    #         # 页面截图
    #         page.screenshot(path='douban.png')
    #
    #         # 页面源码
    #         str_data = page.content()
    #
    #         print(str_data)
    #
    #     except TimeoutError as er:
    #         print('页面在2秒内还没有加载完成!!!')
    #
    #     # 等待时间10秒 (设置单位：毫秒)
    #     page.wait_for_timeout(10000)

    # 多个页面
    with sync_playwright() as p:
        # 2.创建浏览器对象(playwright自带的) headless = False 设置为有界面
        # browser = p.chromium.launch(headless=False)
        # browser = p.firefox.launch(headless=False)

        # 2.2 使用自定义的浏览器 ** 注意全屏args=['--start-maximized'],headless=False设置有界面
        browser = p.chromium.launch(headless=False, executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe', args=['--start-maximized'])

        # 创建上下文
        content = browser.new_context(no_viewport=True)

        # 3.创建新页面 ** 注意全屏no_viewport=True
        # page = browser.new_page(no_viewport=True)
        page = content.new_page()

        # 4.发送请求 timeout,referer 跳转，wait_until[load:等待页面完全加载,domcontentloaded:等待DOM内容加载完成，即HTML文档已解析完毕, networkided:]
        try:
            page.goto('https://movie.douban.com/j/chart/top_list?type=13&interval_id=100%3A90&action=&start=0&limit=20',
                      wait_until='load', timeout=2000)

            # 页面截图
            page.screenshot(path='douban.png')

            # 页面源码
            str_data = page.content()

            print(str_data)

        except TimeoutError as er:
            print('页面在2秒内还没有加载完成!!!')

        # 等待时间10秒 (设置单位：毫秒)
        page.wait_for_timeout(10000)

        page1 = content.new_page()

        page1.goto('https://www.baidu.com')

        # 等待时间10秒 (设置单位：毫秒)
        page1.wait_for_timeout(10000)

