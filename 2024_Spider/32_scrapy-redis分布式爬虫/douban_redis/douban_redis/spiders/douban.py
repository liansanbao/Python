import time

from scrapy import signals
from ..items import *
from scrapy_redis.spiders import RedisSpider

# class DoubanSpider(scrapy.Spider):
class DoubanSpider(RedisSpider):# 自动继承Spider类
    name = "douban"
    allowed_domains = ["movie.douban.com"]
    # start_urls = ["https://movie.douban.com/top250"]
    pageCount = 2
    redis_key = 'sanbao'

    def parse(self, response):
        # 电影名称 xpath定位
        movie_names = response.xpath('//a/span[@class="title"][1]/text()').getall()

        # 电影评分 xpath定位
        score_list = response.xpath('//span[@class="rating_num"]/text()').getall()

        self.logger.info(f'电影名称：{movie_names}')
        self.logger.info(f'电影评分：{score_list}')
        pageNo = response.meta.get('pageNo')
        if pageNo == None:
            pageNo = 1
        self.logger.info(f'第{pageNo}页爬取成功！数据处理中。。。。。')

        # 保存
        # 1.把items里面的东西导入过来
        for title in enumerate(movie_names):
            # 保存数据需要依靠items里面的模版
            move_item = DoubanRedisItem()  # 字典对象 > 键值对 A:B
            move_item['name'] = title[1]  # 构造键值对，保存到itmes对象里面
            # 数据已经保存items，准备进入管道保存，此时name：''
            for score in enumerate(score_list):
                # 需要一一匹配，判断，如果索引相同，保存数据
                if score[0] == title[0]:
                    move_item['score'] = score[1]
            yield move_item

        next_url = response.xpath('//span[@class="next"]//a[text()="后页>"]/@href').get()
        if pageNo < self.pageCount:
            if next_url != None:
                time.sleep(4)
                pageNo += 1
                self.logger.info(f'第{pageNo}页URL：{next_url}')
                yield response.follow(next_url, callback=self.parse, meta={'pageNo': pageNo})
