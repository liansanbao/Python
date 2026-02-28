# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/3/25 22:37
# @Author : 连三保
# @Version: V 1.0
# @File : 13_Playwright文本和属性值获取.py
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
            page.goto('https://quote.eastmoney.com/ztb/detail#type=ztgc')

            # 设置等待load(方式1)
            # page.wait_for_load_state('load')
            # 页面截图
            # page.screenshot(path='douban.png')
            page.wait_for_timeout(5000)

            # 获取元素文本值
            # 批量获取多个元素的内部文本内容，返回列表 all_inner_texts()
            # 获取单个的内部文本内容，返回字符串 inner_text()
            # 获取元素 all(),在通过inner_text()
            element_list = page.locator('//table[@id="zrzttable"]').all()
            for element in element_list:
                print(element.inner_text())

            # 获取元素属性值
            # get_attribute('href')
            a_list = page.locator('//table[@id="zrzttable"]//td[2]//a').all()
            for element in a_list:
                print('https:' + element.get_attribute('href'))


        except TimeoutError as er:
            print('页面在2秒内还没有加载完成!!!')
