# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
import datetime
import json
import pymysql
from scrapy.exceptions import DropItem

from pymongo import MongoClient
from scrapy.utils.project import get_project_settings
from .spiders.eastmoneyTools import get_quarter_dates

class EastmoneyPipeline:
    def __init__(self):
        self.settings = get_project_settings()
        self.sale_data = datetime.date.today().strftime('%Y-%m-%d')

        # 在爬虫开启的时候仅执行一次
    def open_spider(self, spider):
        if spider.name in ['dailylimit_crawl', 'tdx_ivper_crawl']:
            self.fileName = f"{self.settings['OUTPUT_FILE_PATH']}{spider.name}_{self.sale_data}.json"
            self.file_ = open(self.fileName, 'w', encoding='utf-8')
            spider.logger.info(f'{self.fileName} 文件已经打开了。')

    # 数据保存
    def process_item(self, item, spider):
        # 先把键值对的item对象转成字典
        py_dict = dict(item)
        if spider.name == 'zjlx_crawl':
            new_dic = {'股票代码': py_dict['f12'], '股票名称': py_dict['f14'], '最新价': py_dict['f2'],
                       '今日涨跌幅': py_dict['f3'],
                       '今日主力净流入(净额)': py_dict['f62'], '今日主力净流入(净占比)': py_dict['f184'],
                       '今日超大单净流入(净额)': py_dict['f66'], '今日超大单净流入(净占比)': py_dict['f69'],
                       '今日大单净流入(净额)': py_dict['f72'], '今日大单净流入(净占比)': py_dict['f75'],
                       '今日中单净流入(净额)': py_dict['f78'], '今日中单净流入(净占比)': py_dict['f81'],
                       '今日小单净流入(净额)': py_dict['f84'], '今日小单净流入(净占比)': py_dict['f87'], '数据采集日期': py_dict['frq'], '所属行业': py_dict['hybk'],
                       '深度数据': py_dict['depthData'], '量比': py_dict['f50'], '换手': py_dict['f168']}
        elif spider.name == 'hyzjl_crawl':
            new_dic = {'行业代码': py_dict['f12'], '行业名称': py_dict['f14'], '最新价': py_dict['f2'],
                       '今日涨跌幅': py_dict['f3'],
                       '今日主力净流入(净额)': py_dict['f62'], '今日主力净流入(净占比)': py_dict['f184'],
                       '今日超大单净流入(净额)': py_dict['f66'], '今日超大单净流入(净占比)': py_dict['f69'],
                       '今日大单净流入(净额)': py_dict['f72'], '今日大单净流入(净占比)': py_dict['f75'],
                       '今日中单净流入(净额)': py_dict['f78'], '今日中单净流入(净占比)': py_dict['f81'],
                       '今日小单净流入(净额)': py_dict['f84'], '今日小单净流入(净占比)': py_dict['f87'],
                       '今日主力净流入(最大股名称)': py_dict['f204'], '今日主力净流入(最大股代码)': py_dict['f205'], '数据采集日期': py_dict['frq']}
        elif spider.name == 'dailylimit_crawl':
            new_dic = {py_dict['f12']: py_dict['frq']}
            # new_dic = {'股票代码': py_dict['f12'], '股票名称': py_dict['f14'], '最新价': py_dict['f2'],
            #            '涨跌幅': py_dict['f3'], '游资': py_dict['youzi'],
            #            '成交额': py_dict['f62'], '流通市值': py_dict['f184'],
            #            '总市值': py_dict['f66'], '换手率': py_dict['f69'],
            #            '封板资金': py_dict['f72'], '首次封板时间': py_dict['f75'],
            #            '最后封板时间': py_dict['f78'], '炸板次数': py_dict['f81'],
            #            '涨停统计': py_dict['f84'], '连板数': py_dict['f87'], '所属行业': py_dict['hybk'], '数据采集日期': py_dict['frq']}
        elif spider.name == 'mainStock_crawl':
            new_dic = {'股票代码': py_dict['f12'], '股票名称': py_dict['f14'], '最新价': py_dict['f2'],
                       '今日净占比': py_dict['f184'], '今日排名': py_dict['f225'],
                       '今日涨跌': py_dict['f3'], '5日净占比': py_dict['f165'],
                       '5日排名': py_dict['f263'], '5日涨跌': py_dict['f109'],
                       '10日净占比': py_dict['f175'], '10日排名': py_dict['f264'],
                       '10日涨跌': py_dict['f160'], '所属板块ID': py_dict['f265'],
                       '所属板块名称': py_dict['f100'], '量比': py_dict['f50'], '换手': py_dict['f168'], '数据采集日期': py_dict['frq']}
        elif spider.name == 'tdx_dailylimit_crawl':
            new_dic = {'股票代码': py_dict['f12'], '股票名称': py_dict['f14'], '数据采集日期': py_dict['frq'],
                       '涨停主题': py_dict['limitTitle'], '涨停原因': py_dict['limitWhy'], '概念': py_dict['concept']}
        elif spider.name == 'tdx_ivper_crawl':
            new_dic = {'f12': py_dict['f12'], 'REPORT_DATE': py_dict['REPORT_DATE'], 'INSTITUTION_COUNT': py_dict['INSTITUTION_COUNT']}
        # 把字典数据转json
        if spider.name in ['dailylimit_crawl', 'tdx_ivper_crawl']:
            json_data = json.dumps(new_dic, ensure_ascii=False) + '\n'
            self.file_.write(json_data)
        # spider.logger.info(f'{self.fileName} EastmoneyPipeline process:{new_dic}')
        return item

    # 在爬虫关闭的时候仅执行一次
    def close_spider(self, spider):
        if spider.name in ['dailylimit_crawl', 'tdx_ivper_crawl']:
            spider.logger.info(f'{self.fileName} 文件关闭了。')
            self.file_.close()

