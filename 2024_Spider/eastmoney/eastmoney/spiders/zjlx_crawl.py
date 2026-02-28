import json

import jsonpath
from .eastmoneyTools import unquote_str, quote_str, str_to_json, str_to_int, now_date, timestamp_13, \
    generate_jquery_callback
from ..items import *
import time

# 个股资金流数据抓取
class ZjlxCrawlSpider(scrapy.Spider):
    name = "zjlx_crawl"
    allowed_domains = ["eastmoney.com"]
    # start_urls = ["https://eastmoney.com"] jQuery1123043008257659373306_1745 4178 05257
    # https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery11230014427733526856668_1751899518576&fid=f62&po=1&pz=50&pn=1&np=1&fltt=2&invt=2&ut=8dec03ba335b81bf4ebdf7b29ec27d15&fs=m%3A0%2Bt%3A6%2Bf%3A!2%2Cm%3A0%2Bt%3A13%2Bf%3A!2%2Cm%3A0%2Bt%3A80%2Bf%3A!2%2Cm%3A1%2Bt%3A2%2Bf%3A!2%2Cm%3A1%2Bt%3A23%2Bf%3A!2%2Cm%3A0%2Bt%3A7%2Bf%3A!2%2Cm%3A1%2Bt%3A3%2Bf%3A!2&fields=f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13
    cb = generate_jquery_callback()
    cb_str = f'cb={cb}&fid=f62&po=1&pz=99&pn=1&np=1&fltt=2&invt=2&ut=8dec03ba335b81bf4ebdf7b29ec27d15'
    url_base = f'https://push2.eastmoney.com/api/qt/clist/get'
    fs = 'm%3A0%2Bt%3A6%2Bf%3A!2%2Cm%3A0%2Bt%3A13%2Bf%3A!2%2Cm%3A0%2Bt%3A80%2Bf%3A!2%2Cm%3A1%2Bt%3A2%2Bf%3A!2%2Cm%3A1%2Bt%3A23%2Bf%3A!2%2Cm%3A0%2Bt%3A7%2Bf%3A!2%2Cm%3A1%2Bt%3A3%2Bf%3A!2'
    fields = 'f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13'
    detail_fields = 'f58%2Cf734%2Cf107%2Cf57%2Cf43%2Cf59%2Cf169%2Cf301%2Cf60%2Cf170%2Cf152%2Cf177%2Cf111%2Cf46%2Cf44%2Cf45%2Cf47%2Cf260%2Cf48%2Cf261%2Cf279%2Cf277%2Cf278%2Cf288%2Cf19%2Cf17%2Cf531%2Cf15%2Cf13%2Cf11%2Cf20%2Cf18%2Cf16%2Cf14%2Cf12%2Cf39%2Cf37%2Cf35%2Cf33%2Cf31%2Cf40%2Cf38%2Cf36%2Cf34%2Cf32%2Cf211%2Cf212%2Cf213%2Cf214%2Cf215%2Cf210%2Cf209%2Cf208%2Cf207%2Cf206%2Cf161%2Cf49%2Cf171%2Cf50%2Cf86%2Cf84%2Cf85%2Cf168%2Cf108%2Cf116%2Cf167%2Cf164%2Cf162%2Cf163%2Cf92%2Cf71%2Cf117%2Cf292%2Cf51%2Cf52%2Cf191%2Cf192%2Cf262%2Cf294%2Cf295%2Cf269%2Cf270%2Cf256%2Cf257%2Cf285%2Cf286%2Cf748%2Cf747'
    new_detail_fields = quote_str(unquote_str(detail_fields))

    # 爬虫结束输出统计信息
    def close(spider, reason):
        for item in spider.depthDataResult:
            spider.logger.info(f'深度数据: {spider.depthDataResult[item]}')

    def start_requests(self):
        self.depthDataResult = {}
        new_fs = quote_str(unquote_str(self.fs))
        new_fields = quote_str(unquote_str(self.fields))

        url = f'{self.url_base}?{self.cb_str}&fs={new_fs}&fields={new_fields}'
        # self.logger.info(f'start_urls： {url}')
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # self.logger.info(f'parse data： {response.text}')
        stock_baseUrl = 'https://push2.eastmoney.com/api/qt/stock/get'
        json_data = str_to_json(response.text)

        # 股票代码
        f12_list = jsonpath.jsonpath(json_data, '$..f12')
        # 股票名称
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

        # 当日日期 yyyymmdd
        now_ymd = now_date()
        result_list = zip(f12_list, f14_list, f2_list, f3_list, f62_list, f184_list, f66_list, f69_list, f72_list, f75_list, f78_list, f81_list, f84_list, f87_list)
        for item in result_list:
            # 股票名称包含ST开头的不要
            f14 = item[1]
            if str(f14).find('ST') != -1:
                continue

            # # 大于 25 小于 5 不要
            # if item[2] > 25 or item[2] < 5:
            #     continue
            # 涨跌幅小于 5 不要
            if item[3] < 5:
                continue

            zjlx_item = EastmoneyItem()
            # 股票代码
            zjlx_item["f12"] = item[0]
            # 股票名称
            zjlx_item["f14"] = item[1]
            # 最新价
            zjlx_item["f2"] = item[2]
            # 今日涨跌幅
            zjlx_item["f3"] = item[3]
            # 今日主力净流入(净额)
            zjlx_item["f62"] = f'{round(str_to_int(item[4]) / 100000000, 2):.2f}'
            # 今日主力净流入(净占比)
            zjlx_item["f184"] = str(item[5])
            # 今日超大单净流入(净额)
            zjlx_item["f66"] = f'{round(str_to_int(item[6]) / 100000000, 2):.2f}'
            # 今日超大单净流入(净占比)
            zjlx_item["f69"] = str(item[7])
            # 今日大单净流入(净额)
            zjlx_item["f72"] = f'{round(str_to_int(item[8]) / 100000000, 2):.2f}'
            # 今日大单净流入(净占比)
            zjlx_item["f75"] = str(item[9])
            # 今日中单净流入(净额)
            zjlx_item["f78"] = f'{round(str_to_int(item[10]) / 100000000, 2):.2f}'
            # 今日中单净流入(净占比)
            zjlx_item["f81"] = str(item[11])
            # 今日小单净流入(净额)
            zjlx_item["f84"] = f'{round(str_to_int(item[12]) / 100000000, 2):.2f}'
            # 今日小单净流入(净占比)
            zjlx_item["f87"] = str(item[13])
            # 数据采集日期
            zjlx_item["frq"] = now_ymd
            # 行情数据
            # https://push2.eastmoney.com/api/qt/stock/get?invt=2&fltt=1&cb=jQuery35100035493805669187806_1752237750538
            # &fields=f58%2Cf734%2Cf107%2Cf57%2Cf43%2Cf59%2Cf169%2Cf301%2Cf60%2Cf170%2Cf152%2Cf177%2Cf111%2Cf46%2Cf44%2Cf45%2Cf47%2Cf260%2Cf48%2Cf261%2Cf279%2Cf277%2Cf278%2Cf288%2Cf19%2Cf17%2Cf531%2Cf15%2Cf13%2Cf11%2Cf20%2Cf18%2Cf16%2Cf14%2Cf12%2Cf39%2Cf37%2Cf35%2Cf33%2Cf31%2Cf40%2Cf38%2Cf36%2Cf34%2Cf32%2Cf211%2Cf212%2Cf213%2Cf214%2Cf215%2Cf210%2Cf209%2Cf208%2Cf207%2Cf206%2Cf161%2Cf49%2Cf171%2Cf50%2Cf86%2Cf84%2Cf85%2Cf168%2Cf108%2Cf116%2Cf167%2Cf164%2Cf162%2Cf163%2Cf92%2Cf71%2Cf117%2Cf292%2Cf51%2Cf52%2Cf191%2Cf192%2Cf262%2Cf294%2Cf295%2Cf269%2Cf270%2Cf256%2Cf257%2Cf285%2Cf286%2Cf748%2Cf747
            # &secid=0.300059
            # &ut=fa5fd1943c7b386f172d6893dbfba10b&wbp2u=%7C0%7C0%7C0%7Cweb&dect=1&_=1752237750539
            cb = generate_jquery_callback()
            ts = timestamp_13()
            secid = f"1.{item[0]}" if str(item[0]).startswith('6') else f"0.{item[0]}"
            detailUrl = f'{stock_baseUrl}?cb={cb}&fltt=1&invt=2&secid={secid}&fields={self.new_detail_fields}&ut=fa5fd1943c7b386f172d6893dbfba10b&wbp2u=%7C0%7C0%7C0%7Cweb&dect=1&_={ts}'
            # self.logger.info(f'{item[0]}.详情_Url: {detailUrl}')
            yield scrapy.Request(url=detailUrl, meta={'p_item': zjlx_item}, callback=self.parseDetail)
            # 暂停1秒
            time.sleep(1)
            # break

    def parseDetail(self, response):
        zjlx_item = response.meta.get('p_item')
        json_data = str_to_json(response.text)
        # print(f'{zjlx_item["f12"]}_parseDetail json_data: {json_data}')
        # 量比
        f50_list = jsonpath.jsonpath(json_data, '$..f50')
        zjlx_item["f50"] = str(str_to_int(f50_list[0]) / 100)
        # 换手
        f168_list = jsonpath.jsonpath(json_data, '$..f168')
        zjlx_item["f168"] = str(str_to_int(f168_list[0]) / 100)

        # 深度数据采集
        # https://datacenter-web.eastmoney.com/api/data/v1/get?callback=jQuery112302766616683370249_1751982259257&reportName=RPT_F10_CORETHEME_CONTENT&columns=SECUCODE%2CSECURITY_CODE%2CMAINPOINT%2CMAINPOINT_CONTENT%2CKEY_CLASSIF%2CKEY_CLASSIF_CODE%2CMAINPOINT_NUM%2CKEYWORD&sortColumns=KEY_CLASSIF_CODE%2CMAINPOINT_RANK&sortTypes=1%2C1&source=WEB&client=WEB&filter=(SECURITY_CODE%3D%22601003%22)&_=1751982259258
        depthData_base = 'https://datacenter-web.eastmoney.com/api/data/v1/get'
        callback = generate_jquery_callback()
        columns = 'SECUCODE%2CSECURITY_CODE%2CMAINPOINT%2CMAINPOINT_CONTENT%2CKEY_CLASSIF%2CKEY_CLASSIF_CODE%2CMAINPOINT_NUM%2CKEYWORD'
        new_columns = quote_str(unquote_str(columns))
        sortColumns = 'KEY_CLASSIF_CODE%2CMAINPOINT_RANK'
        new_sortColumns = quote_str(unquote_str(sortColumns))
        sortTypes = '1%2C1'
        new_sortTypes = quote_str(unquote_str(sortTypes))
        filter = f'SECURITY_CODE%3D%22{zjlx_item["f12"]}%22'
        new_filter = quote_str(unquote_str(filter))
        ts = timestamp_13()
        depthData_url = f'{depthData_base}?callback={callback}&reportName=RPT_F10_CORETHEME_CONTENT&columns={new_columns}&sortColumns={new_sortColumns}&sortTypes={new_sortTypes}' \
                        f'&source=WEB&client=WEB&filter=({new_filter})&_={ts}'
        # self.logger.info(f'{zjlx_item["f12"]}.深度数据_url: {depthData_url}')
        yield scrapy.Request(url=depthData_url, meta={'p_item': zjlx_item}, callback=self.parseDepthData)
        # 暂停1秒
        time.sleep(1)

    def parseDepthData(self, response):
        zjlx_item = response.meta.get('p_item')
        json_data = str_to_json(response.text)
        depthData_list = jsonpath.jsonpath(json_data, '$..data')
        # 深度数据
        zjlx_item["depthData"] = json.dumps(depthData_list[0], ensure_ascii=False)
        for item in depthData_list[0]:
            # 关键字
            keyword = str(item['KEY_CLASSIF']).strip()
            # 所属板块
            if keyword == '所属板块':
                zjlx_item["hybk"] = str(item["MAINPOINT_CONTENT"]).split(" ")[0]
                # print(f'{item["SECURITY_CODE"]}_{item["KEY_CLASSIF"]}: {str(item["MAINPOINT_CONTENT"]).split(" ")}')

            if not keyword in self.depthDataResult.keys():
                self.depthDataResult[keyword] = [f'{item["MAINPOINT"]}_{item["KEY_CLASSIF"]}']

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