# _*_ coding: utf-8 _*_
# @Time : 2025/4/29 19:32
# @Author : 韦丽
# @Version: V 1.0
# @File : Playwright_51Job.py
# @desc : 模拟人为操作，前程无忧上查找喜欢的岗位:

import os
import sys
import time

import pymysql
from pymysql.cursors import DictCursor

from playwright.sync_api import sync_playwright

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)

# 获取所在文件夹路径
dir_path = str(os.path.dirname(script_path))

dir_path = dir_path.replace('\\', '/')


'''
    要求：
        前程无忧网数据采集
            城市招牌
'''


def str_to_json(param):
    pass


def now_date():
    pass


class Job51Playwright:
    # 构造函数
    def __init__(self, url, maxPage):
        # 初始化数据库连接参数
        self.url = url
        self.max_pages = maxPage

        self.result_data = []
        self.notBkResult_data = {}

    # 数据采集
    def exec(self):
        self.f10ResultData = []
        self.STResultData = []
        self.current_page = 1
        """爬虫程序的入口函数"""
        with sync_playwright() as p:
            # 连接本地启动的浏览器
            self.browser = p.chromium.launch_persistent_context(
                executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                user_data_dir=r'D:\chrome_userData', # 在D盘根目录下创建chrome_userData文件夹
                # user_data_dir=r'C:\Users\Administrator\AppData\Local\Google\Chrome\User Data', # 系统默认chrome浏览器数据访问失败
                # proxy = self.proxy_config,
                headless=False)

            try:
                # 选择默认打开的页面
                self.search_page = self.browser.new_page()
                # 添加初始化js脚本代码，隐藏webdriver属性，防止检测出来
                js = "Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});"
                self.search_page.add_init_script(js)
                # 给playwright添加响应事件的侦听处理函数
                self.search_page.on('response', self.notices_response)
                """爬虫执行的主要逻辑"""
                try:
                    self.search_page.goto(self.url, wait_until="domcontentloaded")
                except:
                    self.search_page.goto(self.url, wait_until="domcontentloaded")

                self.search_page.wait_for_timeout(4000)
                try:
                    # 处理自动弹出开户对话框
                    if self.search_page.wait_for_selector('img[onclick="tk_tg_zoomin()"]', timeout=5000):
                        # 点击关闭按钮
                        self.search_page.locator('img[onclick="tk_tg_zoomin()"]').click()
                except:
                    print('自动弹框出错了！')

                # 第一页跳转 输入1
                self.search_page.locator('//input[@id="gotopageindex"]').fill('1')
                self.search_page.wait_for_timeout(2000)

                # 点击确定
                self.search_page.click('//input[@value="确定"]')
                self.search_page.wait_for_timeout(2000)

                # 分页处理
                for index in range(1, self.max_pages):
                    self.current_page += 1
                    try:
                        # 单击下一页
                        nextPage = self.search_page.locator('//div[@class="pagerbox"]/a[text()="下一页"]')
                        if nextPage.is_visible():
                            nextPage.click()
                        else:
                            # 下一页没有了，退出循环
                            break
                    except Exception as e:
                        # 异常了，退出循环
                        break
                    self.search_page.wait_for_timeout(5000)

                # 关闭页面
                self.search_page.close()
            except Exception as e:
                print(f" 数据处理中。。。。。。连接失败： {e}")

        # 有行业的股票数据保存
        if self.result_data:
            print(f' 有行业的股票数据保存: {len(self.result_data)}件')

    # 服务器响应处理
    def notices_response(self, response):
        try:
            request_url = response.url
            # 沪深京A股公告数据：https://np-anotice-stock.eastmoney.com/api/security/ann?cb=jQuery112309602513623424559_1767684708729&sr=-1&page_size=50&page_index=2&ann_type=SHA%2CCYB%2CSZA%2CBJA%2CINV&client_source=web&f_node=0&s_node=0
            if response.headers.get('content-type') == 'text/plain;charset=UTF-8' and request_url.find(
                    '/api/security/ann') != -1:
                # print(f'沪深京A股公告数据: {request_url}')
                # 沪深京A股公告数据抓取
                self.parseNotices(response)

        except Exception as ex:
            print(f'服务器响应处理错误: {str(ex)}')

    # 沪深京A股公告数据抓取
    def parseNotices(self, response):
        try:
            # 当日日期 yyyymmdd
            now_ymd = now_date()
            json_data = str_to_json(response.body())
            result = json_data["data"]
            if result:
                diff_value = result["list"]  # 安全访问 'list' 字段
                for item in diff_value:
                    self.editFields(item, now_ymd)
        except Exception as ex:
            raise Exception(f'板块资金流数据抓取错误: {str(ex)}')

    # 采集数据编辑
    def editFields(self, item, now_ymd):
        try:
            notice_item = {}
            codes = item['codes'][0]
            # art_code
            notice_item["art_code"] = item['art_code']
            # 股票代码
            notice_item["f12"] = codes['stock_code']
            # 股票名称
            notice_item["f14"] = codes['short_name']
            # 公告类型
            if item['columns'] != None and len(item['columns']) > 0:
                notice_item["notice_type"] = item['columns'][0]['column_name']
            else:
                notice_item["notice_type"] = ''
            # 公告标题
            notice_item["title"] = item['title']
            # 公告日期
            notice_item["notice_date"] = item['notice_date']
            print(f'notice_item: {notice_item}')
            # # 数据采集日期
            # notice_item["frq"] = now_ymd
            # self.result_data.append(notice_item)
        except Exception as ex:
            print(f'item: {item}')
            print(f'{item["art_code"]}_数据编辑错误: {str(ex)}')

if __name__ == '__main__':
    es = Job51Playwright('https://login.51job.com/', 50)
    if not es.isExec():
        es.exec()
        time.sleep(5)

    sys.exit()