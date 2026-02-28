import jsonpath
from fake_useragent import UserAgent

from .eastmoneyTools import unquote_str, quote_str, str_to_json, now_date, \
    generate_jquery_callback, amountUnitEdit
from ..items import *

# 板块资金流数据抓取
class HyzjlCrawlSpider(scrapy.Spider):
    name = "hyzjl_crawl"
    allowed_domains = ["eastmoney.com"]
    # start_urls = ["https://eastmoney.com"]
    cb = generate_jquery_callback()
    url_base = f'https://push2.eastmoney.com/api/qt/clist/get?cb={cb}&fid=f62&po=1&pz=99&pn=1&np=1&fltt=2&invt=2&ut=8dec03ba335b81bf4ebdf7b29ec27d15'
    #           https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery112307581714048690535_1744844737268&fid=f62&po=1&pz=50&pn=1&np=1&fltt=2&invt=2&ut=8dec03ba335b81bf4ebdf7b29ec27d15&fs=m%3A90+t%3A2&fields=f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13
    #           https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery112304437305601807815_1745414051539&fid=f62&po=1&pz=50&pn=1&np=1&fltt=2&invt=2&ut=8dec03ba335b81bf4ebdf7b29ec27d15&fs=m%3A90+t%3A2&fields=f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13
    fs = 'm%3A90+t%3A2'
    fields = 'f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13'

    def start_requests(self):
        new_fs = quote_str(unquote_str(self.fs))
        new_fields = quote_str(unquote_str(self.fields))
        url = f'{self.url_base}&fs={new_fs}&fields={new_fields}'
        self.logger.info(f'start_urls： {url}')
        header = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'User-Agent': UserAgent().random,
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            # 'Connection': 'keep-alive',
            'cookie': 'qgqp_b_id=6a56383af907485ce0e0d8ee26bffcaf; st_nvi=HSp8NEXYJ6lQsspDvGJPaef5e; nid=056f78ce7884d0e39dd0615d06a7c418; nid_create_time=1754575795555; gvi=QjFEkx_yBtvnBH0QlNFd5ed71; gvi_create_time=1754575795555; fullscreengg=1; fullscreengg2=1; st_si=81626491717917; st_asi=delete; st_pvi=48093117281162; st_sp=2025-08-07%2022%3A09%3A55; st_inirUrl=https%3A%2F%2Fdata.eastmoney.com%2Fbkzj%2Fhy.html; st_sn=4; st_psi=20251022063540801-113300300820-0980333881',
            'Referer': 'https://push2.eastmoney.com'
        }
        yield scrapy.Request(url=url, callback=self.parse, headers=header)

    def parse(self, response):
        self.logger.info(f'response.text： {response.text}')
        json_data = str_to_json(response.text)
        self.logger.info(f'json_data： {json_data}')

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
