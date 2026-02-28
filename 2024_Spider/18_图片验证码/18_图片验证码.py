# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/4/10 20:20
# @Author : 连三保
# @Version: V 1.0
# @File : 18_图片验证码.py
# @desc : 分类
# 1、滑动
# 2、纯英文，纯数字
# 3、英文数字组合
# 4、汉字 成语点击
# 5、拼图
# 6、物品选择 4张图片
# 7、图片摆正


'''
使用第三库去识别验证码
    一、ddddocr库：
        pip install ddddocr -i https://pypi.tuna.tsinghua.edu.cn/simple
        优点：免费
        缺点：准备度不高
        from ddddocr import DdddOcr # 首字母大写

        # 创建ocr对象
        ocr = DdddOcr(show_ad=False)

        # 识别图片中内容
        res = ocr.classification(open('xxx.jpg', 'rb').read())

        # 输出
        print(res)

    二、使用大码平台（专门破解验证码的收费平台）
        优点：准确度高
        缺点：
        https://www.chaojiying.com/
            使用：
                1、注册/登录
                2、点击用户中心，充值
                3、点击软件ID==》生成一个软件ID
                4、点击开发者文档，选择Python，点击’这里下载‘

            from chaojiying import Chaojiying_Client

            if __name__ == '__main__':
                # 创建客户端对象
                chaojiying = Chaojiying_Client('Sanbao', 'Chaojiying+2025', '969044')  # 用户中心>>软件ID 生成一个替换 96001
                # 验证码图片对象
                im = open('a.jpg', 'rb').read()  # 本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
                # 打印识别结果
                print(chaojiying.PostPic(im, 1902))  # 1902 验证码类型  官方网站>>价格体系 3.4+版 print 后要加()
                # print chaojiying.PostPic(base64_str, 1902)  #此处为传入 base64代码

    三、实现方法：
        1.requests + ddddocr
        2.playwright + ddddocr
        3.playwright + 打码平台
'''

#实现方法1
# 问题：如何保证当前获取到的验证码和服务器当前需要的验证码保持一致
# 解决：想办法让下载验证码携带的cookie，和发送请求的cookie要一致
# 超级鹰验证码获取地址：https://www.chaojiying.com/include/code/code.php?u=1&t=0.7659833663529517
#                   https://www.chaojiying.com/include/code/code.php?u=1&t=0.9941311277036577
# 超级鹰登录地址：https://www.chaojiying.com/user/login/
# from random import random
#
# import requests
# from ddddocr import DdddOcr
# from fake_useragent import FakeUserAgent
#
# # 获取图片验证码地址
# url = f'https://www.chaojiying.com/include/code/code.php?u=1&t={random()}'
#
# header = {
#     'User-Agent': FakeUserAgent().random
# }
# # 创建sesseion对象
# session = requests.Session()
# response = session.get(url, headers=header)
# with open('pic4.jpg', 'wb') as f:
#     f.write(response.content)
#
# # 2.ddddocr识别验证码图片，得到验证码
# ocr = DdddOcr(show_ad=False)
# res = ocr.classification(open('pic4.jpg', 'rb').read())
#
# print(f'识别结果：{res}')
#
# # 3.requests携带账号，密码，验证码，发送登录请求
# login_url = 'https://www.chaojiying.com/user/login/'
#
# # 登录表单
# from_data = {
#     'user': 'Sanbao',
#     'pass': 'Chaojiying+2025',
#     'imgtxt': res,
#     'act': 1
# }
#
# login_response = session.post(login_url, data=from_data, headers=header)
# print(login_response.text)


#实现方法2 playwright+ddddocr 1.打开登录页面 2.输入账号，密码 3.使用ddddocr识别验证码图片，得到验证码 4.输入验证码 5.点击登录
from ddddocr import DdddOcr
from playwright.sync_api import sync_playwright

def download_image(response):
    """拦截浏览器请求的响应数据【监听响应】"""
    image_url = 'https://www.chaojiying.com/include/code/code.php'
    request_url = response.url
    if request_url.startswith(image_url):
        with open('pic5.jpg', 'wb') as f:
            f.write(response.body())

if __name__ == '__main__':
    while True:
        with sync_playwright() as p:
            # 要先在本地谷歌浏览器先登录目标网址，然后启动本地浏览器
            browser = p.chromium.launch_persistent_context(
                executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                user_data_dir=r'D:\chrome_userData',
                headless=False)
            # 3.创建新页面 ** 注意全屏no_viewport=True
            # page = browser.new_page(no_viewport=True)
            page = browser.new_page()

            # 4.发送请求 timeout,referer 跳转，wait_until[load:等待页面完全加载,domcontentloaded:等待DOM内容加载完成，即HTML文档已解析完毕, networkided:]
            try:

                # 添加JS脚本，隐藏webdriver属性，防止检测出来
                # JS = "Object.defineProperties(navigator, {webdriver: {get: ()=> false}});"
                JS = "Object.defineProperties(navigator, {webdriver: {get: ()=> undefined}});"
                page.add_init_script(JS)

                # 绑定一个事件的处理方法
                page.on("response", download_image)

                # 1.设置等待(方式1)
                page.goto('https://www.chaojiying.com/user/login/')

                page.wait_for_load_state('load')
                # 2.输入用户名
                page.locator('//input[@name="user"]').fill('Sanbao')
                page.wait_for_timeout(2000)
                # 3.输入密码
                page.locator('//input[@name="pass"]').fill('Chaojiying+2025')
                page.wait_for_timeout(2000)

                # 4.使用ddddocr识别验证码图片,侦听(响应去下载)
                ocr = DdddOcr(show_ad=False)
                res = ocr.classification(open('pic5.jpg', 'rb').read())

                # 创建客户端对象
                # chaojiying = Chaojiying_Client('Sanbao', 'Chaojiying+2025', '969044')  # 用户中心>>软件ID 生成一个替换 96001
                # 验证码图片对象
                # im = open('pic5.jpg', 'rb').read()  # 本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
                # 打印识别结果
                # res = chaojiying.PostPic(im, 1902)['pic_str']

                print(f'识别结果：{res}')

                # 5.输入验证码
                page.locator('//input[@name="imgtxt"]').fill(res)
                page.wait_for_timeout(2000)

                # 点击登录
                page.click('//input[@value="登录"]')
                page.wait_for_timeout(2000)

                # 循环识别，直接登录成功才退出
                if '欢迎您' in page.content():
                    print('登录成功！')
                    page.wait_for_timeout(5000)
                    break
                else:
                    print('登录失败！')
                    page.wait_for_timeout(5000)
                    continue

            except TimeoutError as er:
                print('页面在2秒内还没有加载完成!!!')



