import json
import time

import jsonpath
from .eastmoneyTools import get_quarter_dates, str_to_int, now_date
from scrapy.utils.project import get_project_settings
from ..items import *

class TdxIvperCrawlSpider(scrapy.Spider):
    name = "tdx_ivper_crawl"
    allowed_domains = ["tdx.com.cn"]
    custom_settings = {
        'DOWNLOAD_DELAY': 1,  # 替代time.sleep
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'RETRY_TIMES': 3
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 今日日期
        self.nowDate = now_date()
        # 报告日期
        self.endDate = get_quarter_dates()['end_date']
        # self.endDate = ['20250630', '20250331',
        #                 '20241231', '20240930', '20240630', '20240331',
        #                 '20231231', '20230930', '20230630', '20230331',
        #                 '20221231', '20220930', '20220630', '20220331',
        #                 '20211231', '20210930', '20210630', '20210331',
        #                 '20201231', '20200930', '20200630', '20200331']
        # self.endDate = '20250630'
        # self.logger.info(f'self.userInfoDect: {self.userInfoDect.keys()}')
        self.settings = get_project_settings()
        self.base_url = 'https://fk.tdx.com.cn/TQLEX?Entry=CWServ.tdxsj_jgcg_jgcg'
        self.max_pages = 100  # 最大页数限制
        # 用户信息存储, 减少访问服务器的负担
        self.ivperStockNoDect = self.read_existing_json()  # 加载已有的用户信息

    # 读取已有的用户信息
    def read_existing_json(self):
        # 读取userinfo.json文件中所有信息
        result = {}
        try:
            jsonPath = self.settings.get('OUTPUT_FILE_PATH')
            self.ivperJsonFile = f'{jsonPath}tdx_ivper_crawl_{self.endDate}.json'
            with open(self.ivperJsonFile, 'r', encoding='utf-8') as r:
                for line in r:
                    line = line.strip()
                    if line:  # 跳过空行
                        data = dict(json.loads(line))
                        result[data['f12']] = data
        except (FileNotFoundError, json.JSONDecodeError):
            return dict()
        # print(f'result: {result}')
        return result

    # 读取已有的用户信息
    def write_existing_json(self, result: dict = {}):
        # 读取userinfo.json文件中所有信息
        try:
            jsonPath = self.settings.get('OUTPUT_FILE_PATH')
            self.ivperJsonFile = f'{jsonPath}tdx_ivper_crawl_{self.endDate}.json'
            with open(self.ivperJsonFile, 'w', encoding='utf-8') as w:
                for key, value in result.items():
                    json_data = json.dumps(value, ensure_ascii=False) + '\n'
                    w.write(json_data)
        except (FileNotFoundError, json.JSONDecodeError) as ex:
            self.logger.info(f'base_url Json文件写入失败: {str(ex)}')

    def start_requests(self):
        # 机构持股一览 增仓的数据
        # https://fk.tdx.com.cn/TQLEX?Entry=CWServ.tdxsj_jgcg_jgcg
        # POST：{"Params":["1","99","1","20250630","050","","0","1","40"]}  增仓
        #      {"Params":["1","99","2","20250630","010","","1","1","40"]}  减仓
        #      {"Params":["1","99","3","20250630","050","","1","1","40"]}  新进
        #      {"Params":["1","99","0","20250630","010","","1","1","40"]}  重仓[增仓,减仓,新进]
        payload = {
            "Params": ["1", "99", "0", self.endDate, "010", "", "1", "1", "40"]
        }
        self.logger.info(f'base_url: {self.base_url} BODY: {payload}')
        yield scrapy.Request(
            url=self.base_url,
            method='POST',
            body=json.dumps(payload),
            headers={'Content-Type': 'application/json'},
            callback=self.parse,
            meta={'page': 1, 'rowSize': 0}
        )

    def parse(self, response):
        try:
            json_data = response.json()
            # 处理分页
            rowSize = response.meta['rowSize']
            if response.status != 200:
                self.logger.info(f'一共采集了{rowSize}条数据！！！！')
                return

            # content
            resultSets_list = jsonpath.jsonpath(json_data, '$..ResultSets')

            if not resultSets_list or resultSets_list[0][0]['Count'] == 0:
                self.logger.info(f'一共采集了{rowSize}条数据！！！！')
                return

            for item in resultSets_list[0][0]['Content']:
                # 仓位类型
                # if not item[13] in ['增仓', '新进股']:
                #     continue
                # 是否已经采集过 条件1：股票代码不存在需要采集
                if item[1] not in self.ivperStockNoDect.keys():
                    self.ivperStockNoDect[item[1]] = {'f12': item[1], 'REPORT_DATE': item[4], 'INSTITUTION_COUNT': item[6], 'NOW_DATE': self.nowDate}
                    rowSize += 1
                    yield self.process_item(item)

                elif item[1] in self.ivperStockNoDect.keys():
                    # 以股票代码为键，取得对应信息 条件2：机构数不一致需要采集
                    ivperStockDict = self.ivperStockNoDect[item[1]]
                    if item[6] != ivperStockDict['INSTITUTION_COUNT']:
                        self.ivperStockNoDect[item[1]] = {'f12': item[1], 'REPORT_DATE': item[4],
                                                          'INSTITUTION_COUNT': item[6], 'NOW_DATE': self.nowDate}
                        rowSize += 1
                        yield self.process_item(item)

            # 处理分页
            current_page = response.meta['page']
            if resultSets_list[0][0]['Count'] > 0:
                # if current_page < self.max_pages and resultSets_list[0][0]['Count'] > 0:
                next_page = current_page + 1
                payload = {
                    "Params": ["1", "99", "0", self.endDate, "010", "", "1", str(next_page), "40"]
                }
                self.logger.info(f'base_url: {self.base_url} BODY: {payload}')
                yield scrapy.Request(
                    url=self.base_url,
                    method='POST',
                    body=json.dumps(payload),
                    headers={'Content-Type': 'application/json'},
                    callback=self.parse,
                    meta={'page': next_page, 'rowSize': rowSize}
                )
                time.sleep(5)
        except Exception as ex:
            self.logger.error(f'解析错误: {str(ex)}')

    def process_item(self, raw_data):
        # print(f'raw_data: {raw_data}')
        item = EastmoneyItem()
        item["f12"] = raw_data[1]  # 股票代码
        item["f14"] = str(raw_data[0]).strip()  # 股票名称
        item["REPORT_DATE"] = raw_data[4]  # 报告日期
        item["hybk"] = str(raw_data[5]).strip()  # 所属行业
        item["INSTITUTION_COUNT"] = raw_data[6]  # 持股机构数
        item["HOLDING_QUANTITY"] = f'{round(str_to_int(raw_data[7])/10000, 2)}' # 持仓数量（万股）
        item["HOLDING_VALUE"] = f'{round(str_to_int(raw_data[8])/10000, 2)}' # 持仓市值（万元）
        item["TOTAL_SHARE_RATIO"] = raw_data[9] # 占总股本比例（%）
        item["FLOAT_SHARE_RATIO"] = raw_data[10] # 占已流通A股比例（%）
        item["CHANGE_QUANTITY"] = f'{round(str_to_int(raw_data[11])/10000, 2)}' # 较上期增减仓股数（万股）
        item["CHANGE_RATIO"] = raw_data[12] # 增减仓占已流通A股比例（%）
        item["POSITION_TYPE"] = raw_data[13] # 仓位类型
        # print(f'item: {item}')
        return item

    def close(self, spider, reason):
        self.logger.info(f'要处理 {len(self.ivperStockNoDect)} 件。')
        self.write_existing_json(self.ivperStockNoDect)