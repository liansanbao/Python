# _*_ coding: utf-8 _*_
# @Time : 2025/4/18 13:04
# @Author : 韦丽
# @Version: V 1.0
# @File : BookDangdang.py
# @desc :
import chardet
from lxml import etree

import requests
from fake_useragent import FakeUserAgent

# get请求发送
def get(url):
    header = {
        'User-Agent': FakeUserAgent().random,
        'Cookie':'dest_area=country_id%3D9000%26province_id%3D111%26city_id%20%3D0%26district_id%3D0%26town_id%3D0; __permanent_id=20250418122459792339906638033927568; __visit_id=20250418122459793257082539024332689; __out_refer=; ddscreen=2; pos_6_start=1744950383371; pos_6_end=1744950383683; __rpm=...1744951006285%7C...1744951011961; __trace_id=20250418123652367384172593971846884'
    }
    return requests.get(url=url, headers=header)

# 爬取数据
def exec():
    url = 'http://bang.dangdang.com/books/bestsellers/01.00.00.00.00.00-recent7-0-0-1-1'
    response = get(url)
    # 有文字乱码问题，需要再次指定编码（例："岸��一郎"）
    response.encoding = "gbk"
    # 数据
    str_data = response.text
    # html数据
    html_data = etree.HTML(str_data)

    nextpage = getText(html_data.xpath('//ul[@class="paging"]//li[@class="next"]/a/@href'))
    print(response.url.split('-')[-1])
    # 定位包含所有的数据
    lis = html_data.xpath(' //ul[@class="bang_list clearfix bang_list_mode"]//li')
    for li in lis:
        # 标题 xpath定位
        title = getText(li.xpath('.//div[@class="name"]/a/@title'))
        # 评论数
        commentsNum = getText(li.xpath('.//div[@class="star"]/a/text()'))
        # 推荐度
        reco = getText(li.xpath('.//div[@class="star"]/span/text()'))
        # 作者
        author = getText(li.xpath('.//div[@class="publisher_info"][1]/a/@title'))
        # 出版社
        publishingHouse = getText(li.xpath('.//div[@class="publisher_info"][2]/a/text()'))
        # 出版时间
        publishingTime = getText(li.xpath('.//div[@class="publisher_info"][2]/span/text()'))
        # 售价
        price = getText(li.xpath('.//div[@class="price"]/p[1]/span[1]/text()'))
        # 原价
        original = getText(li.xpath('.//div[@class="price"]/p[1]/span[2]/text()'))
        # 电子书价格
        ebookPrice = getText(li.xpath('.//div[@class="price"]/p[2]/span[1]/text()'))
        # 详情链接
        detailsPage = getText(li.xpath('.//div[@class="name"]/a/@href'))
        print(title, commentsNum, reco, author, publishingHouse, publishingTime, price, original, ebookPrice, detailsPage)

# text值取得
def getText(li):
    text_list = li
    if text_list != None and len(text_list) != 0:
        return text_list[0]
    return ''


if __name__ == '__main__':
    exec()