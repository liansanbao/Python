# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookdangdangItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 标题
    title = scrapy.Field()
    # 评论数
    commentsNum = scrapy.Field()
    # 推荐度
    reco = scrapy.Field()
    # 作者
    author = scrapy.Field()
    # 出版社
    publishingHouse = scrapy.Field()
    # 出版时间
    publishingTime = scrapy.Field()
    # 售价
    price = scrapy.Field()
    # 原价
    original = scrapy.Field()
    # 电子书价格
    ebookPrice = scrapy.Field()
    # 详情链接
    detailsPage = scrapy.Field()
    pass
