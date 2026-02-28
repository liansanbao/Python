# _*_ coding: utf-8 _*_
# @Time : 2025/4/15 12:51
# @Author : 韦丽
# @Version: V 1.0
# @File : 17_playwright翻页抓取图片.py
# @desc :
import subprocess
import time
from playwright.sync_api import sync_playwright


class DahaiSpider(object):
    def __init__(self, number=1):
        """定义远程调试参数"""
        path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        params = "--remote-debugging-port=6789"
        cmd = f'"{path}" {params}'
        subprocess.Popen(cmd, shell=True)
        # 定义实例变量number_,表示翻页的页数
        self.number_ = number
        time.sleep(2)

    def main(self):
        """爬虫程序的入口函数"""
        with sync_playwright() as p:
            # 连接本地启动的浏览器
            browser = p.chromium.connect_over_cdp('http://127.0.0.1:6789')
            # 选择默认的浏览器上下文对象
            context = browser.contexts[0]
            # 选择默认打开的页面
            self.page = context.pages[0] if context.pages else context.new_page()
            # 添加初始化js脚本代码，隐藏webdriver属性，防止检测出来 (以后写playwright,直接加上这2行代码，防止被反爬)
            js = "Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});"
            self.page.add_init_script(js)
            # 进行数据提取，执行run_spider方法
            self.run_spider()
            # 关闭页面
            self.page.close()

    def run_spider(self):
        """爬虫执行的主要逻辑"""
        # 给playwright添加响应事件的侦听处理函数
        self.page.on('response', self.handler_response)
        self.page.goto("https://pic.netbian.com/")

        # 翻页抓取
        for i in range(1, 3):
            print(f'第{i}页图片抓取完毕！！')
            self.page.wait_for_load_state('networkidle')
            self.page.wait_for_timeout(2000)
            # 滚动到下一页按钮可见
            self.page.locator('//li[@class="nextpage"]').scroll_into_view_if_needed()
            self.page.wait_for_timeout(2000)
            # 点击下一页
            self.page.click('//li[@class="nextpage"]')

        self.page.wait_for_timeout(10000)

    def handler_response(self, response):
        """拦截浏览器请求的响应数据"""
        # 判断一下这个响应的内容是否为黑乎乎
        if response.headers.get('content-type') == 'image/jpeg':
            url = response.url
            print('捕获到的图片请求地址:', url)
            # 从url地址中截取图片名字
            filename = url.split('/')[-1]
            with open(f'photo/{filename}', 'wb') as f:
                f.write(response.body())


if __name__ == '__main__':
    xiaohai = DahaiSpider()
    xiaohai.main()

"""
目标网站：https://pic.netbian.com/
该网站必须要先在本地谷歌登录，否则使用playwright执行代码拿不到正常的数据(会检测)
"""