# mongoDB数据登录
class EastmoneyMongoPipeline(object):
    def __init__(self):
        self.settings = get_project_settings()
        self.con = MongoClient(host=self.settings.get('MONGODB_HOST'), port=self.settings.get('MONGODB_PORT'))  # 实例化mongoclient

    def open_spider(self, spider):
        if spider.name == 'zjlx_crawl':
            self.collection = self.con[self.settings.get('MONGODB_DATABASE')][self.settings.get('MONGODB_COLLECTION_ZJLX')]
        elif spider.name == 'hyzjl_crawl':
            self.collection = self.con[self.settings.get('MONGODB_DATABASE')][self.settings.get('MONGODB_COLLECTION_HYZJL')]
        elif spider.name == 'dailylimit_crawl':
            self.collection = self.con[self.settings.get('MONGODB_DATABASE')][self.settings.get('MONGODB_COLLECTION_DAILYLIMIT')]
        elif spider.name == 'mainStock_crawl':
            self.collection = self.con[self.settings.get('MONGODB_DATABASE')][self.settings.get('MONGODB_COLLECTION_MAINSTOCK')]
        elif spider.name == 'tdx_dailylimit_crawl':
            self.collection = self.con[self.settings.get('MONGODB_DATABASE')][self.settings.get('MONGODB_COLLECTION_TDXDAILYLIMIT')]
        spider.logger.info(f'MongoDB已经打开了，{spider.name}可以写数据了。。。。。')

    def process_item(self, item, spider):
        py_dict = dict(item)
        if spider.name == 'zjlx_crawl':
            mongo_dict = {'股票代码': py_dict['f12'], '股票名称': py_dict['f14'], '最新价': py_dict['f2'],
                       '今日涨跌幅': py_dict['f3'],
                       '今日主力净流入(净额)': py_dict['f62'], '今日主力净流入(净占比)': py_dict['f184'],
                       '今日超大单净流入(净额)': py_dict['f66'], '今日超大单净流入(净占比)': py_dict['f69'],
                       '今日大单净流入(净额)': py_dict['f72'], '今日大单净流入(净占比)': py_dict['f75'],
                       '今日中单净流入(净额)': py_dict['f78'], '今日中单净流入(净占比)': py_dict['f81'],
                       '今日小单净流入(净额)': py_dict['f84'], '今日小单净流入(净占比)': py_dict['f87'], '数据采集日期': py_dict['frq'], '所属行业': py_dict['hybk'],
                       '深度数据': py_dict['depthData'], '量比': py_dict['f50'], '换手': py_dict['f168']}
            condition_key = '股票代码'
        elif spider.name == 'hyzjl_crawl':
            mongo_dict = {'行业代码': py_dict['f12'], '行业名称': py_dict['f14'], '最新价': py_dict['f2'],
                       '今日涨跌幅': py_dict['f3'],
                       '今日主力净流入(净额)': py_dict['f62'], '今日主力净流入(净占比)': py_dict['f184'],
                       '今日超大单净流入(净额)': py_dict['f66'], '今日超大单净流入(净占比)': py_dict['f69'],
                       '今日大单净流入(净额)': py_dict['f72'], '今日大单净流入(净占比)': py_dict['f75'],
                       '今日中单净流入(净额)': py_dict['f78'], '今日中单净流入(净占比)': py_dict['f81'],
                       '今日小单净流入(净额)': py_dict['f84'], '今日小单净流入(净占比)': py_dict['f87'],
                       '今日主力净流入(最大股名称)': py_dict['f204'], '今日主力净流入(最大股代码)': py_dict['f205'], '数据采集日期': py_dict['frq']}
            condition_key = '行业代码'
        elif spider.name == 'dailylimit_crawl':
            mongo_dict = {'股票代码': py_dict['f12'], '股票名称': py_dict['f14'], '最新价': py_dict['f2'],
                       '涨跌幅': py_dict['f3'], '游资': py_dict['youzi'],
                       '成交额': py_dict['f62'], '流通市值': py_dict['f184'],
                       '总市值': py_dict['f66'], '换手率': py_dict['f69'],
                       '封板资金': py_dict['f72'], '首次封板时间': py_dict['f75'],
                       '最后封板时间': py_dict['f78'], '炸板次数': py_dict['f81'],
                       '涨停统计': py_dict['f84'], '连板数': py_dict['f87'], '所属行业': py_dict['hybk'], '数据采集日期': py_dict['frq']}
            condition_key = '股票代码'
        elif spider.name == 'mainStock_crawl':
            mongo_dict = {'股票代码': py_dict['f12'], '股票名称': py_dict['f14'], '最新价': py_dict['f2'],
                       '今日净占比': py_dict['f184'], '今日排名': py_dict['f225'],
                       '今日涨跌': py_dict['f3'], '5日净占比': py_dict['f165'],
                       '5日排名': py_dict['f263'], '5日涨跌': py_dict['f109'],
                       '10日净占比': py_dict['f175'], '10日排名': py_dict['f264'],
                       '10日涨跌': py_dict['f160'], '所属板块ID': py_dict['f265'],
                       '所属板块名称': py_dict['f100'], '量比': py_dict['f50'], '换手': py_dict['f168'], '数据采集日期': py_dict['frq']}
            condition_key = '股票代码'
        elif spider.name == 'tdx_dailylimit_crawl':
            mongo_dict = {'股票代码': py_dict['f12'], '股票名称': py_dict['f14'], '数据采集日期': py_dict['frq'],
                       '涨停主题': py_dict['limitTitle'], '涨停原因': py_dict['limitWhy'], '概念': py_dict['concept']}
            condition_key = '股票代码'

        # spider.logger.info(f'{spider.name} process:{mongo_dict}')
        with self.con.start_session() as session:
            session.start_transaction()
            try:
                # 以影片作为更新条件，upsert=True为不满足就进行插入操作
                resutl = self.collection.update_one(
                    {condition_key: py_dict['f12'], '数据采集日期': py_dict['frq']},
                    {'$set': mongo_dict},
                    upsert=True,
                    session=session
                )
                # spider.logger.info(f'EastmoneyMongoPipeline 更新件数： {resutl.modified_count}')
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
        self.con.clos

