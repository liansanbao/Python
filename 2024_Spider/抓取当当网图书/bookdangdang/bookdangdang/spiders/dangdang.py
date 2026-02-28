# _*_ coding: utf-8 _*_
# @Time : 2025/4/18 12:41
# @Author : 韦丽
# @Version: V 1.0
# @File : dangdang.py
# @desc : 抓取当当网图书畅销榜全部数据 网站（http://bang.dangdang.com/books/bestsellers/01.00.00.00.00.00-recent7-0-0-1-1）

import scrapy
from lxml import etree
from ..items import *
import time


class DangdangSpider(scrapy.Spider):
    name = "dangdang"
    allowed_domains = ["dangdang.com"]
    start_urls = ["http://bang.dangdang.com/books/bestsellers/01.00.00.00.00.00-recent7-0-0-1-1"]
    next_page_base_url = 'http://bang.dangdang.com/books/bestsellers/01.00.00.00.00.00-recent7-0-0-1-'

    '''
        要求：
            1.爬取到的数据应该包含标题、评论数、推荐度、作者、出版社、出版时间、售价、原价、电子书价格，和详情页
            2.数据存储在Excel表格中
            3.框架不限
    '''
    def parse(self, response):
        # 数据
        str_data = response.text
        # html数据
        html_data = etree.HTML(str_data)
        # 定位包含所有的数据
        lis = html_data.xpath(' //ul[@class="bang_list clearfix bang_list_mode"]//li')
        for li in lis:
            item = BookdangdangItem()
            # 标题
            item['title'] = self.getText(li.xpath('.//div[@class="name"]/a/@title'))
            # 评论数
            item['commentsNum'] = self.getText(li.xpath('.//div[@class="star"]/a/text()'))
            # 推荐度
            item['reco'] = self.getText(li.xpath('.//div[@class="star"]/span/text()'))
            # 作者
            item['author'] = self.getText(li.xpath('.//div[@class="publisher_info"][1]/a/@title'))
            # 出版社
            item['publishingHouse'] = self.getText(li.xpath('.//div[@class="publisher_info"][2]/a/text()'))
            # 出版时间
            item['publishingTime'] = self.getText(li.xpath('.//div[@class="publisher_info"][2]/span/text()'))
            # 售价
            item['price'] = self.getText(li.xpath('.//div[@class="price"]/p[1]/span[1]/text()'))
            # 原价
            item['original'] = self.getText(li.xpath('.//div[@class="price"]/p[1]/span[2]/text()'))
            # 电子书价格
            item['ebookPrice'] = self.getText(li.xpath('.//div[@class="price"]/p[2]/span[1]/text()'))
            # 详情链接
            item['detailsPage'] = self.getText(li.xpath('.//div[@class="name"]/a/@href'))
            yield item

        # 下一页URL取得
        nextpage = self.getText(html_data.xpath('//ul[@class="paging"]//li[@class="next"]/a/@href'))
        if nextpage != "javascript:loadData('0');":
            pageNo = int(response.url.split('-')[-1]) + 1
            new_url = f'{self.next_page_base_url}' + str(pageNo)
            time.sleep(4)
            self.logger.info(f'第{pageNo}页URL：{new_url}')
            yield response.follow(new_url, callback=self.parse)

    # text值取得
    def getText(self, li):
        text_list = li
        if text_list != None and len(text_list) != 0:
            return text_list[0]
        return ''