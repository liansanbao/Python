# _*_ coding: utf-8 _*_
# @Time : 2025/4/14 23:43
# @Author : 韦丽
# @Version: V 1.0
# @File : 17_playwright抓取快手视频.py
# @desc :
"""
快手视频采集思路(一定要事先在本地谷歌登录好快手)
1.找到要采集的博主的主页地址：https://www.kuaishou.com/profile/3x6ekzzxzrbbqe2
2.通过playwright打开主页
3.点击第一个视频，进入刷视频页面
4.写个for循环去刷视频，每个视频看2到6秒，然后每次循环点击下一个视频
5.写一个响应监听器，去获取返回视频内容的请求信息【注意点：视频无法在响应拦截中直接保存】
    5.1 视频网站返回的视频资源响应状态码一般是206，而且内容是流式返回(一点一点返回的)
    5.2 所以对于流式返回的内容，无法在playwright的响应拦截中直接获取到所有的响应体
6.在拿到视频内容请求的url地址之后，再写个代码发送请求进行下载，然后将返回的内容保存为文件
"""

import random
import subprocess
import time
from playwright.sync_api import sync_playwright
import requests

# 步骤一：开启谷歌的远程调试模式(代码开启【本地浏览器】)
path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
params = "--remote-debugging-port=6789"
cmd = f'"{path}" {params}'
subprocess.Popen(cmd, shell=True)
# 等待2秒钟，然后再执行下面的代码
time.sleep(2)


# 监听响应采集视频的函数
def download_video(response):
    # 1.筛选返回内容是视频的请求
    # 获取响应状态码
    status = response.status
    # 获取请求头中的响应内容类型
    content_type = response.headers.get('content-type')
    # 判断响应状态码是否为206以及请求头中的content-type是否为video/mp4
    if status == 206 and content_type == 'video/mp4':
        url = response.url
        print(f'视频请求地址;{url}')

        # 2.视频下载保存
        response = requests.get(url, headers=response.request.headers)
        filename = '视频/' + url.split('?')[0][-20:]
        print(f'视频文件：{filename}')
        with open(filename, 'wb') as f:
            f.write(response.content)


# 步骤二：playwright连接谷歌
with sync_playwright() as p:
    # 连接本地启动的浏览器               本机(远程)IP:监听端口
    browser = p.chromium.connect_over_cdp('http://127.0.0.1:6789')
    # 选择默认的浏览器上下文对象
    context = browser.contexts[0]
    # 选择默认打开的页面
    page = context.pages[0] if context.pages else context.new_page()
    # 添加初始化js脚本代码，隐藏webdriver属性，防止检测出来 (以后写playwright,直接加上这2行代码，防止被反爬)
    js = "Object.defineProperties(navigator, {webdriver:{get:()=>false}});"
    page.add_init_script(js)
    page.on('response', download_video)  # 编写一个响应监听器，用来抓取视频
    # 4.访问
    page.goto("https://www.kuaishou.com/profile/3x6ekzzxzrbbqe2")
    page.wait_for_timeout(2000)
    page.reload()  # 刷新页面
    page.wait_for_timeout(2000)
    # 获取博主作品数
    count = page.locator('//div[@class="user-detail-item"]/h3').inner_text()
    print(f'博主作品数量为:{count}', type(count))
    # 2.定位获取第一个视频
    one = page.locator('//div[@class="video-card-main"]').first
    # 3.点击视频，进入到刷视频的页面
    one.click()
    download_count = 4
    # 4.循环刷视频
    for i in range(int(count) - 1):
        if i >= 4:
            break
        # 模拟人观看的操作，每个视频随机停留2到7秒
        page.wait_for_timeout(random.randint(2000, 7000))
        # 点击下一个视频
        next_btn = page.locator('//div[@class="switch-item video-switch-next"]')
        next_btn.click()
        print(f'视频数量：{i}')

    print('马上要结束了。')
    # 等待2秒
    page.wait_for_timeout(10000)

"""

https://v2.kwaicdn.com/ksc2/Q-kjzJZE3M9SYNS6zA9aGRl_rm1-uCMRfaTfubs0XqRKJhThW9FmDIzme56enhf0Ch1uC8IA2dYxhClLf4bigwHWXSBnbUGtPLyTYuByQWtR3yqfBMDkioOxugGxYgAs.mp4
?
pkey=AAUkB-tPu4R4QWm4LLD9BtTjoe_sO8Ru3tEk-IK7b6hoXMu7cTvYFSBJqdlJOjQqLVR69a7zfSqjaqaVusboj9e3kQ5YuNYUwoXM5BhSpmH68f--l4VGyj-ARUeE2mIH3II&tag=1-1740059205-unknown-0-3kcn8htva3-b54965ede5e55c07&clientCacheKey=3xrnrday3qyunpc_41966f6a&di=3a1417d7&bp=14734&tt=hd15&ss=vp
"""
