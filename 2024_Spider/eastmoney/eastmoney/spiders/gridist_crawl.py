import json
import time

import jsonpath
from scrapy.utils.project import get_project_settings
from .eastmoneyTools import now_date, generate_jquery_callback, timestamp_13, unquote_str, quote_str, str_to_json, \
    str_to_int, amountUnitEdit, str_to_float
from ..items import *

# https://quote.eastmoney.com/center/gridlist.html#hs_a_board
# 采集涨幅 大于 %4 的数据
class GridistCrawlSpider(scrapy.Spider):
    name = "gridist_crawl"
    allowed_domains = ["eastmoney.com"]
    # start_urls = ["https://eastmoney.com"]
    custom_settings = {
        'DOWNLOAD_DELAY': 1,  # 替代time.sleep
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'RETRY_TIMES': 3
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 今日日期
        self.endDate = now_date()
        # self.logger.info(f'self.userInfoDect: {self.userInfoDect.keys()}')
        self.settings = get_project_settings()
        self.base_url = 'https://push2.eastmoney.com/api/qt/clist/get'
        self.max_pages = 500  # 最大页数限制
        self.fields = quote_str(unquote_str(
            'f12%2Cf13%2Cf14%2Cf1%2Cf2%2Cf4%2Cf3%2Cf152%2Cf5%2Cf6%2Cf7%2Cf15%2Cf18%2Cf16%2Cf17%2Cf10%2Cf8%2Cf9%2Cf23'))
        self.fs = quote_str(
            unquote_str('m%3A0%2Bt%3A6%2Cm%3A0%2Bt%3A80%2Cm%3A1%2Bt%3A2%2Cm%3A1%2Bt%3A23%2Cm%3A0%2Bt%3A81%2Bs%3A2048'))
        # 行业板块存储, 减少访问服务器的负担
        self.gridistHybkDict = self.read_existing_json()  # 加载已有的行业板块

    # 读取已有的行业板块
    def read_existing_json(self):
        # 读取hybk.json文件中所有信息
        result = {}
        try:
            jsonPath = self.settings.get('OUTPUT_FILE_PATH')
            self.gridistJsonFile = f'{jsonPath}hybk.json'
            with open(self.gridistJsonFile, 'r', encoding='utf-8') as r:
                for line in r:
                    line = line.strip()
                    if line:  # 跳过空行
                        result = dict(json.loads(line))
                        # result[data['f12']] = data['hybk']
        except (FileNotFoundError, json.JSONDecodeError):
            return dict()
        # print(f'result: {result}')
        return result

    # 读取已有的行业板块
    def write_existing_json(self, result: dict = {}):
        # 读取userinfo.json文件中所有信息
        try:
            # jsonPath = self.settings.get('OUTPUT_FILE_PATH')
            # self.gridistJsonFile = f'{jsonPath}hybk.json'
            with open(self.gridistJsonFile, 'w', encoding='utf-8') as w:
                json_data = json.dumps(result, ensure_ascii=False) + '\n'
                w.write(json_data)
        except (FileNotFoundError, json.JSONDecodeError) as ex:
            self.logger.info(f'hybk Json文件写入失败: {str(ex)}')

    def start_requests(self):
        cb = generate_jquery_callback()
        ts = timestamp_13()
        self.gridist_url = f'{self.base_url}?np=1&fltt=1&invt=2&cb={cb}&fs={self.fs}&fields={self.fields}&fid=f3&pn=1&pz=20&po=1&dect=1&ut=fa5fd1943c7b386f172d6893dbfba10b&wbp2u=%7C0%7C0%7C0%7Cweb&_={ts}'
        # self.logger.info(f'base_url: {self.gridist_url} ')
        yield scrapy.Request(
            url=self.gridist_url,
            method='GET',
            callback=self.parse,
            meta={'page': 1, 'rowSize': 0}
        )

    # 主力排名数据采集
    def parse(self, response):
        try:
            if response.status != 200:
                self.logger.error(f'请求失败: {response.status}')
                return

            json_data = str_to_json(response.text)
            # 今日涨跌 小于 %400的数据不要
            # f3_list = jsonpath.jsonpath(json_data, '$..f3')
            # maxf3 = max(f3_list)
            # if maxf3 < 400:
            #     self.logger.info(f'一共采集了{rowSize}条数据！！！！')
            #     return

            # 处理分页
            rowSize = response.meta['rowSize']
            # self.logger.info(f'f3_list: {f3_list}, minf3: {minf3}')

            # 数据采集
            for item in jsonpath.jsonpath(json_data, '$..data')[0]['diff']:
                # ST 不要
                stockName = str(item['f14'])
                if stockName.find('st') != -1 or stockName.find('ST') != -1:
                    self.logger.info(f"退市股票: {item['f12']}, {item['f14']}, {item['f2']}")
                    continue

                # 涨幅小于4%的不要
                # f3 = float(item['f3'])
                # if f3 < 400:
                #     self.logger.info(f"涨幅小于4%股票: {item['f12']}, {item['f14']}, {item['f3']}")
                #     continue

                # 价格低于4元的不要
                f2 = str_to_float(item['f2'])
                if f2 < 400:
                    self.logger.info(f"价格低于4元的股票: {item['f12']}, {item['f14']}, {item['f2']}")
                    continue

                rowSize += 1

                # 是否已经采集过 条件1：股票代码不存在需要采集
                if item['f12'] not in self.gridistHybkDict.keys():
                    self.logger.info(f"{item['f12']} 行业板块名称没有，数据采集中...")
                    yield self.requestDepthData(item)
                    time.sleep(2)
                else:
                    item['hybk'] = self.gridistHybkDict[item['f12']]
                    if item['hybk'] == 'None':
                        self.logger.info(f"{item['f12']} 行业板块名称不正，数据采集中...")
                        yield self.requestDepthData(item)
                        time.sleep(2)
                    else:
                        yield from self.editFields(item)

            # 处理分页
            current_page = response.meta['page']
            if current_page < self.max_pages:
                next_page = current_page + 1
                cb = generate_jquery_callback()
                ts = timestamp_13()
                self.gridist_url = f'{self.base_url}?np=1&fltt=1&invt=2&cb={cb}&fs={self.fs}&fields={self.fields}&fid=f3&pn={next_page}&pz=20&po=1&dect=1&ut=fa5fd1943c7b386f172d6893dbfba10b&wbp2u=%7C0%7C0%7C0%7Cweb&_={ts}'
                # self.logger.info(f'base_url: {self.gridist_url} ')
                yield scrapy.Request(
                    url=self.gridist_url,
                    method='GET',
                    callback=self.parse,
                    meta={'page': next_page, 'rowSize': rowSize}
                )
                time.sleep(5)

        except Exception as ex:
            self.logger.error(f'解析错误: {str(ex)}')

    # 深度数据请求编辑
    def requestDepthData(self, item):
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
        filter = f'SECURITY_CODE%3D%22{item["f12"]}%22'
        new_filter = quote_str(unquote_str(filter))
        ts = timestamp_13()
        depthData_url = f'{depthData_base}?callback={callback}&reportName=RPT_F10_CORETHEME_CONTENT&columns={new_columns}&sortColumns={new_sortColumns}&sortTypes={new_sortTypes}' \
                        f'&source=WEB&client=WEB&filter=({new_filter})&_={ts}'
        # self.logger.info(f'{item["f12"]}.深度数据_url: {depthData_url}')
        return scrapy.Request(
            url=depthData_url,
            meta={'p_item': item},
            method='GET',
            errback=self.on_depth_error,  # 添加错误处理
            callback=self.parseDepthData
        )

    # 添加错误处理回调
    def on_depth_error(self, failure):
        item = failure.request.meta['p_item']
        self.logger.error(f"请求深度数据失败: {item['f12']}, {failure}")

    # 采集数据编辑
    def parseDepthData(self, response):
        try:
            raw_data = response.meta.get('p_item')
            json_data = str_to_json(response.text)
            depthData_list = jsonpath.jsonpath(json_data, '$..data')
            for item in depthData_list[0]:
                # 关键字
                keyword = str(item['KEY_CLASSIF']).strip()
                # 所属板块
                if keyword == '所属板块':
                    raw_data["hybk"] = str(item["MAINPOINT_CONTENT"]).split(" ")[0]
                    # 所属板块保存
                    hybk_dict = {'f12': raw_data['f12'], 'hybk': raw_data["hybk"]}

                    # 更新全局字典
                    self.gridistHybkDict.update(hybk_dict)
                break

            yield from self.editFields(raw_data)
        except Exception as e:
            self.logger.error(f"处理深度数据出错: {e}")

    # 采集数据编辑
    def editFields(self, raw_data):
        # 数据处理
        item = EastmoneyItem()
        item["f12"] = raw_data["f12"]  # 股票代码
        item["f14"] = str(raw_data["f14"]).strip()  # 股票名称
        item["f2"] = f'{round(str_to_int(raw_data["f2"]) / 100, 2)}'  # 最新价
        item["f3"] = f'{round(str_to_int(raw_data["f3"]) / 100, 2)}%'  # 涨跌幅
        item["f4"] = f'{round(str_to_int(raw_data["f4"]) / 100, 2)}'  # 涨跌额
        item["f5"] = amountUnitEdit(raw_data["f5"], '')  # 成交量(手)
        item["f6"] = amountUnitEdit(raw_data["f6"])  # 成交额
        item["f7"] = f'{round(str_to_int(raw_data["f7"]) / 100, 2)}%'  # 振幅
        item["f8"] = f'{round(str_to_int(raw_data["f8"]) / 100, 2)}%'  # 换手率
        item["f9"] = f'{round(str_to_int(raw_data["f9"]) / 100, 2)}%'  # 市盈率（动态）
        item[
            "f10"] = f'{round(str_to_int(raw_data["f10"]) / 100, 2)}' if f'{round(str_to_int(raw_data["f10"]) / 100, 2)}' != '0.0' else '-'  # 量比
        item["f15"] = f'{round(str_to_int(raw_data["f15"]) / 100, 2)}'  # 最高
        item["f16"] = f'{round(str_to_int(raw_data["f16"]) / 100, 2)}'  # 最低
        item["f17"] = f'{round(str_to_int(raw_data["f17"]) / 100, 2)}'  # 今开
        item["f18"] = f'{round(str_to_int(raw_data["f18"]) / 100, 2)}'  # 昨收
        item["f23"] = f'{round(str_to_int(raw_data["f23"]) / 100, 2)}'  # 市净率
        item["hybk"] = raw_data["hybk"]  # 所属板块
        yield item

    def close(self, spider, reason):
        self.logger.info(f'要处理 {len(self.gridistHybkDict)} 件。')
        self.write_existing_json(self.gridistHybkDict)