# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanRedisItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 电影名称
    name = scrapy.Field()
    # 电影评分
    score = scrapy.Field()
    # 导演
    director = scrapy.Field()
    # 海报图片
    image_urls = scrapy.Field()
    # 海报图片名称
    image_name = scrapy.Field()
    pass
