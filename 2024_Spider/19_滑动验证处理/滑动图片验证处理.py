# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/4/11 10:46
# @Author : 连三保
# @Version: V 1.0
# @File : 滑动图片验证处理.py
# @desc : 目标网站：https://www.geetest.com/adaptive-captcha

'''
技术方案：playwright + ddddocr
出力步骤：
    一、进入到滑动验证的操作界面
    二、识别滑动的轨迹距离（关键）
    三、拖动鼠标进行滑动验证

'''
import random
import re

import ddddocr
import requests
from playwright.sync_api import sync_playwright

def photo():
    # 滑块图片读取
    sli = open('xiao.png', 'rb').read()
    # 背景图片读取
    bg = open('da.png', 'rb').read()
    # ddddocr初始化
    ocr = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)
    result = ocr.slide_match(sli, bg, simple_target=True)
    print(f'result: {result}')

# 图片内容读取
def readImage(imageBytes):
    # 4.使用ddddocr识别验证码图片,侦听(响应去下载)
    ocr = ddddocr.DdddOcr(show_ad=False)
    res = ocr.classification(imageBytes)
    print(f'图片识别结果：{res}')

def download_image(response):
    """拦截浏览器请求的响应数据【监听响应】"""
    image_url = 'https://static.geetest.com/captcha_v4/e70fbf1d77/slide/1e8ffe6222/2022-04-21T09/slice/9cc7c1483c7e4c8fb9779bd692b9f8ed.png'
    request_url = response.url
    if request_url.startswith(image_url):
        with open('pic5.jpg', 'wb') as f:
            f.write(response.body())

def get_track(distance):
    """一个生成模拟人为拖动轨迹的算法"""
    track = []
    # 从哪个位置开始滑动
    current = 0
    # 减速的阈值
    mid = distance * 4 / 5
    # 时间
    t = 0.2
    # 速度
    v = 0
    while current < distance:
        if current < mid:
            a = 2  # 加速值
        else:
            a = -3
        v0 = v
        v = v0 + a * t  # 新的移动速度
        move = v0 * t + 1 / 2 * a * t * t  # 移动的距离
        track.append(round(move))  # 加入移动轨迹
        current += move  # current 记录当前位置
    track.append(distance - sum(track))
    return track

# 选择滑动拼图验证
def runHuadong():
    while True:
        with sync_playwright() as p:
            # 要先在本地谷歌浏览器先登录目标网址，然后启动本地浏览器
            browser = p.chromium.launch(headless=False,
                                        executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                                        args=['--start-maximized'])
            # 3.创建新页面 ** 注意全屏no_viewport=True
            # page = browser.new_page(no_viewport=True)
            page = browser.new_page(no_viewport=True)

            # 4.发送请求 timeout,referer 跳转，wait_until[load:等待页面完全加载,domcontentloaded:等待DOM内容加载完成，即HTML文档已解析完毕, networkided:]
            try:

                # 添加JS脚本，隐藏webdriver属性，防止检测出来
                # JS = "Object.defineProperties(navigator, {webdriver: {get: ()=> false}});"
                JS = "Object.defineProperties(navigator, {webdriver: {get: ()=> undefined}});"
                page.add_init_script(JS)

                # 绑定一个事件的处理方法
                # page.on("response", download_image)

                # 1.设置等待(方式1)
                page.goto('https://www.geetest.com/adaptive-captcha')

                page.wait_for_load_state('load')
                page.locator('//div[@class="tab-item tab-item-0"]').click()
                page.wait_for_timeout(2000)
                # 2.选择滑动拼图验证
                page.locator('//div[@class="tab-item tab-item-1"]').click()
                page.wait_for_timeout(2000)

                # 3.单击按钮开始验证
                page.locator('//div[@aria-label="点击按钮开始验证"]').click()
                page.wait_for_timeout(7000)
                # 4.定位滑块图片和背景图片所在标签
                slice_loc = page.locator('.geetest_slice_bg').get_attribute('style')
                bg_loc = page.locator('.geetest_bg').get_attribute('style')
                slice_loc_url = re.findall(r'background-image: url\("(.*?)"\);', slice_loc)[0]
                bg_loc_url = re.findall(r'background-image: url\("(.*?)"\);', bg_loc)[0]
                print(f'滑块图片下载地址：{slice_loc_url}')
                print(f'滑块背景图片下载地址：{bg_loc_url}')
                page.wait_for_timeout(5000)
                # 图片下载
                slice_loc_content = requests.get(slice_loc_url).content
                bg_loc_content = requests.get(bg_loc_url).content

                # 5识别滑动的轨迹宽度
                ocr = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)
                result = ocr.slide_match(slice_loc_content, bg_loc_content, simple_target=True)
                print(f'识别结果：{result}, 要滑动的距离：{result["target"][0]}')

                # 6选中托块，获取滑块按钮的宽度
                w = page.locator('.geetest_track .geetest_btn').bounding_box()['width']
                x = result["target"][0] + w / 2
                res = get_track(x)
                print(f'生成轨迹行为：{res}')

                # 7滑动行为
                # 7.1 选中滑动模块按钮，鼠标悬停不能点击
                btn = page.locator('.geetest_track .geetest_btn')
                btn.hover()

                # 进行滑动操作
                location = btn.bounding_box()
                btn_x = location['x']
                btn_y = location['y']
                print(f'拖动滑块起始位置：{btn_x, btn_y}')
                s = btn_x
                h = btn_y + random.randint(-5, 5)
                # 按住鼠标
                page.mouse.down()
                for v in res:
                    s = s + v
                    page.mouse.move(s, h)

                # 松开鼠标
                page.mouse.up()
                page.wait_for_timeout(5000)

                # 判断
                if page.locator('//div[text()="验证通过"]').is_visible():
                    break


            except TimeoutError as er:
                print('页面在2秒内还没有加载完成!!!')

