# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MaoyanItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 影片名称
    movieName = scrapy.Field()
    # 综合票房
    num = scrapy.Field()
    # 票房占比
    boxRate = scrapy.Field()
    # 排片场次
    showCount = scrapy.Field()
    pass
