# _*_ coding: utf-8 _*_
# @Time : 2025/5/7 16:32
# @Author : 韦丽
# @Version: V 1.0
# @File : xhs_crawl.py
# @desc : 需要采集每个评论的 评论人、评论时间、评论内容、小红书号、IP属地（小红书号在用户的主页里面）
#         https://www.xiaohongshu.com/search_result?keyword=%25E8%258B%25B1%25E8%25AF%25AD%25E5%25AD%25A6%25E4%25B9%25A0%25E6%259C%25BA&source=web_search_result_notes&type=51
import datetime
import json
import os
import time

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
class XhsCrawl:
    def __init__(self, pageNo = 2, cookie=""):
        # 定义实例变量number_,表示翻页的页数
        self.pageNo = pageNo
        self.cookie = cookie

    # SearchId作成
    def getSearchId(self):
        # 1.使用文件的读写拿到js文件里面的代码
        with open(os.path.abspath('xiaohongshu/xhs.js'), 'r', encoding='utf-8') as r:
            js_data = r.read()

        # 2.拿到js代码时候，需要进行一个类似编码的操作
        js_obj = execjs.compile(js_data)

        # 3.执行js代码
        result = js_obj.call('createSearchId')

        return result

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

    # 请求处理
    def request(self, url, methond, data={}):
        ua = FakeUserAgent().random
        print(f'访问的URL： {url}')
        header = {
            'User-Agent': ua,
            'Cookie': self.cookie
        }
        if methond == 'get':
            return requests.get(url=url, headers=header)
        elif methond == 'post':
            return requests.post(url=url, headers=header, data=data)

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
        url = 'https://edith.xiaohongshu.com/api/sns/web/v1/search/notes'

        # SearchId作成
        searchId = self.getSearchId()

        # 采集数据
        self.result_date = []

        for pageNo in range(1, self.pageNo):
            # {"keyword":"英语学习机","page":1,"page_size":20,"search_id":"2erp1px9bjtip2pcrwvx5","sort":"general","note_type":0,"ext_flags":[],"geo":"","image_formats":["jpg","webp","avif"]}
            data = {
                "keyword":"英语学习机",
                "page":pageNo,
                "page_size":20,
                "search_id":searchId,
                "sort":"general",
                "note_type":0,
                "ext_flags":[],
                "geo":"",
                "image_formats":["jpg","webp","avif"]
            }

            response = self.request(url, 'post', data)
            json_data = response.json()

            # 当请求的数据没有时，退出循环 {'msg': '成功', 'data': {'has_more': False}, 'code': 0, 'success': True}
            has_more = jsonpath.jsonpath(json_data, '$.data.has_more')
            print(f'POST: {has_more}')
            if (not has_more):
                break
            # if has_more != None and len(has_more) > 0:
            #     if (not bool(has_more[0])):
            #         break

            # 评论id （排除model_type==“hot_query”）
            id_list = jsonpath.jsonpath(json_data, '$.data.items[?(@.model_type == "note")]..id')

            # 获取note_card节点下的xsec_token，作为排除条件
            note_card_xsec_token_list = set(jsonpath.jsonpath(json_data, '$.data.items[?(@.model_type == "note")]..note_card..xsec_token'))
            # 获取所有的xsec_token值，当然也包括note_card节点下的xsec_token
            items_xsec_token_list = jsonpath.jsonpath(json_data, '$.data.items[?(@.model_type == "note")]..xsec_token')
            # 评论xsec_token
            xsec_token_list = [x for x in items_xsec_token_list if x not in note_card_xsec_token_list]

            # 评论标题 （model_type==“note”）
            display_title_list = jsonpath.jsonpath(json_data, '$.data.items[?(@.model_type == "note")]..note_card.display_title')

            title_result = zip(display_title_list, id_list, xsec_token_list)
            for item in title_result:
                # 采集: 评论人、评论时间、评论内容、小红书号、IP属地（小红书号在用户的主页里面）
                self.exec_comment('', item)
                time.sleep(2)
            time.sleep(5)

        print(self.result_date)
        # 出力execl文件
        self.save_json()
        # MongoDB中保存
        self.save_mongodb()

    # 评论人、评论时间、评论内容、小红书号、IP属地（小红书号在用户的主页里面）数据采集
    def exec_comment(self, p_cursor, p_item: list=[]):
        # https://edith.xiaohongshu.com/api/sns/web/v2/comment/page?note_id=67da1b4c000000000e007635&cursor=&top_comment_id=&image_formats=jpg,webp,avif&xsec_token=ABna5ZeiCna9qajmpU7fiTcSAuTtNeu9PbsWXpcWmYdRU%3D
        url = f'https://edith.xiaohongshu.com/api/sns/web/v2/comment/page?note_id={p_item[1]}&cursor={p_cursor}&top_comment_id=&image_formats=jpg,webp,avif&xsec_token={p_item[2]}'
        response = self.request(url, 'get')
        json_data = response.json()

        # 评论数据
        comments_list = jsonpath.jsonpath(json_data, '$.data.comments')
        if not comments_list or len(comments_list[0]) == 0:
            return
        print(f'comments_list : {comments_list}')

        # 评论标题
        self.display_title = p_item[0]
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
            time.sleep(3)

        # 下一页评论数据采集
        has_more = jsonpath.jsonpath(json_data, '$.data.has_more')
        if has_more != None and len(has_more) > 0:
            if (bool(has_more[0])):
                # cursor
                cursor = jsonpath.jsonpath(json_data, '$.data.cursor')[0]
                print(has_more, cursor)
                time.sleep(3)
                self.exec_comment(cursor, p_item)

    # 评论人、小红书号、IP属地（小红书号在用户的主页里面）数据采集
    def exec_userinfo(self, item: list=[]):
        # https://www.xiaohongshu.com/user/profile/56cad3f41c07df7ede8374e1?xsec_token=ABmwNjrClqGjd1Xc3XJoVyejjxuasza77vL5D-ehGTtFc=&xsec_source=pc_comment
        url = f'https://www.xiaohongshu.com/user/profile/{item[3]}?xsec_token={item[2]}&xsec_source=pc_comment'
        """爬虫程序的入口函数"""
        with sync_playwright() as p:
            # 连接本地启动的浏览器 headless=True 无窗口模式
            browser = p.chromium.launch(headless=True,
                                        executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                                        args=['--start-maximized'])
            try:
                # 选择默认的浏览器上下文对象 no_viewport=True设置不要
                context = browser.new_context(no_viewport=True)
                # 选择默认打开的页面
                page = context.new_page()
                # 添加初始化js脚本代码，隐藏webdriver属性，防止检测出来
                js = "Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});"
                page.add_init_script(js)
                """爬虫执行的主要逻辑"""
                try:
                    page.goto(url, wait_until="domcontentloaded")
                except:
                    page.goto(url, wait_until="domcontentloaded")

                time.sleep(2)

                rowData = {}
                # 评论标题
                rowData["评论标题"] = self.display_title
                # 评论时间
                rowData["评论时间"]  = self.timestampToDate(item[0])
                # 评论内容
                rowData["评论内容"]  = item[1]
                # 评论内容id
                rowData["评论内容id"] = item[4]
                # 评论人取得
                rowData["评论人"]  = self.getText(page.locator('//div[@class="user-name"]'))
                # 小红书号取得
                rowData["小红书号"]  = self.getText(page.locator('//span[@class="user-redId"]'))
                # IP属地取得
                rowData["IP属地"]  = self.getText(page.locator('//span[@class="user-IP"]'))

                self.result_date.append(rowData)

                # 关闭页面
                page.close()
            except Exception as e:
                print(f'连接失败： {e}')

    # text值取得 （替换：小红书号：/IP属地：）
    def getText(self, li):
        try:
            if li.count() > 0:
                return li.inner_text().replace('小红书号：', '').replace('IP属地：', '')
        except:
            pass
        return ''

    # 生成 13 位毫秒级时间戳 1746602581638
    def timestamp_13(self):
        return int(datetime.datetime.timestamp(datetime.datetime.today()) * 1000)

