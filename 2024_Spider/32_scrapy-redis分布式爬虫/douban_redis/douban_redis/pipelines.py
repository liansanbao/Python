# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json

from itemadapter import ItemAdapter
from scrapy_redis.pipelines import RedisPipeline


# 继承RedisPipeline类，重写_process_item方法
class DoubanRedisMyPipeline(RedisPipeline):
    def open_spider(self, spider):
        self.file_ = open(f'{spider.name}.json', 'w', encoding='utf-8')
        spider.logger.info(f'{spider.name}.json 文件已经打开了。')

    def _process_item(self, item, spider):
        key = self.item_key(item, spider)
        data = self.serialize(item)
        self.server.rpush(key, data)
        # 把字典数据转json
        py_dict = dict(item)
        json_data = json.dumps(py_dict, ensure_ascii=False) + ', \n'
        self.file_.write(json_data)
        spider.logger.info(f'DoubanRedisMyPipeline process:{py_dict}')
        return item

    # 在爬虫关闭的时候仅执行一次
    def close_spider(self, spider):
        spider.logger.info(f'{spider.name}.json 文件关闭了。')
        self.file_.close()
