import json

import jsonpath
import scrapy
import time
from scrapy.utils.project import get_project_settings

from .eastmoneyTools import generate_jquery_callback, quote_str, unquote_str, str_to_json, now_date, timestamp_13, \
    str_to_int
from ..items import EastmoneyItem


# 主力排名数据采集 https://data.eastmoney.com/zjlx/list.html
class MainstockCrawlSpider(scrapy.Spider):
    name = "mainStock_crawl"
    allowed_domains = ["eastmoney.com"]
    # https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery112304787468521821988_1752042924826&fid=f184&po=1&pz=50&pn=1&np=1&fltt=2&invt=2&fields=f2%2Cf3%2Cf12%2Cf13%2Cf14%2Cf62%2Cf184%2Cf225%2Cf165%2Cf263%2Cf109%2Cf175%2Cf264%2Cf160%2Cf100%2Cf124%2Cf265%2Cf1&ut=8dec03ba335b81bf4ebdf7b29ec27d15&fs=m%3A0%2Bt%3A6%2Bf%3A!2%2Cm%3A0%2Bt%3A13%2Bf%3A!2%2Cm%3A0%2Bt%3A80%2Bf%3A!2%2Cm%3A1%2Bt%3A2%2Bf%3A!2%2Cm%3A1%2Bt%3A23%2Bf%3A!2%2Cm%3A0%2Bt%3A7%2Bf%3A!2%2Cm%3A1%2Bt%3A3%2Bf%3A!2
    url_base = 'https://push2.eastmoney.com/api/qt/clist/get'
    cb = generate_jquery_callback()
    fields = 'f2%2Cf3%2Cf12%2Cf13%2Cf14%2Cf62%2Cf184%2Cf225%2Cf165%2Cf263%2Cf109%2Cf175%2Cf264%2Cf160%2Cf100%2Cf124%2Cf265%2Cf1'
    fs = 'm%3A0%2Bt%3A6%2Bf%3A!2%2Cm%3A0%2Bt%3A13%2Bf%3A!2%2Cm%3A0%2Bt%3A80%2Bf%3A!2%2Cm%3A1%2Bt%3A2%2Bf%3A!2%2Cm%3A1%2Bt%3A23%2Bf%3A!2%2Cm%3A0%2Bt%3A7%2Bf%3A!2%2Cm%3A1%2Bt%3A3%2Bf%3A!2'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 配置文件settings.py内容取得
        self.settings = get_project_settings()

    def start_requests(self):
        new_fs = quote_str(unquote_str(self.fs))
        new_fields = quote_str(unquote_str(self.fields))
        # 爬取指定页数的数据
        for pageNo in range(0, self.settings.get('MAINSTOCK_PN')):
            url = f"{self.url_base}?cb={self.cb}&fid=f184&po=1&pz={self.settings.get('MAINSTOCK_PZ')}&pn={pageNo + 1}&np=1&fltt=2&invt=2&fs={new_fs}&fields={new_fields}"
            # self.logger.info(f'start_urls： {url}')
            yield scrapy.Request(url=url, callback=self.parse)
            time.sleep(2)

    # 主力排名数据采集
    def parse(self, response):
        json_data = str_to_json(response.text)
        # self.logger.info(f'json_data: {json_data}')

        # 股票代码
        f12_list = jsonpath.jsonpath(json_data, '$..f12')
        # 股票名称
        f14_list = jsonpath.jsonpath(json_data, '$..f14')
        # 最新价
        f2_list = jsonpath.jsonpath(json_data, '$..f2')

        # 今日净占比
        f184_list = jsonpath.jsonpath(json_data, '$..f184')
        # 今日排名
        f225_list = jsonpath.jsonpath(json_data, '$..f225')
        # 今日涨跌
        f3_list = jsonpath.jsonpath(json_data, '$..f3')

        # 5日净占比
        f165_list = jsonpath.jsonpath(json_data, '$..f165')
        # 5日排名
        f263_list = jsonpath.jsonpath(json_data, '$..f263')
        # 5日涨跌
        f109_list = jsonpath.jsonpath(json_data, '$..f109')

        # 10日净占比
        f175_list = jsonpath.jsonpath(json_data, '$..f175')
        # 10日排名
        f264_list = jsonpath.jsonpath(json_data, '$..f264')
        # 10日涨跌
        f160_list = jsonpath.jsonpath(json_data, '$..f160')

        # 所属板块ID
        f265_list = jsonpath.jsonpath(json_data, '$..f265')
        # 所属板块名称
        f100_list = jsonpath.jsonpath(json_data, '$..f100')

        # 详情URL
        detail_url = 'https://push2.eastmoney.com/api/qt/stock/get'
        fields = 'f58%2Cf734%2Cf107%2Cf57%2Cf43%2Cf59%2Cf169%2Cf301%2Cf60%2Cf170%2Cf152%2Cf177%2Cf111%2Cf46%2Cf44%2Cf45%2Cf47%2Cf260%2Cf48%2Cf261%2Cf279%2Cf277%2Cf278%2Cf288%2Cf19%2Cf17%2Cf531%2Cf15%2Cf13%2Cf11%2Cf20%2Cf18%2Cf16%2Cf14%2Cf12%2Cf39%2Cf37%2Cf35%2Cf33%2Cf31%2Cf40%2Cf38%2Cf36%2Cf34%2Cf32%2Cf211%2Cf212%2Cf213%2Cf214%2Cf215%2Cf210%2Cf209%2Cf208%2Cf207%2Cf206%2Cf161%2Cf49%2Cf171%2Cf50%2Cf86%2Cf84%2Cf85%2Cf168%2Cf108%2Cf116%2Cf167%2Cf164%2Cf162%2Cf163%2Cf92%2Cf71%2Cf117%2Cf292%2Cf51%2Cf52%2Cf191%2Cf192%2Cf262%2Cf294%2Cf295%2Cf269%2Cf270%2Cf256%2Cf257%2Cf285%2Cf286%2Cf748%2Cf747'
        wbp2u = '%7C0%7C0%7C0%7Cweb'

        # 当日日期 yyyymmdd
        now_ymd = now_date()
        result_list = zip(f12_list, f14_list, f2_list, f184_list, f225_list, f3_list, f165_list, f263_list, f109_list, f175_list, f264_list, f160_list, f265_list, f100_list)
        for item in result_list:
            # 股票名称包含ST开头的不要
            f14 = item[1]
            if str(f14).find('ST') != -1:
                self.logger.info(f'{now_ymd}：{item[4]} 股票名称: {f14}')
                continue

            # 涨跌幅小于 配置文件设定的值 不要
            f3 = item[5]
            if f3 < self.settings.get('MAINSTOCK_ZF'):
                self.logger.info(f'{now_ymd}：{item[4]} {f14} 涨跌幅: {f3}')
                continue

            # 价格小于 配置文件设定的值 不要
            f2 = item[2]
            if f2 < self.settings.get('MAINSTOCK_JJ'):
                self.logger.info(f'{now_ymd}：{item[4]} {f14} 价格: {f2}')
                continue

            mainStock_item = EastmoneyItem()
            # 股票代码
            mainStock_item["f12"] = item[0]
            # 股票名称
            mainStock_item["f14"] = item[1]
            # 最新价
            mainStock_item["f2"] = item[2]

            # 今日净占比
            mainStock_item["f184"] = str(item[3])
            # 今日排名
            mainStock_item["f225"] = str(item[4])
            # 今日涨跌
            mainStock_item["f3"] = str(item[5])

            # 5日净占比
            mainStock_item["f165"] = str(item[6])
            # 5日排名
            mainStock_item["f263"] = str(item[7])
            # 5日涨跌
            mainStock_item["f109"] = str(item[8])

            # 10日净占比
            mainStock_item["f175"] = str(item[9])
            # 10日排名
            mainStock_item["f264"] = str(item[10])
            # 10日涨跌
            mainStock_item["f160"] = str(item[11])

            # 所属板块ID
            mainStock_item["f265"] = str(item[12])
            # 所属板块名称
            mainStock_item["f100"] = str(item[13])
            # 数据采集日期
            mainStock_item["frq"] = now_ymd

            # 行情数据
            # https://push2.eastmoney.com/api/qt/stock/get?invt=2&fltt=1&cb=jQuery35107855404136478429_1752054266443&fields=f58%2Cf734%2Cf107%2Cf57%2Cf43%2Cf59%2Cf169%2Cf301%2Cf60%2Cf170%2Cf152%2Cf177%2Cf111%2Cf46%2Cf44%2Cf45%2Cf47%2Cf260%2Cf48%2Cf261%2Cf279%2Cf277%2Cf278%2Cf288%2Cf19%2Cf17%2Cf531%2Cf15%2Cf13%2Cf11%2Cf20%2Cf18%2Cf16%2Cf14%2Cf12%2Cf39%2Cf37%2Cf35%2Cf33%2Cf31%2Cf40%2Cf38%2Cf36%2Cf34%2Cf32%2Cf211%2Cf212%2Cf213%2Cf214%2Cf215%2Cf210%2Cf209%2Cf208%2Cf207%2Cf206%2Cf161%2Cf49%2Cf171%2Cf50%2Cf86%2Cf84%2Cf85%2Cf168%2Cf108%2Cf116%2Cf167%2Cf164%2Cf162%2Cf163%2Cf92%2Cf71%2Cf117%2Cf292%2Cf51%2Cf52%2Cf191%2Cf192%2Cf262%2Cf294%2Cf295%2Cf269%2Cf270%2Cf256%2Cf257%2Cf285%2Cf286%2Cf748%2Cf747&secid=0.001203&ut=fa5fd1943c7b386f172d6893dbfba10b&wbp2u=%7C0%7C0%7C0%7Cweb&dect=1&_=1752054266444
            cb = generate_jquery_callback()
            ts = timestamp_13()
            secid = f"1.{item[0]}" if str(item[0]).startswith('6') else f"0.{item[0]}"
            detailUrl = f'{detail_url}?cb={cb}&fltt=1&invt=2&secid={secid}&fields={fields}&ut=b2884a393a59ad64002292a3e90d46a5&wbp2u={wbp2u}&dect=1&_={ts}'
            # self.logger.info(f'{item[0]}.detailUrl: {detailUrl}')
            yield scrapy.Request(url=detailUrl, meta={'ms_item': mainStock_item}, callback=self.parseMarket)
            # 暂停1秒
            # time.sleep(1)

    # 行情数据采集
    def parseMarket(self, response):
        json_data = str_to_json(response.text)
        p_item = response.meta.get('ms_item')
        # 量比
        f50_list = jsonpath.jsonpath(json_data, '$..f50')
        p_item["f50"] = str(str_to_int(f50_list[0])/100)
        # 换手
        f168_list = jsonpath.jsonpath(json_data, '$..f168')
        p_item["f168"] = str(str_to_int(f168_list[0])/100)
        # print(f'parseDetail 量比: {int(f50_list[0])/100}%')
        # print(f'parseDetail 换手: {int(f168_list[0])/100}%')

        # 可视化报告
        # https://datacenter-web.eastmoney.com/api/data/v1/get?callback=jQuery11230754165697973015_1754114319910&reportName=RPT_F10_EH_FREEHOLDERS&columns=F10_FREEHOLDERS&quoteColumns=&filter=(SECURITY_CODE%3D%22002811%22)&pageNumber=1&pageSize=1&sortTypes=-1%2C1&sortColumns=END_DATE%2CHOLDER_RANK&source=WEB&client=WEB&_=1754114319911
        # https://datacenter-web.eastmoney.com/api/data/v1/get?callback=jQuery435053236685462532865_1754122000397&reportName=RPT_F10_EH_FREEHOLDERS&columns=F10_FREEHOLDERS&quoteColumns=&filter=(SECURITY_CODE603283)&pageNumber=1&pageSize=1&sortTypes=-1%2C1&sortColumns=END_DATE%2CHOLDER_RANK&source=WEB&client=WEB&_=1754122000397
        # https://datacenter-web.eastmoney.com/api/data/v1/get?callback=jQuery41135492698020537905_1754121450513&reportName=RPT_F10_EH_FREEHOLDERS&columns=F10_FREEHOLDERS&quoteColumns=&filter=(SECURITY_CODE603060)&pageNumber=1&pageSize=1&sortTypes=-1%2C1&sortColumns=END_DATE%2CHOLDER_RANK&source=WEB&client=WEB&_=1754121450513
        reportBaseUrl = 'https://datacenter-web.eastmoney.com/api/data/v1/get'
        # ="002811"
        filter = quote_str(f'="{p_item["f12"]}"')
        callback = generate_jquery_callback()
        ts = timestamp_13()
        reportUrl = f'{reportBaseUrl}?callback={callback}&reportName=RPT_F10_EH_FREEHOLDERS&columns=F10_FREEHOLDERS&quoteColumns=&filter=(SECURITY_CODE{filter})&pageNumber=1&pageSize=1&sortTypes=-1%2C1&sortColumns=END_DATE%2CHOLDER_RANK&source=WEB&client=WEB&_={ts}'
        # self.logger.info(f'{p_item["f12"]}可视化数据取得: {reportUrl}')

        yield scrapy.Request(url=reportUrl, meta={'ms_item': p_item}, callback=self.parseReportChart)
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
        filter = f'SECURITY_CODE%3D%22{p_item["f12"]}%22'
        new_filter = quote_str(unquote_str(filter))
        ts = timestamp_13()
        depthData_url = f'{depthData_base}?callback={callback}&reportName=RPT_F10_CORETHEME_CONTENT&columns={new_columns}&sortColumns={new_sortColumns}&sortTypes={new_sortTypes}' \
                        f'&source=WEB&client=WEB&filter=({new_filter})&_={ts}'
        # self.logger.info(f'{zjlx_item["f12"]}.深度数据_url: {depthData_url}')
        yield scrapy.Request(url=depthData_url, meta={'p_item': p_item}, callback=self.parseDepthData)

    # 深度数据采集
    def parseDepthData(self, response):
        zjlx_item = response.meta.get('p_item')
        json_data = str_to_json(response.text)
        depthData_list = jsonpath.jsonpath(json_data, '$..data')
        # 深度数据
        zjlx_item["depthData"] = json.dumps(depthData_list[0], ensure_ascii=False)
        # print(f'zjlx_item["depthData"]: {zjlx_item["depthData"]}')
        yield zjlx_item