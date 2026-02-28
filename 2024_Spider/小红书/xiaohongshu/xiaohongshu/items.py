# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class XiaohongshuItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 评论标题
    display_title = scrapy.Field()
    # 评论时间
    create_time = scrapy.Field()
    # 评论内容
    display_content = scrapy.Field()
    # 评论内容id
    display_contentId = scrapy.Field()
    # 评论人
    userName = scrapy.Field()
    # 小红书号
    redId = scrapy.Field()
    # IP属地
    userIp = scrapy.Field()
    # 用户Id属地
    userId = scrapy.Field()
    pass
