import time

import jsonpath
from .eastmoneyTools import unquote_str, quote_str, str_to_json, now_date, \
    generate_jquery_callback, str_to_float, amountUnitEdit, timestamp_13
from ..items import *

# 概念资金流
class ConceptCrawlSpider(scrapy.Spider):
    name = "concept_crawl"
    allowed_domains = ["eastmoney.com"]
    # start_urls = ["https://eastmoney.com"]
    cb = generate_jquery_callback()
    url_base = f'https://push2.eastmoney.com/api/qt/clist/get?cb={cb}&fid=f62&po=1&pz=99&pn=1&np=1&fltt=2&invt=2&ut=8dec03ba335b81bf4ebdf7b29ec27d15'
    #           https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery112307581714048690535_1744844737268&fid=f62&po=1&pz=50&pn=1&np=1&fltt=2&invt=2&ut=8dec03ba335b81bf4ebdf7b29ec27d15&fs=m%3A90+t%3A2&fields=f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13
    #           https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery112304437305601807815_1745414051539&fid=f62&po=1&pz=50&pn=1&np=1&fltt=2&invt=2&ut=8dec03ba335b81bf4ebdf7b29ec27d15&fs=m%3A90+t%3A2&fields=f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13
    #           https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery112305928687000527004_1760020450143&fid=f62&po=1&pz=50&pn=1&np=1&fltt=2&invt=2&ut=8dec03ba335b81bf4ebdf7b29ec27d15&fs=m%3A90+t%3A3&fields=f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13
    #           https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery112305928687000527004_1760020450143&fid=f62&po=1&pz=50&pn=2&np=1&fltt=2&invt=2&ut=8dec03ba335b81bf4ebdf7b29ec27d15&fs=m%3A90+t%3A3&fields=f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13
    fs = 'm%3A90+t%3A3'
    fields = 'f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13'
    new_fs = quote_str(unquote_str(fs))
    new_fields = quote_str(unquote_str(fields))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Connection': 'keep-alive'
    }

    def start_requests(self):
        url = f'{self.url_base}&fs={self.new_fs}&fields={self.new_fields}'
        self.max_pages = 12
        self.logger.info(f'start_urls： {url}')
        yield scrapy.Request(url=url, callback=self.parse, meta={'page': 1})

    def parse(self, response):
        try:
            # self.logger.info(f'response data： {response.text}')
            # 请求状态判定
            if response.status != 200:
                self.logger.error(f'请求失败: {response.status}')
                return

            json_data = str_to_json(response.text)
            # self.logger.info(f'json_data: {json_data}')

            # content
            resultSets_list = jsonpath.jsonpath(json_data, '$..data')
            # 页数取得
            current_page = response.meta['page']
            if resultSets_list[0] == None:
                self.logger.info(f'一共采集了{(current_page - 1)}页数据！！！！')
                return

            # 行业代码
            f12_list = jsonpath.jsonpath(json_data, '$..f12')
            # 行业名称
            f14_list = jsonpath.jsonpath(json_data, '$..f14')
            # 最新价
            f2_list = jsonpath.jsonpath(json_data, '$..f2')
            # 今日涨跌幅
            f3_list = jsonpath.jsonpath(json_data, '$..f3')
            # 今日主力净流入(净额)
            f62_list = jsonpath.jsonpath(json_data, '$..f62')
            # 今日主力净流入(净占比)
            f184_list = jsonpath.jsonpath(json_data, '$..f184')
            # 今日超大单净流入(净额)
            f66_list = jsonpath.jsonpath(json_data, '$..f66')
            # 今日超大单净流入(净占比)
            f69_list = jsonpath.jsonpath(json_data, '$..f69')
            # 今日大单净流入(净额)
            f72_list = jsonpath.jsonpath(json_data, '$..f72')
            # 今日大单净流入(净占比)
            f75_list = jsonpath.jsonpath(json_data, '$..f75')
            # 今日中单净流入(净额)
            f78_list = jsonpath.jsonpath(json_data, '$..f78')
            # 今日中单净流入(净占比)
            f81_list = jsonpath.jsonpath(json_data, '$..f81')
            # 今日小单净流入(净额)
            f84_list = jsonpath.jsonpath(json_data, '$..f84')
            # 今日小单净流入(净占比)
            f87_list = jsonpath.jsonpath(json_data, '$..f87')
            # 今日主力净流入(最大股名称)
            f204_list = jsonpath.jsonpath(json_data, '$..f204')
            # 今日主力净流入(最大股代码)
            f205_list = jsonpath.jsonpath(json_data, '$..f205')

            # 当日日期 yyyymmdd
            now_ymd = now_date()
            result_list = zip(f12_list, f14_list, f2_list, f3_list, f62_list, f184_list, f66_list, f69_list, f72_list,
                              f75_list, f78_list, f81_list, f84_list, f87_list, f204_list, f205_list)
            for item in result_list:
                # 今日主力净流入(净额) 小于 0 的数据不要
                # 例子：620811552.0
                #      76256208.0
                #      66343.0
                # if isinstance(item[4], float):
                #     if str_to_float(item[4]) < 0:
                #         continue
                zjlx_item = EastmoneyItem()
                # 行业代码
                zjlx_item["f12"] = item[0]
                # 行业名称
                zjlx_item["f14"] = item[1]
                # 最新价
                zjlx_item["f2"] = str(item[2]) + '元'
                # 今日涨跌幅
                zjlx_item["f3"] = str(item[3]) + '%'
                # 今日主力净流入(净额) amountUnitEdit 这里不需要转换，有画面来转换
                zjlx_item["f62"] = item[4]
                # 今日主力净流入(净占比)
                zjlx_item["f184"] = str(item[5]) + '%'
                # 今日超大单净流入(净额) amountUnitEdit 这里不需要转换，有画面来转换
                zjlx_item["f66"] = amountUnitEdit(item[6])
                # 今日超大单净流入(净占比)
                zjlx_item["f69"] = str(item[7]) + '%'
                # 今日大单净流入(净额) amountUnitEdit 这里不需要转换，有画面来转换
                zjlx_item["f72"] = amountUnitEdit(item[8])
                # 今日大单净流入(净占比)
                zjlx_item["f75"] = str(item[9]) + '%'
                # 今日中单净流入(净额) amountUnitEdit 这里不需要转换，有画面来转换
                zjlx_item["f78"] = amountUnitEdit(item[10])
                # 今日中单净流入(净占比)
                zjlx_item["f81"] = str(item[11]) + '%'
                # 今日小单净流入(净额) amountUnitEdit 这里不需要转换，有画面来转换
                zjlx_item["f84"] = amountUnitEdit(item[12])
                # 今日小单净流入(净占比)
                zjlx_item["f87"] = str(item[13]) + '%'
                # 今日主力净流入(最大股名称)
                zjlx_item["f204"] = item[14]
                # 今日主力净流入(最大股代码)
                zjlx_item["f205"] = item[15]
                # 数据采集日期
                zjlx_item["frq"] = now_ymd
                yield zjlx_item

            # 处理分页
            if current_page < self.max_pages:
                next_page = current_page + 1
                cb = generate_jquery_callback()
                url_base = f'https://push2.eastmoney.com/api/qt/clist/get?cb={cb}&fid=f62&po=1&pz=99&pn={next_page}&np=1&fltt=2&invt=2&ut=8dec03ba335b81bf4ebdf7b29ec27d15'
                concept_url = f'{url_base}&fs={self.new_fs}&fields={self.new_fields}'
                self.logger.info(f'concept_url: {concept_url} ')
                yield scrapy.Request(
                    url=concept_url,
                    method='GET',
                    callback=self.parse,
                    meta={'page': next_page}
                )
                # time.sleep(5)
        except Exception as ex:
            self.logger.error(f'解析错误: {str(ex)}')