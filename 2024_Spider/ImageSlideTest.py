# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/3/27 21:00
# @Author : 连三保
# @Version: V 1.0
# @File : ImageSlideTest.py
# @desc :
"""
目标网站：https://www.geetest.com/adaptive-captcha-demo
工具：playwright + ddddocr
处理步骤：
    一.进入到滑动验证的操作界面
    二.识别滑动的轨迹距离(最关键)
    三.拖动鼠标进行滑动验证
"""

import random
import ddddocr
import requests
import re
from playwright.sync_api import sync_playwright


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


def run():
    with sync_playwright() as p:
        # 1.创建浏览器
        broswer = p.chromium.launch(headless=False, args=['--start-maximized'])

        # 2.创建上下文
        context = broswer.new_context(no_viewport=True)

        # 3.创建页面
        page = context.new_page()

        # 添加初始化js脚本代码，隐藏webdriver属性，防止检测出来(以后写playwright，直接先加上这2行代码，防止被反爬)
        js = "Object.defineProperties(navigator, {webdriver:{get:()=>false}});"
        page.add_init_script(js)

        # 4.访问目标网站  注意  写入的url必须是http或者https开头的
        page.goto('https://www.geetest.com/adaptive-captcha-demo')

        # 一.进入到滑动验证的操作界面
        # 1.1 选择'滑动拼图验证'
        page.click('//div[@class="tab-item tab-item-1"]')
        page.wait_for_timeout(2000)

        # 1.2 点击'点击按钮开始验证'
        page.click('//div[@aria-label="点击按钮开始验证"]')
        page.wait_for_timeout(2000)
        while True:
            # 二.识别滑动的轨迹距离(最关键)
            # 2.1 下载滑动图片和背景图片
            # 2.1.1 定位滑动图片和背景图片所在棱
            slice_loc = page.locator('.geetest_slice_bg').get_attribute('style')
            bg_loc = page.locator('.geetest_bg').get_attribute('style')

            # 通过正则提取图片的下载地址
            slice_url = re.findall(r'url\("(.*?)"\)', slice_loc)[0]
            bg_url = re.findall(r'url\("(.*?)"\)', bg_loc)[0]
            # print('滑块图片下载地址:',slice_url)
            # print('背景图片下载地址:',bg_url)

            # 2.1.2 下载滑动图片和背景图片(获取字节数据即可)
            slice_content = requests.get(slice_url).content
            bg_content = requests.get(bg_url).content

            # 2.2 识别滑动的轨迹宽度
            # 2.2.1 识别缺口在背景图中的坐标位置
            ocr = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)
            result = ocr.slide_match(slice_content, bg_content, simple_target=True)
            print('识别结果:', result)

            # 从识别结果中获取滑动的距离X值(由于拖动的时候是通过滑动中间点进行移动的，所以需要加上滑动按钮宽度的一半)
            # 定位滑动按钮元素，获取滑块按钮的
            w = page.locator('.geetest_track .geetest_btn').bounding_box()['width']
            x = result['target'][0] + w / 2
            print('要滑动的距离为:', x)

            # 2.3 根据滑动的总距离，生成滑动轨迹
            dis = get_track(x)
            print('生成滑动的轨迹为:', dis)

            # 3.执行滑动验证操作
            # 3.1 鼠标移动到滑动按钮上方(不能点击)
            # 3.1.1 定位滑块按钮元素
            btn = page.locator('.geetest_track .geetest_btn')

            # 3.1.2 把鼠标移动到滑块按钮上方
            btn.hover()

            # 3.1.3 获取滑块按钮的x和y的坐标
            location = btn.bounding_box()
            print('按钮的坐标为:', location)
            btn_x = location['x']
            btn_y = location['y']

            # 3.2 按钮鼠标(不能点击)
            page.mouse.down()

            # 设置鼠标移动的xy起始位置
            s = btn_x
            h = btn_y + random.randint(-5, 5)

            # 3.2 拖动鼠标
            for i in dis:
                s = s + i
                page.mouse.move(s, h)

            # 模拟人的不完美操作，调整最终位置(给定一个随机小范围的误差值)
            page.mouse.move(s + random.randint(-5, 5), h)

            # 3.4 松开鼠标
            page.mouse.up()

            # 4. 判断验证是否通过，通过则结束循环
            page.wait_for_timeout(4000)
            # 判断验证通过是否存在
            if page.locator("//div[text()='验证通过']").is_visible():
                break

        page.wait_for_timeout(20000)

if __name__ == '__main__':
    run()