if __name__ == '__main__':
    timstamp = int(datetime.datetime.timestamp(datetime.datetime.today()) * 1000)
    #Cookie":'abRequestId=a3c0c64b-a5a5-5bc8-b817-65daf495ea09; webBuild=4.62.3; xsecappid=xhs-pc-web; a1=196a92f9e5fsey3j13dmyfh07qanxht7uujz9hgf750000107451; webId=658e712ce27f02a16fabbbb93a9d768d; gid=yjK0jJiD4J7SyjK0jJijd7xk2iMdvqVyqf6vViWix8WA0u28ICx9Wj888y8W42y8fYK4JiWy; unread={%22ub%22:%2267fdcd71000000001c0335d3%22%2C%22ue%22:%2267f43165000000001e00a4c8%22%2C%22uc%22:29}; web_session=040069b96eae313016ffa0a52f3a4b3570664c; acw_tc=0a0bb41417466024286092732e1cc515554b3d61a6ad8cebef16aa91bd6665; websectiga=82e85efc5500b609ac1166aaf086ff8aa4261153a448ef0be5b17417e4512f28; sec_poison_id=417541e9-af6a-40ff-a1e8-0db9670f5381; loadts=1746602581638',
    #         abRequestId=a3c0c64b-a5a5-5bc8-b817-65daf495ea09; a1=196a92f9e5fsey3j13dmyfh07qanxht7uujz9hgf750000107451; webId=658e712ce27f02a16fabbbb93a9d768d; gid=yjK0jJiD4J7SyjK0jJijd7xk2iMdvqVyqf6vViWix8WA0u28ICx9Wj888y8W42y8fYK4JiWy; acw_tc=0a4ae10f17467476132833955e3cbeb1d7f82fec967887de6166db19620943; webBuild=4.62.3; xsecappid=xhs-pc-web; websectiga=2a3d3ea002e7d92b5c9743590ebd24010cf3710ff3af8029153751e41a6af4a3; sec_poison_id=90195e11-6257-4450-8fd3-40f727cdc12b; web_session=040069b96eae313016ff570f283a4b7bc5d305; unread={%22ub%22:%22681b2c530000000022036c3d%22%2C%22ue%22:%2267f62c6d000000001d026324%22%2C%22uc%22:29}; loadts=1746749264230
    cookie = 'abRequestId=bb197601-041c-57d5-9124-91293741b13c; a1=196b57fcbc8414dgopmg2tgbnsfxqj8rwexz5sw3750000102108; webId=e5be0ab84c1f53c63f12868a10e28b52; gid=yjKD2WifdjEYyjKD2WiSDdMESY4y4fklU6kJCqW9kDIMiu28CAVYF2888y8Jy8Y8KJ4yY880; xsecappid=xhs-pc-web; web_session=040069b96eae313016ffa1ff2b3a4bee204069; acw_tc=0a4ad41017468440729697505e4378dec45a79f69d2d323ad579e56256426b; websectiga=cf46039d1971c7b9a650d87269f31ac8fe3bf71d61ebf9d9a0a87efb424b816c; sec_poison_id=75db3705-784b-41c7-8933-ab622fd9d8ef; webBuild=4.62.3; loadts=1746844328717'
    pageNo = 2
    xhsCrawl = XhsCrawl(pageNo, cookie)
    xhsCrawl.exec()