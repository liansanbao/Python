import datetime
import json
import math
import random
import time

import jsonpath
import scrapy.http

from .eastmoneyTools import now_date, str_to_json, str_to_int, format_hms, str_to_float, timestamp_13, youzi, quote_str, \
    generate_jquery_callback, amountUnitEdit
from ..items import *

'''
涨停股 https://quote.eastmoney.com/ztb/?from=center
'''
class DailylimitCrawlSpider(scrapy.Spider):
    name = "dailylimit_crawl"
    allowed_domains = ["eastmoney.com"]
    # start_urls = ["https://eastmoney.com"]
    url_base = 'https://push2ex.eastmoney.com/getTopicZTPool?'
    # cb=callbackdata225352&ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt&Pageindex=0&pagesize=99&sort=fbt:asc&date=20250423&_=1745394877868
    # 1e7: 10000000

    # def start_requests(self):
    #     # 涨停主题和原因
    #     # https://fk.tdx.com.cn/TQLEX?Entry=CWServ.tdxsj_tzrl_gsrl
    #     # POST：{"Params":["zdtfx","ztfx","2025-07-10","0","2","20"]}
    #     #       {"Params":["zdtfx","ztfx","2025-07-10","1","1","20"]}
    #     #       {"Params":["zdtfx","ztfx","2025-07-10","0","3","20"]}
    #     #       {"Params":["zdtfx","ztfx","2025-07-10","0","4","20"]}
    #     sale_data = datetime.date.today().strftime('%Y-%m-%d')
    #     tdx_url = 'https://fk.tdx.com.cn/TQLEX?Entry=CWServ.tdxsj_tzrl_gsrl'
    #     data_str = json.dumps({"Params": ["zdtfx", "ztfx", "2025-07-10", "1", "1", "200"]})
    #     self.logger.info(f'tdx_url: {tdx_url} BODY: {data_str}')
    #     yield scrapy.Request(tdx_url, method='POST', callback=self.dailylimitTdx, body=data_str, headers={'Content-Type': 'application/json'})

    def start_requests(self):
        cb = f'callbackdata{math.floor(1e7 * random.random() + 1)}'
        timestamp = timestamp_13()
        # 当日日期 yyyymmdd
        now_ymd = now_date()
        url = f'{self.url_base}cb={cb}&ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt&Pageindex=0&pagesize=200&sort=fbt:asc&date={now_ymd}&_={timestamp}'
        # url = f'{self.url_base}cb={cb}&ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt&Pageindex=0&pagesize=200&sort=fbt:asc&date=20250710&_={timestamp}'
        self.logger.info(f'start_urls： {url}')
        yield scrapy.Request(url=url, callback=self.parse)

    def dailylimitTdx(self, response):
        json_data = response.json()
        # content
        resultSets_list = jsonpath.jsonpath(json_data, '$..ResultSets')
        report_dict = {}
        for item in resultSets_list:
            if item[0]['Count'] >= 20:
                content_list = item[0]['Content']
                for content in content_list:
                    # 股票名称包含ST开头的不要
                    if str(content[7]).find('ST') != -1:
                        continue
                    report_dict[content[6]] = [content[1], content[2], content[5]]
                # 其它暂时不处理
                break
        self.logger.info(f'涨停数据件数: {len(report_dict)}')

    def parse(self, response):
        # self.logger.info(f'response data： {response.text}')
        json_data = str_to_json(response.text)
        # 股票代码
        f12_list = jsonpath.jsonpath(json_data, '$..c')
        if f12_list != None and len(f12_list) == 0:
            return
        # 股票名称
        f14_list = jsonpath.jsonpath(json_data, '$..n')
        # 最新价
        f2_list = jsonpath.jsonpath(json_data, '$..p')
        # 涨跌幅
        f3_list = jsonpath.jsonpath(json_data, '$..zdp')
        # 成交额 amount
        f62_list = jsonpath.jsonpath(json_data, '$..amount')
        # 流通市值 ltsz
        f184_list = jsonpath.jsonpath(json_data, '$..ltsz')
        # 总市值 tshare
        f66_list = jsonpath.jsonpath(json_data, '$..tshare')
        # 换手率 hs
        f69_list = jsonpath.jsonpath(json_data, '$..hs')
        # 封板资金 fund
        f72_list = jsonpath.jsonpath(json_data, '$..fund')
        # 首次封板时间 fbt
        f75_list = jsonpath.jsonpath(json_data, '$..fbt')
        # 最后封板时间 lbt
        f78_list = jsonpath.jsonpath(json_data, '$..lbt')
        # 炸板次数 zbc
        f81_list = jsonpath.jsonpath(json_data, '$..zbc')
        # 涨停统计 zttj{days, ct }
        f84_ct_list = jsonpath.jsonpath(json_data, '$..zttj.ct')
        f84_days_list = jsonpath.jsonpath(json_data, '$..zttj.days')
        # 连板数 lbc
        f87_list = jsonpath.jsonpath(json_data, '$..lbc')
        # 所属行业 hybk
        hybk_list = jsonpath.jsonpath(json_data, '$..hybk')

        # 当日日期 yyyymmdd
        now_ymd = now_date()
        result_list = zip(f12_list, f14_list, f2_list, f3_list, f62_list, f184_list, f66_list, f69_list, f72_list,
                          f75_list, f78_list, f81_list, f84_ct_list, f84_days_list, f87_list, hybk_list)

        for item in result_list:

            # 股票名称包含ST开头的不要
            f14 = item[1]
            if str(f14).find('ST') != -1:
                continue

            # 最新价大于25且小于4的不要,
            f2 = int(round(str_to_int(item[2]) / 1000, 2))
            # if f2 < 4 or f2 > 25:
            #     continue

            # 流通市值大于100亿不要
            f184 = int(round(str_to_float(item[5]) / 100000000, 2))
            # if f184 > 100:
            #     continue

            # 非首板的不要
            # if str_to_int(item[14]) != 1:
            #     continue

            zjlx_item = EastmoneyItem()
            # 股票代码
            zjlx_item["f12"] = item[0]
            # 股票名称
            zjlx_item["f14"] = f14
            # 最新价
            zjlx_item["f2"] = f'{round(str_to_int(item[2]) / 1000, 2):.2f}'
            # 涨跌幅
            zjlx_item["f3"] = f'{round(str_to_float(item[3]), 2):.2f}'
            # 成交额
            zjlx_item["f62"] = f'{round(str_to_float(item[4]) / 100000000, 2):.2f}'
            # 流通市值
            zjlx_item["f184"] = f'{round(str_to_float(item[5]) / 100000000, 2):.2f}'
            # 总市值
            zjlx_item["f66"] = f'{round(str_to_float(item[6]) / 100000000, 2):.2f}'
            # 换手率
            zjlx_item["f69"] = f'{round(str_to_float(item[7]), 2):.2f}'
            # 封板资金
            # zjlx_item["f72"] = f'{round(str_to_int(item[8])/10000, 2)}'
            zjlx_item["f72"] = amountUnitEdit(item[8])
            # 首次封板时间
            zjlx_item["f75"] = format_hms(str(item[9]))
            # 最后封板时间
            zjlx_item["f78"] = format_hms(str(item[10]))
            # 炸板次数
            zjlx_item["f81"] = item[11]
            # 涨停统计
            zjlx_item["f84"] = f'{item[12]}/{item[13]}'
            # 连板数
            zjlx_item["f87"] = str_to_int(item[14])
            # 所属行业
            zjlx_item["hybk"] = str(item[15])
            # 数据采集日期
            zjlx_item["frq"] = now_ymd
            # 游资['有','无']
            zjlx_item["youzi"] = youzi(str(item[0]), now_ymd)

            # 可视化报告
            # https://datacenter-web.eastmoney.com/api/data/v1/get?callback=jQuery11230754165697973015_1754114319910&reportName=RPT_F10_EH_FREEHOLDERS&columns=F10_FREEHOLDERS&quoteColumns=&filter=(SECURITY_CODE%3D%22002811%22)&pageNumber=1&pageSize=1&sortTypes=-1%2C1&sortColumns=END_DATE%2CHOLDER_RANK&source=WEB&client=WEB&_=1754114319911
            # https://datacenter-web.eastmoney.com/api/data/v1/get?callback=jQuery435053236685462532865_1754122000397&reportName=RPT_F10_EH_FREEHOLDERS&columns=F10_FREEHOLDERS&quoteColumns=&filter=(SECURITY_CODE603283)&pageNumber=1&pageSize=1&sortTypes=-1%2C1&sortColumns=END_DATE%2CHOLDER_RANK&source=WEB&client=WEB&_=1754122000397
            # https://datacenter-web.eastmoney.com/api/data/v1/get?callback=jQuery41135492698020537905_1754121450513&reportName=RPT_F10_EH_FREEHOLDERS&columns=F10_FREEHOLDERS&quoteColumns=&filter=(SECURITY_CODE603060)&pageNumber=1&pageSize=1&sortTypes=-1%2C1&sortColumns=END_DATE%2CHOLDER_RANK&source=WEB&client=WEB&_=1754121450513
            reportBaseUrl = 'https://datacenter-web.eastmoney.com/api/data/v1/get'
            # ="002811"
            filter = quote_str(f'="{zjlx_item["f12"]}"')
            callback = generate_jquery_callback()
            ts = timestamp_13()
            reportUrl = f'{reportBaseUrl}?callback={callback}&reportName=RPT_F10_EH_FREEHOLDERS&columns=F10_FREEHOLDERS&quoteColumns=&filter=(SECURITY_CODE{filter})&pageNumber=1&pageSize=1&sortTypes=-1%2C1&sortColumns=END_DATE%2CHOLDER_RANK&source=WEB&client=WEB&_={ts}'
            # self.logger.info(f'{p_item["f12"]}可视化数据取得: {reportUrl}')

            yield scrapy.Request(url=reportUrl, meta={'ms_item': zjlx_item}, callback=self.parseReportChart)
            # 暂停1秒
            time.sleep(1)

    # 可视化数据采集
    def parseReportChart(self, response):
        json_data = str_to_json(response.text)
        # json_data = str_to_json('jQuery11230754165697973015_1754114319910({"version":null,"result":null,"success":false,"message":"返回数据为空","code":9201});')
        # jQuery11230754165697973015_1754114319910({"version":"e548239c76f290a96bc99d3301fad08d","result":{"pages":360,"data":[{"SECUCODE":"002811.SZ","SECURITY_CODE":"002811","SECURITY_NAME_ABBR":"郑中设计","END_DATE":"2025-03-31 00:00:00","REPORT_DATE_NAME":"2025一季报","HOLDER_RANK":1,"HOLDER_CODE":"10398124","HOLDER_NAME":"深圳市亚泰一兆投资有限公司","HOLDER_TYPE":"投资公司","HOLD_NUM":141961723,"HOLD_RATIO":46.3087,"FREE_HOLDNUM_RATIO":50.394280226319,"HOLD_CHANGE":"不变","HOLD_RATIO_CHANGE":-5.5632,"SHARES_TYPE":"A股","UPDATE_DATE":"2025-04-29 00:00:00","LISTING_STATE":"0"}],"count":360},"success":true,"message":"ok","code":0});
        # jQuery11230754165697973015_1754114319910({"version":null,"result":null,"success":false,"message":"返回数据为空","code":9201});
        p_item = response.meta.get('ms_item')
        result = jsonpath.jsonpath(json_data, '$..result')
        # print(f'result: {result[0]}')
        if result[0]:
            # 可视化报告Code
            secucode_list = jsonpath.jsonpath(json_data, '$..SECUCODE')
            p_item['secucode'] = secucode_list[0]
            # print(f'secucode_list[0]: {secucode_list[0]}')
            # 可视化报告日期
            endData_list = jsonpath.jsonpath(json_data, '$..END_DATE')
            p_item['endData'] = str(endData_list[0]).split(' ')[0]
        else:
            p_item['secucode'] = ''
            p_item['endData'] = ''

        # print(f'endData_list[0]: {p_item["endData"]}')
        yield p_item