# Mysql数据登录
class EastmoneyMysqlPipeline:
    def __init__(self, mysql_host, mysql_port, mysql_db, mysql_user, mysql_pass, mysql_charset):
        # 初始化数据库连接参数
        self.mysql_host = mysql_host
        self.mysql_port = mysql_port
        self.mysql_db = mysql_db
        self.mysql_user = mysql_user
        self.mysql_pass = mysql_pass
        self.mysql_charset = mysql_charset

        # 连接对象和游标
        self.conn = None
        self.cursor = None
        # 资金流向表数据插入
        self.insert_zjlx_sql = f"""
            INSERT INTO ZJLX_CRAWL (
                       STOCK_NO,
                       STOCK_NAME,
                       ZHANG_FU,
                       XIAN_JIA,
                       CREATE_DATE,
                       F62,
                       F184,
                       F66,
                       F69,
                       F72,
                       F75,
                       F78,
                       F81,
                       F84,
                       F87,
                       hybk,
                       depthData,
                       F50,
                       F168,
                       secucode,
                       endData
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                       STOCK_NO = VALUES(STOCK_NO),
                       CREATE_DATE = VALUES(CREATE_DATE),
                       STOCK_NAME = VALUES(STOCK_NAME),
                       ZHANG_FU = VALUES(ZHANG_FU),
                       XIAN_JIA = VALUES(XIAN_JIA),
                       F62 = VALUES(F62),
                       F184 = VALUES(F184),
                       F66 = VALUES(F66),
                       F69 = VALUES(F69),
                       F72 = VALUES(F72),
                       F75 = VALUES(F75),
                       F78 = VALUES(F78),
                       F81 = VALUES(F81),
                       F84 = VALUES(F84),
                       F87 = VALUES(F87),
                       hybk = VALUES(hybk),
                       depthData = VALUES(depthData),
                       F50 = VALUES(F50),
                       F168 = VALUES(F168),
                       secucode = VALUES(secucode),
                       endData = VALUES(endData)  
                    """
        # 行业资金流向表数据插入
        self.insert_hyzjl_sql = f"""
            INSERT INTO HYZJL_CRAWL (
               F12,
               F14,
               F2,
               F3,
               F62,
               F184,
               F66,
               F69,
               F72,
               F75,
               F78,
               F81,
               F84,
               F87,
               F204,
               F205,
               ActivateType,
               hyType
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
               F12 = VALUES(F12),
               F14 = VALUES(F14),
               F2 = VALUES(F2),
               F3 = VALUES(F3),
               F62 = VALUES(F62),
               F184 = VALUES(F184),
               F66 = VALUES(F66),
               F69 = VALUES(F69),
               F72 = VALUES(F72),
               F75 = VALUES(F75),
               F78 = VALUES(F78),
               F81 = VALUES(F81),
               F84 = VALUES(F84),
               F87 = VALUES(F87),
               F204 = VALUES(F204),
               F205 = VALUES(F205),
               ActivateType = VALUES(ActivateType),
               hyType = VALUES(hyType)
            """
        # 涨停板表数据插入
        self.insert_dailylimit_sql = f"""
            INSERT INTO DAILYLIMIT (
               CREATE_DATE,
               F12,
               F14,
               F2,
               F3,
               YOUZI,
               F62,
               F184,
               F66,
               F69,
               F72,
               F75,
               F78,
               F81,
               F84,
               F87,
               HYBK,
               secucode,
               endData
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
               F12 = VALUES(F12),
               CREATE_DATE = VALUES(CREATE_DATE),
               F14 = VALUES(F14),
               F2 = VALUES(F2),
               F3 = VALUES(F3),
               YOUZI = VALUES(YOUZI),
               F62 = VALUES(F62),
               F184 = VALUES(F184),
               F66 = VALUES(F66),
               F69 = VALUES(F69),
               F72 = VALUES(F72),
               F75 = VALUES(F75),
               F78 = VALUES(F78),
               F81 = VALUES(F81),
               F84 = VALUES(F84),
               F87 = VALUES(F87),
               HYBK = VALUES(HYBK),
               secucode = VALUES(secucode),
               endData = VALUES(endData)  
            """
        # 通达信涨停分析表数据插入
        self.insert_tdx_dailylimit_sql = f"""
                    INSERT INTO TDX_DAILYLIMIT (
                       CREATE_DATE,
                       F12,
                       F14,
                       LIMITTITLE,
                       LIMITWHY,
                       CONCEPT
                    ) VALUES (%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE
                       F12 = VALUES(F12),
                       CREATE_DATE = VALUES(CREATE_DATE),
                       F14 = VALUES(F14),
                       LIMITTITLE = VALUES(LIMITTITLE),
                       LIMITWHY = VALUES(LIMITWHY),
                       CONCEPT = VALUES(CONCEPT)  
                    """
        # 所属行业表数据插入
        self.insert_sshy_sql = f"""
            INSERT INTO STOCK_SSHY (
               CREATE_DATE,
               SSHY,
               OPTION_TYPE
            ) VALUES (%s,%s,%s)
            ON DUPLICATE KEY UPDATE
               SSHY = VALUES(SSHY),
               CREATE_DATE = VALUES(CREATE_DATE),
               OPTION_TYPE = VALUES(OPTION_TYPE)  
            """
        # 主力排名表数据插入
        self.insert_mainstock_sql = f"""
                    INSERT INTO MAINSTOCK (
                       CREATE_DATE,
                       F12,
                       F14,
                       F2,
                       F184,
                       F225,
                       F3,
                       F165,
                       F263,
                       F109,
                       F175,
                       F264,
                       F160,
                       F265,
                       F100,
                       F50,
                       F168,
                       depthData,
                       secucode,
                       endData
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE
                       F12 = VALUES(F12),
                       CREATE_DATE = VALUES(CREATE_DATE),
                       F14 = VALUES(F14),
                       F2 = VALUES(F2),
                       F184 = VALUES(F184),
                       F225 = VALUES(F225),
                       F3 = VALUES(F3),
                       F165 = VALUES(F165),
                       F263 = VALUES(F263),
                       F109 = VALUES(F109),
                       F175 = VALUES(F175),
                       F264 = VALUES(F264),
                       F160 = VALUES(F160),
                       F265 = VALUES(F265),
                       F100 = VALUES(F100),
                       F50 = VALUES(F50),
                       F168 = VALUES(F168),
                       depthData = VALUES(depthData),
                       secucode = VALUES(secucode),
                       endData = VALUES(endData)
                    """
        # 持股机构一览表数据插入
        self.insert_stock_holding_sql = f"""
                    INSERT INTO STOCK_HOLDING (
                       STOCK_CODE,
                       STOCK_NAME,
                       REPORT_DATE,
                       INDUSTRY,
                       INSTITUTION_COUNT,
                       HOLDING_QUANTITY,
                       HOLDING_VALUE,
                       TOTAL_SHARE_RATIO,
                       FLOAT_SHARE_RATIO,
                       CHANGE_QUANTITY,
                       CHANGE_RATIO,
                       POSITION_TYPE
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE
                       STOCK_CODE = VALUES(STOCK_CODE),
                       STOCK_NAME = VALUES(STOCK_NAME),
                       REPORT_DATE = VALUES(REPORT_DATE),
                       INDUSTRY = VALUES(INDUSTRY),
                       INSTITUTION_COUNT = VALUES(INSTITUTION_COUNT),
                       HOLDING_QUANTITY = VALUES(HOLDING_QUANTITY),
                       HOLDING_VALUE = VALUES(HOLDING_VALUE),
                       TOTAL_SHARE_RATIO = VALUES(TOTAL_SHARE_RATIO),
                       FLOAT_SHARE_RATIO = VALUES(FLOAT_SHARE_RATIO),
                       CHANGE_QUANTITY = VALUES(CHANGE_QUANTITY),
                       CHANGE_RATIO = VALUES(CHANGE_RATIO),
                       POSITION_TYPE = VALUES(POSITION_TYPE)
                    """
        # 机构持股明细表数据插入
        self.insert_institution_holding_sql = f"""
                    INSERT INTO INSTITUTION_HOLDING_DETAIL (
                       STOCK_CODE,
                       REPORT_DATE,
                       INSTITUTION_TYPE,
                       INSTITUTION_COUNT,
                       HOLDING_QUANTITY,
                       HOLDING_VALUE,
                       TOTAL_SHARE_RATIO,
                       FLOAT_SHARE_RATIO
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE
                       STOCK_CODE = VALUES(STOCK_CODE),
                       REPORT_DATE = VALUES(REPORT_DATE),
                       INSTITUTION_TYPE = VALUES(INSTITUTION_TYPE),
                       INSTITUTION_COUNT = VALUES(INSTITUTION_COUNT),
                       HOLDING_QUANTITY = VALUES(HOLDING_QUANTITY),
                       HOLDING_VALUE = VALUES(HOLDING_VALUE),
                       TOTAL_SHARE_RATIO = VALUES(TOTAL_SHARE_RATIO),
                       FLOAT_SHARE_RATIO = VALUES(FLOAT_SHARE_RATIO)
                    """
        # 机构持股明细表数据插入
        self.insert_position_holding_sql = f"""
                    INSERT INTO POSITION_HOLDING_DETAIL (
                       STOCK_CODE,
                       REPORT_DATE,
                       INSTITUTION_TYPE,
                       INSTITUTION_NAME,
                       HOLDING_QUANTITY,
                       HOLDING_VALUE,
                       TOTAL_SHARE_RATIO,
                       FLOAT_SHARE_RATIO
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE
                       STOCK_CODE = VALUES(STOCK_CODE),
                       REPORT_DATE = VALUES(REPORT_DATE),
                       INSTITUTION_TYPE = VALUES(INSTITUTION_TYPE),
                       INSTITUTION_NAME = VALUES(INSTITUTION_NAME),
                       HOLDING_QUANTITY = VALUES(HOLDING_QUANTITY),
                       HOLDING_VALUE = VALUES(HOLDING_VALUE),
                       TOTAL_SHARE_RATIO = VALUES(TOTAL_SHARE_RATIO),
                       FLOAT_SHARE_RATIO = VALUES(FLOAT_SHARE_RATIO)
                    """
        # 大盘主力资金表数据插入
        self.insert_gridist_stock_sql = f"""
                            INSERT INTO GRIDIST_STOCK (
                               CREATE_DATE,
                               F12,
                               F14,
                               F2,
                               F3,
                               F4,
                               F5,
                               F6,
                               F7,
                               F8,
                               F9,
                               F10,
                               F15,
                               F16,
                               F17,
                               F18,
                               F23,
                               hybk
                            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                            ON DUPLICATE KEY UPDATE
                               CREATE_DATE = VALUES(CREATE_DATE),
                               F12 = VALUES(F12),
                               F14 = VALUES(F14),
                               F2 = VALUES(F2),
                               F3 = VALUES(F3),
                               F4 = VALUES(F4),
                               F5 = VALUES(F5),
                               F6 = VALUES(F6),
                               F7 = VALUES(F7),
                               F8 = VALUES(F8),
                               F9 = VALUES(F9),
                               F10 = VALUES(F10),
                               F15 = VALUES(F15),
                               F16 = VALUES(F16),
                               F17 = VALUES(F17),
                               F18 = VALUES(F18),
                               F23 = VALUES(F23),
                               hybk = VALUES(hybk)
                            """
        # 中国A股表数据插入
        self.insert_aboard_sql = f"""
                                    INSERT INTO ABOARD (
                                       CREATE_DATE,
                                       F12,
                                       F14,
                                       F2,
                                       F3,
                                       F4,
                                       F5,
                                       F6,
                                       F7,
                                       F8,
                                       F9,
                                       F10,
                                       F15,
                                       F16,
                                       F17,
                                       F18,
                                       F23,
                                       hybk
                                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                                    ON DUPLICATE KEY UPDATE
                                       CREATE_DATE = VALUES(CREATE_DATE),
                                       F12 = VALUES(F12),
                                       F14 = VALUES(F14),
                                       F2 = VALUES(F2),
                                       F3 = VALUES(F3),
                                       F4 = VALUES(F4),
                                       F5 = VALUES(F5),
                                       F6 = VALUES(F6),
                                       F7 = VALUES(F7),
                                       F8 = VALUES(F8),
                                       F9 = VALUES(F9),
                                       F10 = VALUES(F10),
                                       F15 = VALUES(F15),
                                       F16 = VALUES(F16),
                                       F17 = VALUES(F17),
                                       F18 = VALUES(F18),
                                       F23 = VALUES(F23),
                                       hybk = VALUES(hybk)
                                    """

    @classmethod
    def from_crawler(cls, crawler):
        # 从settings.py加载配置
        return cls(
            mysql_host=crawler.settings.get('MYSQL_HOST'),
            mysql_port=crawler.settings.get('MYSQL_PORT', 3306),
            mysql_db=crawler.settings.get('MYSQL_DATABASE'),
            mysql_user=crawler.settings.get('MYSQL_USER'),
            mysql_pass=crawler.settings.get('MYSQL_PASS'),
            mysql_charset=crawler.settings.get('MYSQL_CHARSET', 'utf8mb4')
        )

    def open_spider(self, spider):
        # 爬虫启动时建立连接
        self.conn = pymysql.connect(
            host=self.mysql_host,
            port=self.mysql_port,
            user=self.mysql_user,
            password=self.mysql_pass,
            db=self.mysql_db,
            charset=self.mysql_charset,
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cursor = self.conn.cursor()
        spider.logger.info(f'MYSQL已经打开了，{spider.name}可以写数据了。。。。。')

    def close_spider(self, spider):
        # 爬虫关闭时关闭连接
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        spider.logger.info(f'MYSQL关闭了。')

    def process_item(self, item, spider):
        # 根据item中的操作类型执行不同SQL
        try:
            sale_data = datetime.date.today().strftime('%Y-%m-%d')
            # sale_data = '2025-08-01'
            if spider.name == 'zjlx_crawl':
                # 数据插入
                mysql_dict = (item['f12'], item['f14'], item['f3'], item['f2'], sale_data,
                              item['f62'], item['f184'], item['f66'], item['f69'],
                              item['f72'], item['f75'], item['f78'], item['f81'],
                              item['f84'], item['f87'], item['hybk'], item['depthData'], item['f50'], item['f168'],
                              item['secucode'], item['endData'])
                exec_sql = self.insert_zjlx_sql
            elif spider.name == 'hyzjl_crawl':
                activateType = '1' if datetime.datetime.now().strftime('%H%M%S') > '150100' else '0'
                mysql_dict = (item['f12'], item['f14'], item['f2'], item['f3'],
                              item['f62'], item['f184'], item['f66'], item['f69'],
                              item['f72'], item['f75'], item['f78'], item['f81'], item['f84'], item['f87'], item['f204'], item['f205'], activateType, '1')
                exec_sql = self.insert_hyzjl_sql
            elif spider.name == 'concept_crawl':
                activateType = '1'
                mysql_dict = (item['f12'], item['f14'], item['f2'], item['f3'],
                              item['f62'], item['f184'], item['f66'], item['f69'],
                              item['f72'], item['f75'], item['f78'], item['f81'], item['f84'], item['f87'], item['f204'], item['f205'], activateType, '2')
                exec_sql = self.insert_hyzjl_sql
            elif spider.name == 'dailylimit_crawl':
                mysql_dict = (sale_data, item['f12'], item['f14'], item['f2'],
                              item['f3'], item['youzi'], item['f62'], item['f184'],
                              item['f66'], item['f69'], item['f72'], item['f75'], item['f78'], item['f81'], item['f84'], item['f87'], item['hybk'],
                              item['secucode'], item['endData'])
                exec_sql = self.insert_dailylimit_sql
            elif spider.name == 'mainStock_crawl':
                mysql_dict = (sale_data, item['f12'], item['f14'], item['f2'],
                              item['f184'], item['f225'],
                              item['f3'], item['f165'],
                              item['f263'], item['f109'],
                              item['f175'], item['f264'],
                              item['f160'], item['f265'],
                              item['f100'], item['f50'], item['f168'],
                              item['depthData'], item['secucode'], item['endData'])
                exec_sql = self.insert_mainstock_sql
            elif spider.name == 'tdx_dailylimit_crawl':
                mysql_dict = (sale_data, item['f12'], item['f14'],
                              item['limitTitle'], item['limitWhy'], item['concept'])
                exec_sql = self.insert_tdx_dailylimit_sql
            elif spider.name == 'tdx_ivper_crawl':
                mysql_dict = (item['f12'], item['f14'], item['REPORT_DATE'],
                              item['hybk'], item['INSTITUTION_COUNT'],
                              item['HOLDING_QUANTITY'], item['HOLDING_VALUE'],
                              item['TOTAL_SHARE_RATIO'], item['FLOAT_SHARE_RATIO'],
                              item['CHANGE_QUANTITY'], item['CHANGE_RATIO'],
                              item['POSITION_TYPE'])
                exec_sql = self.insert_stock_holding_sql

            elif spider.name == 'tdx_institution_crawl':
                mysql_dict = (item['f12'], item['REPORT_DATE'],
                              item['INSTITUTION_TYPE'], item['INSTITUTION_COUNT'],
                              item['HOLDING_QUANTITY'], item['HOLDING_VALUE'],
                              item['TOTAL_SHARE_RATIO'], item['FLOAT_SHARE_RATIO'])
                exec_sql = self.insert_institution_holding_sql
            elif spider.name == 'tdx_position_crawl':
                mysql_dict = (item['f12'], item['REPORT_DATE'],
                              item['INSTITUTION_TYPE'], item['INSTITUTION_NAME'],
                              item['HOLDING_QUANTITY'], item['HOLDING_VALUE'],
                              item['TOTAL_SHARE_RATIO'], item['FLOAT_SHARE_RATIO'])
                exec_sql = self.insert_position_holding_sql
            elif spider.name == 'gridist_crawl':
                mysql_dict = (sale_data, item['f12'], item['f14'], item['f2'],
                              item['f3'], item['f4'], item['f5'], item['f6'],
                              item['f7'], item['f8'], item['f9'], item['f10'], item['f15'], item['f16'], item['f17'], item['f18'], item['f23'], item['hybk'])
                if float(str(item['f3']).replace('%', '')) >= 4:
                    exec_sql = self.insert_gridist_stock_sql
                    self.cursor.execute(exec_sql, mysql_dict)

                if float(str(item['f2'])) > 0:
                    # 中国A股大盘数据采集
                    exec_sql = self.insert_aboard_sql
                    self.cursor.execute(exec_sql, mysql_dict)

            if spider.name != 'gridist_crawl':
                self.cursor.execute(exec_sql, mysql_dict)

            # spider.logger.info(f'{spider.name} {exec_sql}: {mysql_dict}')
            # self.cursor.execute(self.insert_sshy_sql, mysql_sshy_dict)
            # spider.logger.info(f'{spider.name} {self.insert_sshy_sql}: {mysql_sshy_dict}')
            self.conn.commit()  # 提交事务
        except pymysql.Error as e:
            self.conn.rollback()  # 回滚事务
            spider.logger.error(f"{spider.name} Error: {e}")
            raise DropItem(f"Failed to process item: {e}")

        return item