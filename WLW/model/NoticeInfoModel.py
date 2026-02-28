# _*_ coding: utf-8 _*_
# @Time : 2026/1/21 星期三 18:32
# @Author : 韦丽
# @Version: V 1.0
# @File : NoticeInfoModel.py
# @desc : 公告数据查询
import pandas

from WLW.StockBase import DateTimeUtils
from WLW.StockBase.sqlite_db import SQLiteDB
from WLW.Tools.LoggingEx import logger

# SHowWLW执行时的设定
db = SQLiteDB()

def getNoticeInfoData(noticeInfoCondition):
    # 报告时间
    reportDate = DateTimeUtils.get_quarter_dates()['end_date']

    # 检索SQL
    show_sql = f"""
                SELECT strftime('%Y-%m-%d', SIW.NOTICE_DATE) AS NOTICE_DATE,
                   SIW.INDUSTRY,
                   SIW.STOCK_CODE,
                   SIW.STOCK_NAME,
                   SIW.NOTICE_TYPE,
                   SIW.NOTICE_TITLE,
                   SIW.NOTICE_INFO_URL,
                   SIW.create_time,
                   COALESCE(SIQ.STOCK_TYPE_NAME, '无风险') AS STOCK_TYPE_NAME,
                   COALESCE(SH.INSTITUTION_COUNT, 0) AS INSTITUTION_COUNT
                FROM NOTICE_CRAWL SIW
                LEFT JOIN STOCK_HOLDING SH
                ON SIW.STOCK_CODE = SH.STOCK_CODE
                AND strftime('%Y%m%d', SH.REPORT_DATE) = '{reportDate}'
                LEFT JOIN (SELECT STOCK_NO, 
                                 group_concat(STOCK_TYPE_LNAME, ',') AS STOCK_TYPE_NAME,
                                 group_concat(STOCK_TYPE, ',') AS STOCK_TYPE
                            FROM STOCK_INFO_QUESTION 
                            GROUP BY STOCK_NO) SIQ
                ON SIW.STOCK_CODE = SIQ.STOCK_NO
                """

    where_sql = ' WHERE 1 = 1'

    if noticeInfoCondition:
        # 交易日期
        if conditionString(noticeInfoCondition.saleDayFrom):
            where_sql += f" AND strftime('%Y%m%d', SIW.create_time) >= '{noticeInfoCondition.saleDayFrom}'"
        if conditionString(noticeInfoCondition.saleDayTo):
            where_sql += f" AND strftime('%Y%m%d', SIW.create_time) <= '{noticeInfoCondition.saleDayTo}'"

        # 股票No
        if conditionString(noticeInfoCondition.stockNo):
            if noticeInfoCondition.saleDateType == 'S':
                where_sql += f" AND SIW.STOCK_CODE LIKE '{noticeInfoCondition.stockNo}%'"
            elif noticeInfoCondition.saleDateType == 'M':
                where_sql += f" AND SIW.STOCK_CODE in ({noticeInfoCondition.stockNo})"

        # 股票名称
        if conditionString(noticeInfoCondition.stockName):
            where_sql += f" AND SIW.STOCK_NAME LIKE '%{noticeInfoCondition.stockName}%'"

    # 检索SQL文
    select_sql = show_sql + where_sql + noticeInfoCondition.orderByOption
    logger.info(f'检索SQL：{select_sql}')
    return db.process_stock_data_select(select_sql)

def conditionString(strValue : str = ''):
    if strValue == None or strValue == '':
        return False
    return True

# 以公告类型进行数据编辑
def editNoticeTypeAndSort(showNoticeData, formWidget):
    if showNoticeData:
        commonColumns = ['NOTICE_DATE', 'INDUSTRY', 'STOCK_CODE', 'STOCK_NAME', 'NOTICE_TYPE', 'NOTICE_TITLE', 'NOTICE_INFO_URL', 'create_time', 'STOCK_TYPE_NAME',
                         'INSTITUTION_COUNT']
        pandasData = pandas.DataFrame(data=showNoticeData, columns=commonColumns)
        # 按采集日期降序排列后，取每个股票No第一次出现的数据（即最新日期）
        groupNoticeType = (
            pandasData
            .sort_values('create_time', ascending=False)  # 先按日期降序
            .groupby(by='NOTICE_TYPE')  # 按涨停主题分组
        )
        sortGroupSuoShuHangYe = []
        sortGroupSuoShuHangYeColumns = ['公告类型', '数量', '股票code', '股票名称', '公告标题', '公告详情']

        for noticeType, groupbyCol in groupNoticeType:
            num = len(groupbyCol)
            sortStockCodeData = groupbyCol.sort_values(by=['STOCK_CODE'], ascending=False)
            stockNames = {row['STOCK_CODE']: row['STOCK_NAME'] for _, row in sortStockCodeData.iterrows()}
            noticeTitles = {row['STOCK_CODE']: row['NOTICE_TITLE'] for _, row in sortStockCodeData.iterrows()}
            stockNoticeUrl = {row['STOCK_CODE']: row['NOTICE_INFO_URL'] for _, row in sortStockCodeData.iterrows()}
            stockCodes = [row['STOCK_CODE'] for _, row in sortStockCodeData.iterrows()]
            sortGroupSuoShuHangYe.append(
                [noticeType, num, stockCodes, stockNames, noticeTitles, stockNoticeUrl])

        pandasSortData = pandas.DataFrame(data=sortGroupSuoShuHangYe, columns=sortGroupSuoShuHangYeColumns).sort_values(
            by='数量', ascending=False)
        return pandasSortData
    return pandas.DataFrame()