# 选择图片点选验证
def runDianxuan():
    while True:
        with sync_playwright() as p:
            # 要先在本地谷歌浏览器先登录目标网址，然后启动本地浏览器
            browser = p.chromium.launch(headless=False,
                                        executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                                        args=['--start-maximized'])
            # 3.创建新页面 ** 注意全屏no_viewport=True
            # page = browser.new_page(no_viewport=True)
            page = browser.new_page(no_viewport=True)

            # 4.发送请求 timeout,referer 跳转，wait_until[load:等待页面完全加载,domcontentloaded:等待DOM内容加载完成，即HTML文档已解析完毕, networkided:]
            try:

                # 添加JS脚本，隐藏webdriver属性，防止检测出来
                # JS = "Object.defineProperties(navigator, {webdriver: {get: ()=> false}});"
                JS = "Object.defineProperties(navigator, {webdriver: {get: ()=> undefined}});"
                page.add_init_script(JS)

                # 绑定一个事件的处理方法
                # page.on("response", download_image)

                # 1.设置等待(方式1)
                page.goto('https://www.geetest.com/adaptive-captcha')

                page.wait_for_load_state('load')
                page.locator('//div[@class="tab-item tab-item-0"]').click()
                page.wait_for_timeout(2000)
                # 2.选择文字点选验证
                page.locator('//div[@class="tab-item tab-item-2"]').click()
                page.wait_for_timeout(2000)

                # 3.单击按钮开始验证
                page.locator('//div[@aria-label="点击按钮开始验证"]').click()
                page.wait_for_timeout(7000)
                # 4.定位滑块图片和背景图片所在标签
                # slice_loc = page.locator('.geetest_slice_bg').get_attribute('style')
                bg_loc = page.locator('.geetest_bg').get_attribute('style')
                # slice_loc_url = re.findall(r'background-image: url\("(.*?)"\);', slice_loc)[0]
                bg_loc_url = re.findall(r'background-image: url\("(.*?)"\);', bg_loc)[0]
                # print(f'滑块图片下载地址：{slice_loc_url}')
                print(f'滑块背景图片下载地址：{bg_loc_url}')
                page.wait_for_timeout(5000)
                # 图片下载
                # slice_loc_content = requests.get(slice_loc_url).content
                bg_loc_content = requests.get(bg_loc_url).content
                readImage(bg_loc_content)

                page.wait_for_timeout(5000)

                page.close()
                break
                #
                # # 5识别滑动的轨迹宽度
                # # ocr = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)
                # # result = ocr.slide_match(slice_loc_content, bg_loc_content, simple_target=True)
                # # print(f'识别结果：{result}, 要滑动的距离：{result["target"][0]}')
                #
                # # 6选中托块，获取滑块按钮的宽度
                # # w = page.locator('.geetest_track .geetest_btn').bounding_box()['width']
                # # x = result["target"][0] + w / 2
                # # res = get_track(x)
                # # print(f'生成轨迹行为：{res}')
                #
                # # 7滑动行为
                # # 7.1 选中滑动模块按钮，鼠标悬停不能点击
                # btn = page.locator('.geetest_track .geetest_btn')
                # btn.hover()
                #
                # # 进行滑动操作
                # location = btn.bounding_box()
                # btn_x = location['x']
                # btn_y = location['y']
                # print(f'拖动滑块起始位置：{btn_x, btn_y}')
                # s = btn_x
                # h = btn_y + random.randint(-5, 5)
                # # 按住鼠标
                # page.mouse.down()
                # for v in res:
                #     s = s + v
                #     page.mouse.move(s, h)
                #
                # # 松开鼠标
                # page.mouse.up()
                # page.wait_for_timeout(5000)
                #
                # # 判断
                # if page.locator('//div[text()="验证通过"]').is_visible():
                #     break


            except TimeoutError as er:
                print('页面在2秒内还没有加载完成!!!')


if __name__ == '__main__':
    # photo()
    runHuadong()
    # runDianxuan()


