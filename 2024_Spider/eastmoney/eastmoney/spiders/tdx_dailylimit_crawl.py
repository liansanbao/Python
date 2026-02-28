import datetime
import json

import jsonpath
from scrapy.utils.project import get_project_settings

from ..items import *
from .eastmoneyTools import now_date


class TdxDailylimitCrawlSpider(scrapy.Spider):
    name = "tdx_dailylimit_crawl"
    allowed_domains = ["tdx.com.cn"]
    # start_urls = ["https://tdx.com.cn"]
    # url_base = 'https://push2ex.eastmoney.com/getTopicZTPool?'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 今日日期
        self.sale_data = datetime.date.today().strftime('%Y-%m-%d')
        # self.logger.info(f'self.userInfoDect: {self.userInfoDect.keys()}')
        self.settings = get_project_settings()
        # 用户信息存储, 减少访问服务器的负担
        self.dailyStockNoDect = self.load_existing_json() # 加载已有的用户信息

    # 读取已有的用户信息
    def load_existing_json(self):
        # 读取userinfo.json文件中所有信息
        result = {}
        try:
            jsonPath = self.settings.get('OUTPUT_FILE_PATH')
            with open(f'{jsonPath}dailylimit_crawl_{self.sale_data}.json', 'r', encoding='utf-8') as r:
                for line in r:
                    line = line.strip()
                    if line: # 跳过空行
                        data = json.loads(line)
                        result.update(data)
        except (FileNotFoundError, json.JSONDecodeError):
            return dict()
        return result

    def start_requests(self):
        # 涨停主题和原因
        # https://fk.tdx.com.cn/TQLEX?Entry=CWServ.tdxsj_tzrl_gsrl
        # POST：{"Params":["zdtfx","ztfx","2025-07-10","0","2","20"]}
        #       {"Params":["zdtfx","ztfx","2025-07-10","1","1","20"]}
        #       {"Params":["zdtfx","ztfx","2025-07-10","0","3","20"]}
        #       {"Params":["zdtfx","ztfx","2025-07-10","0","4","20"]}
        tdx_url = 'https://fk.tdx.com.cn/TQLEX?Entry=CWServ.tdxsj_tzrl_gsrl'
        data_str = json.dumps({"Params": ["zdtfx", "ztfx", self.sale_data, "1", "1", "200"]})
        self.logger.info(f'tdx_url: {tdx_url} BODY: {data_str}')
        yield scrapy.Request(tdx_url, method='POST', callback=self.parse,
                             body=data_str, headers={'Content-Type': 'application/json'})

    def parse(self, response):
        json_data = response.json()
        # content
        resultSets_list = jsonpath.jsonpath(json_data, '$..ResultSets')
        report_list = []
        for item in resultSets_list:
            if item[0]['Count'] >= 20:
                content_list = item[0]['Content']
                for content in content_list:
                    # 股票名称包含ST开头的不要
                    if str(content[7]).find('ST') != -1:
                        self.logger.info(f'{content[7]}: {content[6]}')
                        continue

                    # 类型为曾涨停的不要
                    if str(content[4]).find('曾涨停') != -1:
                        self.logger.info(f'{content[7]}: {content[4]}')
                        continue

                    # 涨停板之外的排除
                    if not content[6] in self.dailyStockNoDect.keys():
                        self.logger.info(f'{content[7]}: {content[6]}')
                        continue

                    report_list.append([content[1], content[2], content[5], content[6], content[7]])
                # 其它暂时不处理
                break
        self.logger.info(f'涨停数据件数: {len(report_list)}')
        # 当日日期 yyyymmdd
        now_ymd = now_date()
        # 涨停数据取得
        for report_item in report_list:
            zjlx_item = EastmoneyItem()
            # 股票代码
            zjlx_item["f12"] = report_item[3]
            # 股票名称
            zjlx_item["f14"] = report_item[4]
            # 涨停主题
            zjlx_item["limitTitle"] = report_item[0]
            # 涨停原因
            zjlx_item["limitWhy"] = report_item[1]
            # 概念
            zjlx_item["concept"] = report_item[2]
            # 数据采集日期
            zjlx_item["frq"] = now_ymd
            # self.logger.info(f'zjlx_item: {zjlx_item}')
            yield zjlx_item

