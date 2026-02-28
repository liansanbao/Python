import datetime
import json
import os
import time
import execjs
from ..items import *
from scrapy.utils.project import get_project_settings

'''
    要求：
        1.采集每个评论的 评论人、评论时间、评论内容、小红书号、IP属地（小红书号在用户的主页里面）
        2.采集的数据，存放mongodb，导出为json文件进行交付
'''
class XhsCrawlSpider(scrapy.Spider):
    name = "xhs_crawl"
    allowed_domains = ["xiaohongshu.com"]
    # start_urls = ["https://xiaohongshu.com"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 用户信息存储, 减少访问服务器的负担
        self.userInfoDect = self.load_existing_json() # 加载已有的用户信息
        # self.logger.info(f'self.userInfoDect: {self.userInfoDect.keys()}')
        self.settings = get_project_settings()

    # 读取已有的用户信息
    def load_existing_json(self):
        # 读取userinfo.json文件中所有信息
        result = {}
        try:
            with open(f'{self.name}.json', 'r', encoding='utf-8') as r:
                for line in r:
                    line = line.strip()
                    if line: # 跳过空行
                        data = json.loads(line)
                        result.update(data)
        except (FileNotFoundError, json.JSONDecodeError):
            return dict()
        return result

    def start_requests(self):
        url = 'https://www.xiaohongshu.com/explore'
        #     'https://www.xiaohongshu.com/search_result?keyword=%25E8%258B%25B1%25E8%25AF%25AD%25E5%25AD%25A6%25E4%25B9%25A0%25E6%259C%25BA&source=web_explore_feed'

        # SearchId作成
        searchId = self.getSearchId()
        self.has_more = True

        for pageNo in range(1, self.settings.get('XHS_PAGE')):
            # {"keyword":"英语学习机","page":1,"page_size":20,"search_id":"2erp1px9bjtip2pcrwvx5","sort":"general","note_type":0,"ext_flags":[],"geo":"","image_formats":["jpg","webp","avif"]}
            data_str = json.dumps({
                "keyword": "英语学习机",
                "page": pageNo,
                "page_size": 20,
                "search_id": searchId,
                "sort": "general",
                "note_type": 0,
                "ext_flags": [],
                "geo": "",
                "image_formats": ["jpg", "webp", "avif"]
            })

            # cookie值
            cookie_str = self.settings.get('COOKIE_STR')
            # 转为字典
            self.cookie = dict(
                pair.split('=', 1)  # 拆分键值
                for pair in map(str.strip, cookie_str.split(';'))  # 分割并去空格
            )

            # loadts值需要从新生成
            self.cookie['loadts'] = str(self.timestamp_13())

            # 当请求的数据没有了，指定的页数还没有爬取完的场合，直接退出循环
            if self.has_more:
                yield scrapy.Request(url, method='POST', callback=self.parse, body=data_str, headers={'Content-Type': 'application/json'}, cookies=self.cookie)
            else:
                break


    ''' 评论数据采集 '''
    def parse(self, response):
        json_data = response.json()

        # 当请求的数据没有时，退出 {'msg': '成功', 'data': {'has_more': False}, 'code': 0, 'success': True}
        #                     {'code': -101, 'success': False, 'msg': '无登录信息，或登录信息为空', 'data': {}}
        has_more = json_data.get('data', {}).get('has_more', False)
        self.logger.info(f'has_more: {has_more}')
        if (not has_more):
            self.has_more = False
            return

        time.sleep(2)
        # 评论数据处理
        for note in json_data['data']['items']:
            # 评论id
            note_id = note['id']
            # 评论xsec_token
            note_xsec_token = note['xsec_token']
            # model_type为note时，进行数据采集
            if note['model_type'] == 'note':
                # 评论标题的作者
                note_title = note.get("note_card", {}).get("user", {}).get('nick_name')
                # 评论标题
                title = note.get("note_card", {}).get("display_title", "无评论标题")
                note_title = title if title != '' else note_title
                # 评论内容URL
                url = f'https://edith.xiaohongshu.com/api/sns/web/v2/comment/page?note_id={note_id}&cursor=&top_comment_id=&image_formats=jpg,webp,avif&xsec_token={note_xsec_token}'
                # 采集: 评论人、评论时间、评论内容、小红书号、IP属地（小红书号在用户的主页里面）
                # self.logger.info(f'评论人、评论时间、评论内容、小红书号、IP属地（小红书号在用户的主页里面） : {url}')
                item = [note_title, note_id, note_xsec_token]
                time.sleep(3)
                yield scrapy.Request(url, callback=self.exec_comment, meta={'p_item': item}, cookies=self.cookie)

    ''' 评论人、评论时间、评论内容、小红书号、IP属地（小红书号在用户的主页里面）数据采集 '''
    def exec_comment(self, response):
        json_data = response.json()
        # 评论数据
        comments_list = json_data['data']['comments']
        if not comments_list or len(comments_list[0]) == 0:
            return
        p_item = response.meta.get('p_item')
        time.sleep(2)
        # 评论数据处理
        for comment in comments_list:
            # 评论时间
            create_time = self.timestampToDate(comment['create_time'])
            # 评论内容
            content = comment['content']
            # 评论内容id
            content_id = comment['id']
            # 用户xsec_token
            xsec_token = comment['user_info']['xsec_token']
            # 用户user_id
            user_id = comment['user_info']['user_id']
            # 用户名称
            nickname = comment['user_info']['nickname']
            # 用户注销的情况，
            if nickname == '用户已注销':
                rowData = XiaohongshuItem()
                # 评论标题
                rowData["display_title"] = p_item[0]
                # 评论时间
                rowData["create_time"] = create_time
                # 评论内容id
                rowData["display_contentId"] = comment['id']
                # 评论内容
                rowData["display_content"] = comment['content']
                # 评论人取得
                rowData["userName"] = nickname
                # 小红书号取得
                rowData["redId"] = ''
                # IP属地取得
                rowData["userIp"] = ''
                # 用户Id取得
                rowData["userId"] = 'JSON'
                yield rowData
            # 用户信息在JSON文件中，以JSON文件中用户信息保存
            elif (self.userInfoDect and user_id in self.userInfoDect.keys()):
                userInfo = self.userInfoDect[user_id]
                self.logger.info(f'来自Json文件：{userInfo}')
                rowData = XiaohongshuItem()
                # 评论标题
                rowData["display_title"] = p_item[0]
                # 评论时间
                rowData["create_time"] = create_time
                # 评论内容id
                rowData["display_contentId"] = comment['id']
                # 评论内容
                rowData["display_content"] = comment['content']
                # 评论人取得
                rowData["userName"] = userInfo[0]
                # 小红书号取得
                rowData["redId"] = userInfo[1]
                # IP属地取得
                rowData["userIp"] = userInfo[2]
                # 用户Id取得
                rowData["userId"] = 'JSON'
                yield rowData
            else:
                time.sleep(2)
                url = f'https://www.xiaohongshu.com/user/profile/{user_id}?xsec_token={xsec_token}&xsec_source=pc_comment'
                # 评论时间、评论内容、评论内容id、用户Id
                item = [create_time, content, content_id, user_id, p_item[0]]
                # 评论人、小红书号、IP属地（小红书号在用户的主页里面）数据采集
                yield scrapy.Request(url, callback=self.exec_userinfo, meta={'content_item': item}, cookies=self.cookie)

        # 下一页评论数据采集
        if json_data['data']['has_more']:
            # cursor
            cursor = json_data['data']['cursor']
            url = f'https://edith.xiaohongshu.com/api/sns/web/v2/comment/page?note_id={p_item[1]}&cursor={cursor}&top_comment_id=&image_formats=jpg,webp,avif&xsec_token={p_item[2]}'
            time.sleep(3)
            # 采集: 评论人、评论时间、评论内容、小红书号、IP属地（小红书号在用户的主页里面）
            yield scrapy.Request(url, callback=self.exec_comment, meta={'p_item': p_item}, cookies=self.cookie)

    ''' 评论人、小红书号、IP属地（小红书号在用户的主页里面）数据采集 '''
    def exec_userinfo(self, response):
        time.sleep(3)
        content_item = response.meta.get('content_item')
        rowData = XiaohongshuItem()
        # 评论标题
        rowData["display_title"] = content_item[4]
        # 评论时间
        rowData["create_time"] = content_item[0]
        # 评论内容id
        rowData["display_contentId"] = content_item[2]
        # 评论内容
        rowData["display_content"] = content_item[1]
        # 评论人取得
        rowData["userName"] = self.getText(response.xpath('//div[@class="user-name"]/text()'))
        # 小红书号取得
        rowData["redId"] = self.getText(response.xpath('//span[@class="user-redId"]/text()'))
        # IP属地取得
        rowData["userIp"] = self.getText(response.xpath('//span[@class="user-IP"]/text()'))
        # 用户Id取得
        rowData["userId"] = content_item[3]
        self.userInfoDect[str(content_item[3])] = [rowData["userName"], rowData["redId"], rowData["userIp"]]
        self.logger.info(f'来自浏览器：{self.userInfoDect[str(content_item[3])]}')
        yield rowData

    ''' text值取得 （替换：小红书号：/IP属地：） '''
    def getText(self, li):
        try:
            if li != None:
                return li.get().replace('小红书号：', '').replace('IP属地：', '')
        except:
            pass
        return ''

    ''' 生成 13 位毫秒级时间戳 '''
    def timestamp_13(self):
        return int(datetime.datetime.timestamp(datetime.datetime.today()) * 1000)

    ''' SearchId作成 '''
    def getSearchId(self):
        # 1.使用文件的读写拿到js文件里面的代码
        with open(os.path.abspath('xhs.js'), 'r', encoding='utf-8') as r:
            js_data = r.read()

        # 2.拿到js代码时候，需要进行一个类似编码的操作
        js_obj = execjs.compile(js_data)

        # 3.执行js代码
        result = js_obj.call('createSearchId')

        return result

    ''' 输入时间戳字符串转换成日期 '''
    def timestampToDate(self, timestamp):
        # 转换为整型并处理单位
        timestamp_ms = int(timestamp)
        timestamp_sec = timestamp_ms // 1000  # 毫秒转秒

        # 生成本地时间
        dt_local = datetime.datetime.fromtimestamp(timestamp_sec)

        # 格式化输出
        # print(f"本地时间: {dt_local.strftime('%Y-%m-%d')}")
        return dt_local.strftime('%Y-%m-%d')