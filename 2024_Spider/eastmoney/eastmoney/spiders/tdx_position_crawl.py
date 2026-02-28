import datetime
import json
import time

import jsonpath
from ..items import *
from scrapy.utils.project import get_project_settings
from .eastmoneyTools import get_quarter_dates, str_to_int


class TdxPositionCrawlSpider(scrapy.Spider):
    name = "tdx_position_crawl"
    allowed_domains = ["tdx.com.cn"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 今日日期
        self.sale_data = datetime.date.today().strftime('%Y-%m-%d')
        # 报告日期
        self.endDate = get_quarter_dates()['end_date']
        # self.logger.info(f'self.userInfoDect: {self.userInfoDect.keys()}')
        self.settings = get_project_settings()
        self.base_url = 'https://fk.tdx.com.cn/TQLEX?Entry=CWServ.tdxsj_jgcg_jgcgmx'
        self.max_pages = 1  # 最大页数限制
        # 用户信息存储, 减少访问服务器的负担
        self.ivperStockNoDect = self.load_existing_json()  # 加载已有的用户信息

    # 读取已有的用户信息
    def load_existing_json(self):
        # 读取userinfo.json文件中所有信息
        result = []
        try:
            jsonPath = self.settings.get('OUTPUT_FILE_PATH')
            self.ivperJsonFile = f'{jsonPath}tdx_ivper_crawl_{self.sale_data}.json'
            with open(self.ivperJsonFile, 'r', encoding='utf-8') as r:
                for line in r:
                    line = line.strip()
                    if line:  # 跳过空行
                        data = dict(json.loads(line))
                        result.append(data)
        except (FileNotFoundError, json.JSONDecodeError):
            return dict()
        return result

    def start_requests(self):
        # check
        if not self.ivperStockNoDect or len(self.ivperStockNoDect) == 0:
            self.logger.error(f'Json文件数据没有了: {self.ivperJsonFile}')
            return

        # 持股机构总览
        # https://fk.tdx.com.cn/TQLEX?Entry=CWServ.tdxsj_jgcg_jgcgmx
        # POST：{"Params":["2","99","20250630","600663","1","1","40"]}
        # 所有持股一览
        for item in self.ivperStockNoDect:
            payload = {
                "Params": ["2", "99", item['REPORT_DATE'], item['f12'], "1", '1', "40"]
            }
            self.logger.info(f'base_url: {self.base_url} BODY: {payload}')
            yield scrapy.Request(
                url=self.base_url,
                method='POST',
                body=json.dumps(payload),
                headers={'Content-Type': 'application/json'},
                callback=self.parse,
                meta={'page': 1, 'item': item}
            )
            time.sleep(3)

    def parse(self, response):
        try:
            json_data = response.json()
            if response.status != 200:
                self.logger.error(f'请求失败: {response.status}')
                return
            # content
            resultSets_list = jsonpath.jsonpath(json_data, '$..ResultSets')

            if not resultSets_list or resultSets_list[0][0]['Count'] == 0:
                self.logger.info('无更多数据')
                return

            ivper_item = response.meta['item']
            for item in resultSets_list[0][0]['Content']:
                # print(f'item: {item}')
                yield self.process_item(item, ivper_item)

        except Exception as ex:
            self.logger.error(f'解析错误: {str(ex)}')

    def process_item(self, raw_data, ivper_item):
        item = EastmoneyItem()
        item["f12"] = ivper_item["f12"]  # 股票代码
        item["REPORT_DATE"] = ivper_item["REPORT_DATE"]  # 报告日期
        item["INSTITUTION_NAME"] = raw_data[0] # 持股机构名称
        item["INSTITUTION_TYPE"] = raw_data[1]  # 机构属性(如:一般法人/基金/QFII等)
        item["HOLDING_QUANTITY"] = f'{round(str_to_int(raw_data[2]) / 10000, 2)}'  # 持仓数量(万股)
        item["HOLDING_VALUE"] = f'{round(str_to_int(raw_data[3]) / 10000, 2)}'  # 持仓市值(万元)
        item["TOTAL_SHARE_RATIO"] = raw_data[4]  # 占总股本比例(%)
        item["FLOAT_SHARE_RATIO"] = raw_data[5]  # 占已流通A股比例(%)
        # print(f'item: {item}')
        return item