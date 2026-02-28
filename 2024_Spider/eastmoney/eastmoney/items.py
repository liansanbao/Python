# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class EastmoneyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 最新价
    f2 = scrapy.Field()
    # 今日涨跌幅
    f3 = scrapy.Field()
    # 涨跌额
    f4 = scrapy.Field()
    # 成交量(手)
    f5 = scrapy.Field()
    # 成交额
    f6 = scrapy.Field()
    # 振幅
    f7 = scrapy.Field()
    # 换手率
    f8 = scrapy.Field()
    # 市盈率（动态）
    f9 = scrapy.Field()
    # 量比
    f10 = scrapy.Field()
    # 行业/股票代码
    f12 = scrapy.Field()
    # 行业/股票名称
    f14 = scrapy.Field()
    # 最高
    f15 = scrapy.Field()
    # 最低
    f16 = scrapy.Field()
    # 今开
    f17 = scrapy.Field()
    # 昨收
    f18 = scrapy.Field()
    # 市净率
    f23 = scrapy.Field()
    # 量比
    f50 = scrapy.Field()
    # 今日主力净流入(净额)
    f62 = scrapy.Field()
    # 今日超大单净流入(净额)
    f66 = scrapy.Field()
    # 今日超大单净流入(净占比)
    f69 = scrapy.Field()
    # 今日大单净流入(净额)
    f72 = scrapy.Field()
    # 今日大单净流入(净占比)
    f75 = scrapy.Field()
    # 今日中单净流入(净额)
    f78 = scrapy.Field()
    # 今日中单净流入(净占比)
    f81 = scrapy.Field()
    # 今日小单净流入(净额)
    f84 = scrapy.Field()
    # 今日小单净流入(净占比)
    f87 = scrapy.Field()
    # 所属板块名称
    f100 = scrapy.Field()
    # 5日涨跌
    f109 = scrapy.Field()
    # 10日涨跌
    f160 = scrapy.Field()
    # 5日净占比
    f165 = scrapy.Field()
    # 换手
    f168 = scrapy.Field()
    # 涨跌金额
    f169 = scrapy.Field()
    # 10日净占比
    f175 = scrapy.Field()
    # 今日主力净流入(净占比)
    f184 = scrapy.Field()
    # 今日主力净流入(最大股名称)
    f204 = scrapy.Field()
    # 今日主力净流入(最大股代码)
    f205 = scrapy.Field()
    # 今日排名
    f225 = scrapy.Field()
    # 5日排名
    f263 = scrapy.Field()
    # 10日排名
    f264 = scrapy.Field()
    # 所属板块ID
    f265 = scrapy.Field()
    # 数据采集日期
    frq = scrapy.Field()
    # 所属行业
    hybk = scrapy.Field()
    # 游资['有','无']
    youzi = scrapy.Field()
    # 涨停主题
    limitTitle = scrapy.Field()
    # 涨停原因
    limitWhy = scrapy.Field()
    # 概念
    concept = scrapy.Field()
    # 深度数据
    depthData = scrapy.Field()
    # 可视化报告Code
    secucode = scrapy.Field()
    # 可视化报告日期
    endData = scrapy.Field()
    # 报告日期
    REPORT_DATE = scrapy.Field()
    # 持股机构数
    INSTITUTION_COUNT = scrapy.Field()
    # 持仓数量（万股）
    HOLDING_QUANTITY = scrapy.Field()
    # 持仓市值（万元）
    HOLDING_VALUE = scrapy.Field()
    # 占总股本比例（%）
    TOTAL_SHARE_RATIO = scrapy.Field()
    # 占已流通A股比例（%）
    FLOAT_SHARE_RATIO = scrapy.Field()
    # 较上期增减仓股数（万股）
    CHANGE_QUANTITY = scrapy.Field()
    # 增减仓占已流通A股比例（%）
    CHANGE_RATIO = scrapy.Field()
    # 仓位类型
    POSITION_TYPE = scrapy.Field()
    # 机构属性
    INSTITUTION_TYPE = scrapy.Field()
    # 持股机构名称
    INSTITUTION_NAME = scrapy.Field()
    pass
