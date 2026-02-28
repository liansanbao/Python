# _*_ coding: utf-8 _*_
# @Time : 2025/8/26 星期二 8:29
# @Author : 韦丽
# @Version: V 1.0
# @File : PlateFundModel.py
# @desc : 板块资金实体类
from WLW.StockBase import DateTimeUtils
from WLW.StockBase.sqlite_db import SQLiteDB
from WLW.Tools.LoggingEx import logger

# SHowWLW执行时的设定
db = SQLiteDB()

def getPlateFundWLWData(plateFundCondition):
    # 报告时间
    reportDate = DateTimeUtils.get_quarter_dates()['end_date']

    # 检索SQL
    sql_start = f"""
        Select strftime('%Y-%m-%d %H:%M:00', HC.CREATE_DATE) as CREATE_DATE,
               HC.F12,
               HC.F14,
               HC.F2,
               HC.F3,
               HC.F62,
               HC.F184,
               HC.F204,
               HC.F205,
               COALESCE(SH.INSTITUTION_COUNT, 0) AS INSTITUTION_COUNT,
               COALESCE(SIW.LIMIT_TITLE, '') AS LIMIT_TITLE,
               COALESCE(SIW.CONCEPT, '') AS CONCEPT,
               COALESCE(SIW.LIMIT_WHY, '') AS LIMIT_WHY,
               COALESCE(GS.F3, '') AS GSF3,
               COALESCE(GS.F2, '') AS GSF2,
               COALESCE(GS.F5, '') AS GSF5,
               COALESCE(GS.F6, '') AS GSF6,
               COALESCE(GS.F8, '') AS GSF8,
               strftime('%Y-%m-%d %H:%M:%S', SH.create_time) AS create_time
               FROM HYZJL_CRAWL HC
               LEFT JOIN GRIDIST_STOCK GS
               ON strftime('%Y-%m-%d', HC.CREATE_DATE) = strftime('%Y-%m-%d', GS.CREATE_DATE)
               AND HC.F205 = GS.F12
               LEFT JOIN STOCK_HOLDING SH
               --ON strftime('%Y-%m-%d', HC.CREATE_DATE) = strftime('%Y-%m-%d', SH.CREATE_DATE)
               ON HC.F205 = SH.STOCK_CODE
               AND strftime('%Y%m%d', SH.REPORT_DATE) = '{reportDate}'
               LEFT JOIN STOCK_INFO_WLW SIW
               ON strftime('%Y-%m-%d', HC.CREATE_DATE) = strftime('%Y-%m-%d', SIW.STOCK_DATE)
               AND HC.F205 = SIW.STOCK_NO
        """

    where_sql = ' WHERE 1 = 1'
    condition = ['=', '>', '<']
    if plateFundCondition:
        # 活动类型
        if plateFundCondition.activateType == 'S':
            # 交易日期From
            if conditionString(plateFundCondition.hangQingDateFrom):
                where_sql += f" AND strftime('%Y%m%d', HC.CREATE_DATE) >= '{plateFundCondition.hangQingDateFrom}'"

            # 交易日期To
            if conditionString(plateFundCondition.hangQingDateTo):
                where_sql += f" AND strftime('%Y%m%d', HC.CREATE_DATE) <= '{plateFundCondition.hangQingDateTo}'"

            where_sql += " AND HC.ActivateType = '1'"
        elif plateFundCondition.activateType == 'A':
            # 交易日期From
            if conditionString(plateFundCondition.hangQingDateFrom):
                where_sql += f" AND strftime('%Y%m%d %H%M00', HC.CREATE_DATE) = '{plateFundCondition.searchTime}'"

            where_sql += " AND HC.ActivateType = '0'"

        # 板块No
        if conditionString(plateFundCondition.plateFund_No):
            if plateFundCondition.activateType == 'S':
                where_sql += f" AND HC.F12 = '{plateFundCondition.plateFund_No}'"
            elif plateFundCondition.activateType == 'M':
                where_sql += f" AND HC.F12 in ({plateFundCondition.plateFund_No})"

        # 板块名称
        if conditionString(plateFundCondition.plateFund_Name):
            where_sql += f" AND HC.F14 LIKE '%{plateFundCondition.plateFund_Name}%'"

        # 主力净流入(净额)
        if conditionString(plateFundCondition.plateFund_zljlrje):
            where_sql += f" AND CAST(HC.F62 AS INTEGER) {condition[plateFundCondition.condition_zljlrje]} CAST({plateFundCondition.plateFund_zljlrje} AS INTEGER) "

        # 板块类型
        if conditionString(plateFundCondition.hyType):
            where_sql += f" AND HC.hyType = '{plateFundCondition.hyType}'"


    # 检索SQL文
    select_sql = sql_start + where_sql + plateFundCondition.orderByOption + ' LIMIT 86'
    logger.info(f'检索SQL：{select_sql}')

    return db.process_stock_data_select(select_sql)

def conditionString(strValue : str = ''):
    if strValue == None or strValue == '':
        return False
    return True
