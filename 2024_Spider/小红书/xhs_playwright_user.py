# _*_ coding: utf-8 _*_
# @Time : 2025/5/9 8:17
# @Author : 韦丽
# @Version: V 1.0
# @File : xhs_playwright.py
# @desc : 需要采集每个评论的 评论人、评论时间、评论内容、小红书号、IP属地（小红书号在用户的主页里面）
#         https://www.xiaohongshu.com/search_result?keyword=%25E8%258B%25B1%25E8%25AF%25AD%25E5%25AD%25A6%25E4%25B9%25A0%25E6%259C%25BA&source=web_search_result_notes&type=51
import datetime
import json
import os
import time
import urllib
from functools import partial

import execjs
import jsonpath
import requests
from fake_useragent import FakeUserAgent
from itemadapter import ItemAdapter
from playwright.sync_api import sync_playwright
from pymongo import MongoClient

'''
    要求：
        1.采集每个评论的 评论人、评论时间、评论内容、小红书号、IP属地（小红书号在用户的主页里面）
        2.采集的数据，存放mongodb，导出为json文件进行交付
'''
class XhsPlaywrightUser:
    def __init__(self):
        self.name = 'xhs_crawl'
        # 用户信息存储, 减少访问服务器的负担
        self.userInfoDect = self.load_existing_json() # 加载已有的用户信息
        # 以追加模式打开文件，保留历史数据
        self.file_ = open(f'{self.name}.json', 'a', encoding='utf-8')

    def __del__(self):
        print(f'{self.jsonFile} 文件关闭了。')
        self.file_.close()

    # 数据保存
    def save_item(self, item):
        # 先把键值对的item对象转成字典
        py_dict = dict(item)
        if py_dict['userId'] != '' and py_dict["redId"] != '':
            new_dic = {py_dict["userId"]: [py_dict["userName"], py_dict["redId"], py_dict["userIp"]]}
            # 将新数据按行追加写入文件
            line = json.dumps(ItemAdapter(new_dic).asdict(), ensure_ascii=False) + '\n'
            self.file_.write(line)
            print(f'save_item process:{new_dic}')

    # 读取已有的用户信息
    def load_existing_json(self):
        # 读取userinfo.json文件中所有信息
        result = {}
        try:
            with open(f'{self.name}.json', 'r', encoding='utf-8') as r:
                for line in r:
                    line = line.strip()
                    if line:  # 跳过空行
                        data = json.loads(line)
                        result.update(data)
        except (FileNotFoundError, json.JSONDecodeError):
            return dict()
        return result

    # text值取得 （替换：小红书号：/IP属地：）
    def getText(self, li):
        try:
            if li.count() > 0:
                return li.inner_text().replace('小红书号：', '').replace('IP属地：', '')
        except:
            pass
        return ''

    # 出力execl文件
    def save_json(self):
        nowdate = datetime.date.today().strftime('%Y%m%d')
        with open(f'xhs_crawl_{nowdate}.json', 'w', encoding='utf-8') as w:
            for item in self.result_data:
                # 把字典数据转json
                json_data = json.dumps(item, ensure_ascii=False) + ', \n'
                w.write(json_data)

    # MongoDB中保存
    def save_mongodb(self):
        with MongoClient(host='192.168.1.15', port=27017) as con:  # 实例化mongoclient
            collection = con['xiaohongshuSpider']['xhs_crawl']
            for py_dict in self.result_data:
                with con.start_session() as session:
                    session.start_transaction()
                    print(py_dict)
                    try:
                        # 以详情页作为更新条件，upsert=True不满足就进行插入操作
                        resutl = collection.update_one(
                            {'评论内容id': py_dict['评论内容id']},
                            {'$set': py_dict},
                            upsert=True,
                            session=session
                        )
                        print(f'更新件数： {resutl.modified_count}')
                        session.commit_transaction()
                    except Exception as e:
                        session.abort_transaction()

    # 小红书评论数据采集
    def exec(self):
        url = 'https://www.xiaohongshu.com/search_result?keyword=%25E8%258B%25B1%25E8%25AF%25AD%25E5%25AD%25A6%25E4%25B9%25A0%25E6%259C%25BA&source=web_search_result_notes&type=51'
        self.result_data = []
        """爬虫程序的入口函数"""
        with sync_playwright() as p:
            # 连接本地启动的浏览器
            self.browser = p.chromium.launch_persistent_context(
                executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                user_data_dir=r'D:\chrome_userData', # 在D盘根目录下创建chrome_userData文件夹
                # user_data_dir=r'C:\Users\Administrator\AppData\Local\Google\Chrome\User Data', # 系统默认chrome浏览器数据访问失败
                headless=False)

            scrollNo = 0
            try:
                # 选择默认打开的页面
                self.search_page = self.browser.new_page()
                # 添加初始化js脚本代码，隐藏webdriver属性，防止检测出来
                js = "Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});"
                self.search_page.add_init_script(js)
                # 给playwright添加响应事件的侦听处理函数
                # self.search_page.on('response', self.handler_response)
                """爬虫执行的主要逻辑"""
                try:
                    self.search_page.goto(url, wait_until="domcontentloaded")
                except:
                    self.search_page.goto(url, wait_until="domcontentloaded")

                self.search_page.wait_for_timeout(120000)
                if self.search_page.is_visible('//div[@class="feeds-container"]'):
                    all_div = self.search_page.locator('//section[@class="note-item"]//a[@class="cover mask ld"]').all()
                    for alick in all_div:
                        # 视频评论页面打开
                        alick.click()
                        # 暂停5秒
                        self.search_page.wait_for_timeout(5000)
                        # 定位可滚动容器 先在容器内聚焦
                        self.search_page.locator('//div[@class="desc"]').hover()
                        # 视频链接打开的状态，此时暂停
                        while self.search_page.is_visible('//div[@class="note-detail-mask"]'):
                            self.search_page.wait_for_timeout(2000)
                            print('评论内容滚动条向下滚动1000个像素。。。。')
                            # 直接在容器内触发滚动
                            self.search_page.mouse.wheel(0, 1000)
                            # 滚动条滚动到底部时，获取所有评论数据
                            if self.search_page.is_visible('//div[@class="end-container"]'):
                                self.search_page.wait_for_timeout(2000)
                                comments_all = self.search_page.locator(
                                    '//div[@class="parent-comment"]//div[@class="comment-item"]').all()
                                for coment in comments_all:
                                    # 用户信息获取，
                                    coment.locator(
                                        '//div[@class="comment-inner-container"]//div[@class="avatar"]/a').click()
                                    self.search_page.wait_for_timeout(2000)
                                    # 定位到刚打开的用户信息页面
                                    self.userPage = [page for page in self.browser.pages if
                                                     page.url.find('user/profile') != -1]
                                    # 用户信息数据和评论数据编辑
                                    if self.userPage != None and len(self.userPage) > 0:
                                        self.userPageData = self.userPage[0]
                                        rowData = {}
                                        # 评论标题
                                        rowData["评论标题"] = self.getText(
                                            self.search_page.locator('//div[@id="detail-title"]'))
                                        # 评论时间
                                        rowData["评论时间"] = self.getText(coment.locator(
                                            '//div[@class="comment-inner-container"]//div[@class="right"]//div[@class="info"]//div[@class="date"]//span[1]'))
                                        # 评论内容id
                                        rowData["评论内容id"] = coment.get_attribute('id').replace('comment-', '')
                                        # 评论内容
                                        rowData["评论内容"] = self.getText(
                                            coment.locator(
                                                '//div[@class="comment-inner-container"]//div[@class="right"]//div[@class="content"]//span//span'))
                                        # 评论人取得
                                        rowData["评论人"] = self.getText(
                                            self.userPageData.locator('//div[@class="user-name"]'))
                                        # 小红书号取得
                                        rowData["小红书号"] = self.getText(
                                            self.userPageData.locator('//span[@class="user-redId"]'))
                                        # IP属地取得
                                        rowData["IP属地"] = self.getText(
                                            self.userPageData.locator('//span[@class="user-IP"]'))

                                        self.result_data.append(rowData)

                                        print(f'采集结果：{rowData}')
                                        self.userPageData.wait_for_timeout(1000)
                                        # 关闭页面
                                        self.userPageData.close()

                # 关闭页面
                self.search_page.close()
            except Exception as e:
                print(f"滚动滚动条第{scrollNo}次滚动结束，数据处理中。。。。。。连接失败： {e}")

        # 出力execl文件
        self.save_json()
        # MongoDB中保存
        self.save_mongodb()


if __name__ == '__main__':
    client = XhsPlaywrightUser()
    client.exec()