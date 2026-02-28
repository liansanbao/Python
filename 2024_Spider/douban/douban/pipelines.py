# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import hashlib
import json

from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline # 图片管道
from scrapy.utils.project import get_project_settings

class DoubanPipeline:
    # def __init__(self):
    #     self.file_ = open('douban_31.json', 'w', encoding='utf-8')
    #     print(f'{self.file_}文件打开了。')

    # 在爬虫开启的时候仅执行一次
    def open_spider(self, spider):
        self.file_ = open(f'{spider.name}.json', 'w', encoding='utf-8')
        spider.logger.info(f'{spider.name}.json 文件已经打开了，可以写数据了。。。。。')

    # 数据保存
    def process_item(self, item, spider):
        # 先把键值对的item对象转成字典
        py_dict = dict(item)
        if spider.name == 'crawl_move':
            py_dict = {'电影名称':py_dict['name'], '评分':py_dict['score'], '导演':py_dict['director'], '海报图片': "images/" + py_dict['image_name'] + ".jpg"}
        # 把字典数据转json
        json_data = json.dumps(py_dict, ensure_ascii=False) + ', \n'
        self.file_.write(json_data)
        spider.logger.info(f'DoubanPipeline process:{py_dict}')
        return item

    # 在爬虫关闭的时候仅执行一次
    def close_spider(self, spider):
        spider.logger.info(f'close_spider {self.file_}文件关闭了。')
        self.file_.close()

    # 此方法有问题最好不要使用，建议使用：close_spider 在爬虫关闭的时候仅执行一次
    # def __del__(self):
    #     print(f'{self.file_}文件关闭了。')
    #     self.file_.close()


# mongoDB数据登录
class DoubanMongoPipeline(object):
    def open_spider(self, spider):
        if spider.name == 'movie':
            settings = get_project_settings()
            self.con = MongoClient(host=settings.get('MONGODB_HOST'),
                                   port=settings.get('MONGODB_PORT'))  # 实例化mongoclient
            self.con.doubanSpider.douban.drop()
            self.collection = self.con.doubanSpider.douban  # 创建数据库名为doubanSpider,集合名为douban的集合操作对象
            spider.logger.info(f'MongoDB已经打开了，可以写数据了。。。。。')

    def process_item(self, item, spider):
        if spider.name == 'movie':
            py_dict = dict(item)
            mongo_dict = {'电影名称': py_dict['name'], '电影评分': py_dict['score']}
            self.collection.insert_one(mongo_dict)  # 此时item对象需要先转换为字典,再插入
            spider.logger.info(f'DoubanMongoPipeline process:{mongo_dict}')
        # 不return的情况下，另一个权重较低的pipeline将不会获得item
        return item

    # 在爬虫关闭的时候仅执行一次
    def close_spider(self, spider):
        if spider.name == 'movie':
            spider.logger.info(f'MongoDB关闭了。')
            self.con.close()


# 图片下载
class DoubanPicPipeline(ImagesPipeline):
    # 拿到item对象里面的图片名称数据
    def get_media_requests(self, item, info):
        urls = ItemAdapter(item).get(self.images_urls_field, [])
        return [Request(u, meta={'doubanIamge':item}) for u in urls] # 传递item对象

    # 自定义的图片需要去注册
    def file_path(self, request, response=None, info=None, *, item=None):
        # image_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        image_name = request.meta.get('doubanIamge')['image_name']
        # 修改默认文件夹名称
        return f"images/{image_name}.jpg"