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
from playwright.sync_api import sync_playwright
from pymongo import MongoClient

'''
    要求：
        1.采集每个评论的 评论人、评论时间、评论内容、小红书号、IP属地（小红书号在用户的主页里面）
        2.采集的数据，存放mongodb，导出为json文件进行交付
'''
class XhsPlaywright:
    # 输入时间戳字符串转换成日期
    def timestampToDate(self, timestamp):
        # 转换为整型并处理单位
        timestamp_ms = int(timestamp)
        timestamp_sec = timestamp_ms // 1000  # 毫秒转秒

        # 生成本地时间
        dt_local = datetime.datetime.fromtimestamp(timestamp_sec)

        # 格式化输出
        # print(f"本地时间: {dt_local.strftime('%Y-%m-%d')}")
        return dt_local.strftime('%Y-%m-%d')

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
            for item in self.result_date:
                # 把字典数据转json
                json_data = json.dumps(item, ensure_ascii=False) + ', \n'
                w.write(json_data)

    # MongoDB中保存
    def save_mongodb(self):
        with MongoClient(host='192.168.1.15', port=27017) as con:  # 实例化mongoclient
            collection = con['xiaohongshuSpider']['xhs_crawl']
            for py_dict in self.result_date:
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
        self.result_date = []
        """爬虫程序的入口函数"""
        with sync_playwright() as p:
            # 连接本地启动的浏览器
            self.browser = p.chromium.launch_persistent_context(
                executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                user_data_dir=r'D:\chrome_userData',
                headless=False)
            scrollNo = 0
            try:
                # 选择默认打开的页面
                self.search_page = self.browser.new_page()
                # 添加初始化js脚本代码，隐藏webdriver属性，防止检测出来
                js = "Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});"
                self.search_page.add_init_script(js)
                # 给playwright添加响应事件的侦听处理函数
                self.search_page.on('response', self.handler_response)
                """爬虫执行的主要逻辑"""
                try:
                    self.search_page.goto(url, wait_until="domcontentloaded")
                except:
                    self.search_page.goto(url, wait_until="domcontentloaded")

                # 滚动滚动条
                for index in range(1, 200):
                    scrollNo += 1
                    self.search_page.wait_for_timeout(80000)
                    commentsUrls = {x.url for x in self.browser.pages if (x.url.find('comment/page') != -1 or x.url.find('user/profile') != -1)}
                    # 评论内容和评论人信息的URL存在的场合，继续暂停50秒，一直到当前评论的数据处理完
                    while len(commentsUrls) > 0:
                        print(f"滚动滚动条第{scrollNo}次滚动结束，数据处理中。。。。。。")
                        self.search_page.wait_for_timeout(50000)
                        commentsUrls = {x.url for x in self.browser.pages if
                                        (x.url.find('comment/page') != -1 or x.url.find('user/profile') != -1)}

                    # 一次向下滚动840个像素
                    self.search_page.evaluate(f'document.documentElement.scrollTop={100 * index}')


                # 关闭页面
                self.search_page.close()
            except Exception as e:
                print(f"滚动滚动条第{scrollNo}次滚动结束，数据处理中。。。。。。连接失败： {e}")

        # 出力execl文件
        self.save_json()
        # MongoDB中保存
        self.save_mongodb()

    # 检索主页关键字数据处理
    def handler_response(self, response):
        request_url = response.url
        # https://edith.xiaohongshu.com/api/sns/web/v1/search/notes
        if response.headers.get('content-type') == 'application/json; charset=utf-8' and request_url.find('search/notes') != -1:
            # 获取关联的请求对象
            request = response.request
            if request.method == "POST":
                # 获取原始POST数据
                raw_post_data = request.post_data
                # 自动解析JSON格式参数
                if raw_post_data and "application/json" in request.headers.get("content-type", ""):
                    json_params = request.post_data_json
                    # 页数获取
                    self.page = jsonpath.jsonpath(json_params, '$..page')[0]
                    print(f"滚动滚动条时,第{self.page}页处理，请求参数：{json_params} ")

            # 获取滚动条滚动时的异步请求响应数据
            str_data = response.body()
            # 转Json数据
            json_data = json.loads(str_data)

            # 当请求的数据没有时，退出循环 {'msg': '成功', 'data': {'has_more': False}, 'code': 0, 'success': True}
            has_more = jsonpath.jsonpath(json_data, '$.data.has_more')
            if has_more != None and len(has_more) > 0:
                if (not bool(has_more[0])):
                    print('数据没有了！')
                    return

            # 评论id （排除model_type==“hot_query”）
            id_list = jsonpath.jsonpath(json_data, '$.data.items[?(@.model_type == "note")]..id')

            # 获取note_card节点下的xsec_token，作为排除条件
            note_card_xsec_token_list = set(
                jsonpath.jsonpath(json_data, '$.data.items[?(@.model_type == "note")]..note_card..xsec_token'))
            # 获取所有的xsec_token值，当然也包括note_card节点下的xsec_token
            items_xsec_token_list = jsonpath.jsonpath(json_data, '$.data.items[?(@.model_type == "note")]..xsec_token')
            # 评论xsec_token
            xsec_token_list = [x for x in items_xsec_token_list if x not in note_card_xsec_token_list]

            # 评论标题 （model_type==“note”）
            display_title_list = jsonpath.jsonpath(json_data,
                                                   '$.data.items[?(@.model_type == "note")]..note_card.display_title')

            title_result = zip(display_title_list, id_list, xsec_token_list)

            for item in title_result:
                print(f'评论内容第一页数据处理：')
                # 采集: 评论人、评论时间、评论内容、小红书号、IP属地（小红书号在用户的主页里面）
                self.exec_comment('', item)
                commentsUrls = {x.url for x in self.browser.pages if
                                (x.url.find('user/profile') != -1)}
                self.comment_page.wait_for_timeout(50000)
                # 评论内容和评论人信息的URL存在的场合，继续暂停50秒，一直到当前评论的数据处理完
                while len(commentsUrls) > 0:
                    self.comment_page.wait_for_timeout(50000)
                    commentsUrls = {x.url for x in self.browser.pages if
                                    (x.url.find('user/profile') != -1)}
                # 关闭评论数据页面
                self.comment_page.close()

    # 评论人、评论时间、评论内容、小红书号、IP属地（小红书号在用户的主页里面）数据采集
    def exec_comment(self, p_cursor, p_item: list = []):
        url = f'https://edith.xiaohongshu.com/api/sns/web/v2/comment/page?note_id={p_item[1]}&cursor={p_cursor}&top_comment_id=&image_formats=jpg,webp,avif&xsec_token={p_item[2]}'
        try:
            # 选择默认打开的页面
            self.comment_page = self.browser.new_page()
            # 添加初始化js脚本代码，隐藏webdriver属性，防止检测出来
            js = "Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});"
            self.comment_page.add_init_script(js)
            # 给playwright添加响应事件的侦听处理函数
            bound_handler = partial(self.comment_handler_response, c_itme=p_item)
            self.comment_page.on('response', bound_handler)
            """爬虫执行的主要逻辑"""
            try:
                self.comment_page.goto(url, wait_until="domcontentloaded")
            except:
                self.comment_page.goto(url, wait_until="domcontentloaded")
        except Exception as e:
            print(f'评论内容第一页数据获取失败： {e}')

    # 评论人、评论时间、评论内容、小红书号、IP属地（小红书号在用户的主页里面）数据采集
    def exec_comment_next(self, p_cursor, p_item: list = []):
        url = f'https://edith.xiaohongshu.com/api/sns/web/v2/comment/page?note_id={p_item[1]}&cursor={p_cursor}&top_comment_id=&image_formats=jpg,webp,avif&xsec_token={p_item[2]}'
        try:
            # 选择默认打开的页面
            self.comment_next_page = self.browser.new_page()
            # 添加初始化js脚本代码，隐藏webdriver属性，防止检测出来
            js = "Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});"
            self.comment_next_page.add_init_script(js)
            # 给playwright添加响应事件的侦听处理函数
            bound_handler = partial(self.comment_handler_response, c_itme=p_item)
            self.comment_next_page.on('response', bound_handler)
            """爬虫执行的主要逻辑"""
            try:
                self.comment_next_page.goto(url, wait_until="domcontentloaded")
            except:
                self.comment_next_page.goto(url, wait_until="domcontentloaded")

            self.comment_next_page.wait_for_timeout(60000)

            # 关闭评论数据页面
            self.comment_next_page.close()
        except Exception as e:
            print(f'评论内容下一页数据获取失败： {e}')

    # 评论人、评论时间、评论内容、小红书号、IP属地（小红书号在用户的主页里面）数据采集
    def comment_handler_response(self, response, c_itme):
        request_url = response.url
        # https://edith.xiaohongshu.com/api/sns/web/v2/comment/page?note_id=66a0d520000000000a006b3f&cursor=&top_comment_id=&image_formats=jpg,webp,avif&xsec_token=ABWX9BtkSBICFGODD7t0CjF5B6WimxFXRJUvOX6ig7N1A%3D
        if response.headers.get('content-type') == 'application/json; charset=utf-8' and request_url.find(
                'comment/page') != -1:
            json_data = response.json()

            # 评论数据
            comments_list = jsonpath.jsonpath(json_data, '$.data.comments')
            print(f'comments_list : {comments_list}')
            if not comments_list or len(comments_list[0]) == 0:
                return

            # 评论标题
            self.display_title = c_itme[0]
            # 评论时间
            create_time_list = jsonpath.jsonpath(json_data, '$.data.comments..create_time')
            # 评论内容
            content_list = jsonpath.jsonpath(json_data, '$.data.comments..content')
            # 评论内容id 去重
            content_id_list = list(set(jsonpath.jsonpath(json_data, '$.data.comments..id')))
            # xsec_token
            xsec_token_list = jsonpath.jsonpath(json_data, '$.data.comments..user_info.xsec_token')
            # user_id
            user_id_list = jsonpath.jsonpath(json_data, '$.data.comments..user_info.user_id')

            content_result = zip(create_time_list, content_list, xsec_token_list, user_id_list, content_id_list)

            for item in content_result:
                self.exec_userinfo(item)
                # 关闭用户页面
                self.user_page.close()

            # 下一页评论数据采集
            has_more = jsonpath.jsonpath(json_data, '$.data.has_more')
            if has_more != None and len(has_more) > 0:
                if (bool(has_more[0])):
                    # cursor
                    cursor = jsonpath.jsonpath(json_data, '$.data.cursor')[0]
                    print(f'评论内容数据处理：{cursor}')
                    self.exec_comment_next(cursor, c_itme)


    # 评论人、小红书号、IP属地（小红书号在用户的主页里面）数据采集
    def exec_userinfo(self, item: list = []):
        # https://www.xiaohongshu.com/user/profile/56cad3f41c07df7ede8374e1?xsec_token=ABmwNjrClqGjd1Xc3XJoVyejjxuasza77vL5D-ehGTtFc=&xsec_source=pc_comment
        url = f'https://www.xiaohongshu.com/user/profile/{item[3]}?xsec_token={item[2]}&xsec_source=pc_comment'
        """爬虫程序的入口函数"""

        try:
            # 选择默认打开的页面
            self.user_page = self.browser.new_page()
            # 添加初始化js脚本代码，隐藏webdriver属性，防止检测出来
            js = "Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});"
            self.user_page.add_init_script(js)
            """爬虫执行的主要逻辑"""
            try:
                self.user_page.goto(url, wait_until="domcontentloaded")
            except:
                self.user_page.goto(url, wait_until="domcontentloaded")

            rowData = {}
            # 评论标题
            rowData["评论标题"] = self.display_title
            # 评论时间
            rowData["评论时间"] = self.timestampToDate(item[0])
            # 评论内容id
            rowData["评论内容id"] = item[4]
            # 评论内容
            rowData["评论内容"] = item[1]
            # 评论人取得
            rowData["评论人"] = self.getText(self.user_page.locator('//div[@class="user-name"]'))
            # 小红书号取得
            rowData["小红书号"] = self.getText(self.user_page.locator('//span[@class="user-redId"]'))
            # IP属地取得
            rowData["IP属地"] = self.getText(self.user_page.locator('//span[@class="user-IP"]'))

            print(f'采集结果：{rowData}')

            self.result_date.append(rowData)

            self.user_page.wait_for_timeout(2000)
        except Exception as e:
            print(f'用户数据获取失败： {e}')

if __name__ == '__main__':
    client = XhsPlaywright()
    client.exec()