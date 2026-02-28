# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/3/25 23:07
# @Author : 连三保
# @Version: V 1.0
# @File : 13_Playwright之IFrame操作.py
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
            page.goto('https://music.163.com')

            page.wait_for_timeout(4000)

            # 切换指定的Iframe中
            frame_obj = page.frame_locator('//iframe[@id="g_iframe"]')
            page.wait_for_timeout(1000)

            # 定位frame内容里的元素
            frame_obj.locator('//ul/li[1]/p[@class="dec"]/a').click(timeout=10000)

            # 设置等待load(方式1)
            # page.wait_for_load_state('load')
            # 页面截图
            # page.screenshot(path='douban.png')
            page.wait_for_timeout(5000)


        except TimeoutError as er:
            print('页面在2秒内还没有加载完成!!!')

