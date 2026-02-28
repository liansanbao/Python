# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pandas
from itemadapter import ItemAdapter

# 数据存储在Excel表格中
class BookdangdangPipeline:
    def __init__(self):
        self.data = []

    def process_item(self, item, spider):
        # 先把键值对的item对象转成字典
        py_dict = dict(item)
        if spider.name == 'dangdang':
            py_dict = {'标题': py_dict['title'], '评论数': py_dict['commentsNum'], '推荐度': py_dict['reco'],
                       '作者': py_dict['author'], '出版社': py_dict['publishingHouse'], '出版时间': py_dict['publishingTime'],
                       '售价': py_dict['price'], '原价': py_dict['original'], '电子书价格': py_dict['ebookPrice'], '详情链接': py_dict['detailsPage']}
        self.data.append(py_dict)
        spider.logger.info(f'BookdangdangPipeline process:{py_dict}')
        return item

    def close_spider(self, spider):
        # 批量转换为DataFrame 并保存
        df = pandas.DataFrame(self.data)
        df.to_excel(f'../{spider.name}.xlsx', index=False)
        spider.logger.info(f'../{spider.name}.xlsx文件已生成！')
