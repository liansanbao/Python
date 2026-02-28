# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/3/26 16:03
# @Author : 连三保
# @Version: V 1.0
# @File : 13_Playwright连接开启远程调试谷歌.py
# @desc : 远程调试模式（自带本地登录状态）
#         1.控制本地浏览器
#         2.控制远程浏览器   D:\learing\Python\PycharmProjects\untitled\爬虫\14-playwright项目实战.mp4 参考

import subprocess
import os
from playwright.sync_api import sync_playwright

# 步骤
#      1.开启谷歌的远程调试模式(代码开启【本地浏览器】/cmd终端开启【远程浏览器】)
import time

path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
#      2.指定开启远程调试模式的参数
params = '--remote-debugging-port=6789'
#      3.组合命令
cmd = f'"{path}" {params}'

#      4.1 执行cmd命令：通过subprocess
subprocess.run(cmd, shell=True)

#      4.2 执行cmd命令：通过os模块
# os.popen(cmd)

# time.sleep(2)

# 步骤二：playwright连接谷歌
with sync_playwright() as p:
    # 创建浏览器
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:6789')

    # 3.创建新页面 ** 注意全屏no_viewport=True
    # page = browser.new_page(no_viewport=True)
    context = browser.contexts[0]
    # page = context.pages[0] # 选择默认打开的页面
    page = context.pages[0] if context.pages else context.new_page()

    # 4.发送请求 timeout,referer 跳转，wait_until[load:等待页面完全加载,domcontentloaded:等待DOM内容加载完成，即HTML文档已解析完毕, networkided:]
    try:

        # 添加JS脚本，隐藏webdriver属性，防止检测出来
        # JS = "Object.defineProperties(navigator, {webdriver: {get: ()=> false}});"
        JS = "Object.defineProperties(navigator, {webdriver: {get: ()=> undefined}});"
        page.add_init_script(JS)

        # 设置等待(方式1)
        # page.goto('https://www.so.com/', wait_until='load', timeout=6000)
        page.goto('https://www.jingdong.com/')

        page.wait_for_load_state('load')

        # 定位搜索框并输入关键字
        page.locator('//input[@id="key"]').fill('华为手机')
        # 点击搜索按钮
        page.click('//button[text()="搜索"]')

        page.wait_for_timeout(2000)

        page.close()

    except TimeoutError as er:
        print('页面在2秒内还没有加载完成!!!')
