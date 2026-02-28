# _*_ coding: utf-8 _*_
# @Time : 2025/7/26 星期六 15:44
# @Author : 韦丽
# @Version: V 1.0
# @File : Crawl_Move.py
# @desc : 抖音视频下载
import subprocess

from fake_useragent import FakeUserAgent
from playwright.sync_api import sync_playwright
import requests

class DouyinMove:
    def __init__(self, url, movename):
        self.url = url
        self.movename = movename

    # 监听响应采集视频的函数
    def download_video(self, response):
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
            filename = f'视频/{self.movename}.mp4'
            with open(filename, 'wb') as f:
                f.write(response.content)

            print(f'{filename}下载完成。')

    def exec(self):
        # 步骤二：playwright连接谷歌
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False,
                                        executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                                        args=['--start-maximized'])

            # 创建上下文
            context = browser.new_context(no_viewport=True)
            # 选择默认打开的页面
            page = context.pages[0] if context.pages else context.new_page()
            # 添加初始化js脚本代码，隐藏webdriver属性，防止检测出来 (以后写playwright,直接加上这2行代码，防止被反爬)
            js = "Object.defineProperties(navigator, {webdriver:{get:()=>false}});"
            page.add_init_script(js)
            page.on('response', self.download_video)  # 编写一个响应监听器，用来抓取视频
            # 4.访问
            page.goto(self.url)
            page.wait_for_timeout(20000)
            page.close()


if __name__ == '__main__':
    url = "https://v3-web.douyinvod.com/4b0ba003dfa99f533a6cb2768ceac029/6884afe3/video/tos/cn/tos-cn-ve-0015c800/oA4A4qfejIzxlJQAbbigNvhBlhEA9kzANBjKiB/?a=6383&ch=11&cr=3&dr=0&lr=all&cd=0%7C0%7C0%7C3&br=118&bt=118&cs=0&ds=6&ft=4TMWc6DhppftDFLB.CF.C_fauVq0InDEf~Gc6B0gTT8POQdHDDq46y_iS4UscusZ.&mime_type=video_mp4&qs=12&rc=PDppNjhpM2dpOjtmZGg4aEBpajZpdTw6ZmxucTMzNGkzM0AtLzNeNV8xNjAxYzYwYjEtYSNhZXItcjRnb2xgLS1kLWFzcw%3D%3D&btag=80000e00028000&cquery=101n_100B_100x_100z_100o&dy_q=1753515337&feature_id=46a7bb47b4fd1280f3d3825bf2b29388&l=2025072615353697E35F8CE04D1ABF2216&__vid=7345737988317433115"
    moveName= '新的异象新的方向'
    crawl = DouyinMove(url, moveName)
    crawl.exec()