# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json

from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy.utils.project import get_project_settings


class MaoyanPipeline:
    # 在爬虫开启的时候仅执行一次
    def open_spider(self, spider):
        self.file_ = open(f'{spider.name}.json', 'w', encoding='utf-8')
        spider.logger.info(f'{spider.name}.json 文件已经打开了。')

    # 数据保存
    def process_item(self, item, spider):
        # 先把键值对的item对象转成字典
        py_dict = dict(item)
        new_dic = {'影片': py_dict['movieName'], '综合票房': py_dict['num'], '票房占比': py_dict['boxRate'], '排片场次': py_dict['showCount']}
        # 把字典数据转json
        json_data = json.dumps(new_dic, ensure_ascii=False) + ', \n'
        self.file_.write(json_data)
        spider.logger.info(f'DoubanPipeline process:{new_dic}')
        return item

    # 在爬虫关闭的时候仅执行一次
    def close_spider(self, spider):
        spider.logger.info(f'{spider.name}.json 文件关闭了。')
        self.file_.close()

# mongoDB数据登录
class MaoyanMongoPipeline(object):
    def __init__(self):
        settings = get_project_settings()
        self.con = MongoClient(host=settings.get('MONGODB_HOST'), port=settings.get('MONGODB_PORT'))  # 实例化mongoclient
        self.collection = self.con[settings.get('MONGODB_DATABASE')][settings.get('MONGODB_COLLECTION')]

    def open_spider(self, spider):
        spider.logger.info(f'MongoDB已经打开了，可以写数据了。。。。。')

    def process_item(self, item, spider):
        py_dict = dict(item)
        mongo_dict = {'影片': py_dict['movieName'], '综合票房': py_dict['num'], '票房占比': py_dict['boxRate'], '排片场次': py_dict['showCount']}
        spider.logger.info(f'MaoyanMongoPipeline process:{mongo_dict}')
        with self.con.start_session() as session:
            session.start_transaction()
            try:
                # 以影片作为更新条件，upsert=True为不满足就进行插入操作
                resutl = self.collection.update_one(
                    {'影片': py_dict['movieName']},
                    {'$set': mongo_dict},
                    upsert=True,
                    session=session
                )
                spider.logger.info(f'更新件数： {resutl.modified_count}')
                session.commit_transaction()
            except Exception as e:
                session.abort_transaction()
                spider.logger.info(f'事务回滚： {str(e)}')
        # self.collection.insert_one(mongo_dict)  # 此时item对象需要先转换为字典,再插入
        # 不return的情况下，另一个权重较低的pipeline将不会获得item
        return item

    # 在爬虫关闭的时候仅执行一次
    def close_spider(self, spider):
        spider.logger.info(f'MongoDB关闭了。')
        self.con.close()