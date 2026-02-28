# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import datetime
import json

from itemadapter import ItemAdapter

# Json文件出力
from pymongo import MongoClient
from scrapy.utils.project import get_project_settings


class XiaohongshuPipeline:
    # 在爬虫开启的时候仅执行一次
    def open_spider(self, spider):
        self.jsonFile = f'{spider.name}.json'
        # 以追加模式打开文件，保留历史数据
        self.file_ = open(self.jsonFile, 'a', encoding='utf-8')
        spider.logger.info(f'{spider.name}.json 文件已经打开了。')

    # 数据保存
    def process_item(self, item, spider):
        # 先把键值对的item对象转成字典
        py_dict = dict(item)
        if py_dict['userId'] != 'JSON' and py_dict["redId"] != '':
            new_dic = {py_dict["userId"]: [py_dict["userName"], py_dict["redId"], py_dict["userIp"]]}
            # 将新数据按行追加写入文件
            line = json.dumps(ItemAdapter(new_dic).asdict(), ensure_ascii=False) + '\n'
            self.file_.write(line)
            spider.logger.info(f'XiaohongshuPipeline process:{new_dic}')
        return item

    # 在爬虫关闭的时候仅执行一次
    def close_spider(self, spider):
        spider.logger.info(f'{self.jsonFile} 文件关闭了。')
        self.file_.close()


# mongoDB数据登录
class XiaohongshuMongoPipeline(object):
    def __init__(self):
        settings = get_project_settings()
        self.con = MongoClient(host=settings.get('MONGODB_HOST'), port=settings.get('MONGODB_PORT'))  # 实例化mongoclient
        self.collection = self.con[settings.get('MONGODB_DATABASE')][settings.get('MONGODB_COLLECTION')]

    def open_spider(self, spider):
        spider.logger.info(f'MongoDB已经打开了，可以写数据了。。。。。')

    def process_item(self, item, spider):
        py_dict = dict(item)
        mongo_dict = {'评论标题': py_dict['display_title'], '评论时间': py_dict['create_time'], '评论内容id': py_dict['display_contentId'],
                   '评论内容': py_dict['display_content'], '评论人': py_dict['userName'], '小红书号': py_dict['redId'], 'IP属地': py_dict['userIp']}
        # spider.logger.info(f'XiaohongshuMongoPipeline process:{mongo_dict}')
        with self.con.start_session() as session:
            session.start_transaction()
            try:
                # 以评论内容id作为更新条件，upsert=True为不满足就进行插入操作
                resutl = self.collection.update_one(
                    {'评论内容id': mongo_dict['评论内容id']},
                    {'$set': mongo_dict},
                    upsert=True,
                    session=session
                )
                spider.logger.info(f'更新件数： {resutl.modified_count}')
                session.commit_transaction()
            except Exception as e:
                session.abort_transaction()
                spider.logger.info(f'事务回滚： {str(e)}')
        return item

    # 在爬虫关闭的时候仅执行一次
    def close_spider(self, spider):
        spider.logger.info(f'MongoDB关闭了。')
        self.con.close()