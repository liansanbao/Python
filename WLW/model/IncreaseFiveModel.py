# _*_ coding: utf-8 _*_
# @Time : 2025/8/23 星期六 10:28
# @Author : 韦丽
# @Version: V 1.0
# @File : IncreaseFiveModel.py
# @desc : 涨幅(5%)以上实体类
import pandas

from WLW.StockBase import DateTimeUtils
from WLW.StockBase.MysqlConnection import connect_to_mysql, select_data
from WLW.StockBase.sqlite_db import SQLiteDB
from WLW.Tools.LoggingEx import logger
from WLW.model.MainCapitalCondition import MainCapitalCondition

# SHowWLW执行时的设定
db = SQLiteDB()

# 涨幅(5%)以上数据检索SQL
def getIncreaseFiveWLWData(increaseFiveCondition, tableName = 'GRIDIST_STOCK'):
    # 报告时间
    reportDate = DateTimeUtils.get_quarter_dates()['end_date']
    # 检索SQL
    sql_start = f"""
        Select strftime('%Y-%m-%d', GS.CREATE_DATE) as CREATE_DATE,
               GS.hybk,
               GS.F12,
               GS.F14,
               GS.F3,
               GS.F2,
               COALESCE(SIQ.STOCK_TYPE_NAME, '无风险') AS STOCK_TYPE_NAME,
               GS.F4,
               GS.F5,
               GS.F6,
               GS.F7,
               GS.F8,
               GS.F9,
               GS.F10,
               COALESCE(SIW.LIMIT_TITLE, '') AS LIMIT_TITLE,
               COALESCE(SIW.CONCEPT, '') AS CONCEPT,
               COALESCE(SIW.LIMIT_WHY, '') AS LIMIT_WHY,
               COALESCE(SH.INSTITUTION_COUNT, 0) AS INSTITUTION_COUNT,
               GS.DEPTHDATAURL, 
               GS.F10URL, 
               GS.REPORTCHARTURL,
               strftime('%Y-%m-%d %H:%M:%S', SH.create_time) AS create_time
               FROM GRIDIST_STOCK GS
               LEFT JOIN (SELECT STOCK_NO, 
                                 GROUP_CONCAT(STOCK_TYPE_LNAME) AS STOCK_TYPE_NAME,
                                 GROUP_CONCAT(STOCK_TYPE) AS STOCK_TYPE
                            FROM STOCK_INFO_QUESTION 
                            GROUP BY STOCK_NO) SIQ
               ON GS.F12 = SIQ.STOCK_NO
               LEFT JOIN STOCK_HOLDING SH
               ON GS.F12 = SH.STOCK_CODE
               AND strftime('%Y%m%d', SH.REPORT_DATE) = '{reportDate}'
               LEFT JOIN STOCK_INFO_WLW SIW
               ON strftime('%Y-%m-%d', GS.CREATE_DATE) = strftime('%Y-%m-%d', SIW.STOCK_DATE)
               AND GS.F12 = SIW.STOCK_NO
        """

    where_sql = ' WHERE 1 = 1'
    condition = ['=', '>', '<']
    if increaseFiveCondition:
        # 交易日期From
        if conditionString(increaseFiveCondition.hangQingDateFrom):
            where_sql += f" AND strftime('%Y%m%d', GS.CREATE_DATE) >= '{increaseFiveCondition.hangQingDateFrom}'"

        # 交易日期To
        if conditionString(increaseFiveCondition.hangQingDateTo):
            where_sql += f" AND strftime('%Y%m%d', GS.CREATE_DATE) <= '{increaseFiveCondition.hangQingDateTo}'"

        # 股票No
        if conditionString(increaseFiveCondition.masterStockNo):
            if increaseFiveCondition.saleDateType == 'D':
                where_sql += f" AND GS.F12 = '{increaseFiveCondition.masterStockNo}'"
            elif increaseFiveCondition.saleDateType == 'M':
                where_sql += f" AND GS.F12 in ({increaseFiveCondition.masterStockNo})"

        # 股票名称
        if conditionString(increaseFiveCondition.masterStockName):
            where_sql += f" AND GS.F14 LIKE '%{increaseFiveCondition.masterStockName}%'"

        # 涨幅 大于等于
        # if conditionString(increaseFiveCondition.masterZhangFu):
        #     where_sql += f" AND GS.F3 >= '{increaseFiveCondition.masterZhangFu}'"

        # 现价
        if conditionString(increaseFiveCondition.masterXianJia):
            where_sql += f" AND CAST(GS.F2 AS INTEGER) {condition[increaseFiveCondition.condition_xj]} CAST({increaseFiveCondition.masterXianJia} AS INTEGER) "

        # 所属行业
        if conditionString(increaseFiveCondition.masterHangYe):
            where_sql += f" AND GS.hybk like '%{increaseFiveCondition.masterHangYe}%'"

        # 风险类型
        if conditionString(increaseFiveCondition.masterStockType) and increaseFiveCondition.masterStockType != 0:
            where_sql += f" AND COALESCE(SIQ.STOCK_TYPE, '7') like '%{increaseFiveCondition.masterStockType}%'"

    # 检索SQL文
    select_sql = sql_start + where_sql + increaseFiveCondition.orderByOption
    logger.info(f'检索SQL：{select_sql}')

    return db.process_stock_data_select(select_sql)

def conditionString(strValue : str = ''):
    if strValue == None or strValue == '':
        return False
    return True

def editSuoShuHangYeAndSort(showMainCapitalData, formWigdet):
    if showMainCapitalData:
        pandasData = pandas.DataFrame(showMainCapitalData)
        commonColumns = ['交易日期', '所属行业', '股票No', '名称', '涨幅', '现价(元)', '风险种类', '涨跌额', '成交量(手)', '成交额', '振幅', '换手率', '市盈率（动态）',
             '量比', '最高', '最低', '今开', '昨收', '机构持股数量']
        pandasData.columns = commonColumns
        # 以股票No为条件删除重复行，默认保留第一次出现的行:drop_duplicates
        # groupSuoShuHangYe = pandasData.drop_duplicates(subset=['股票No']).groupby(by='所属行业')
        # 按交易日期降序排列后，取每个股票No第一次出现的数据（即最新日期）
        groupSuoShuHangYe = (
            pandasData
            .sort_values('交易日期', ascending=False)  # 先按日期降序
            .drop_duplicates(subset=['股票No'])  # 保留每个股票最新记录
            .groupby(by='所属行业')  # 按行业分组
        )
        sortGroupSuoShuHangYe = []
        sortGroupSuoShuHangYeColumns = ['所属行业', '数量', '股票名称', '现价', '涨幅', '股票No', '数据URL', 'F10URL', '可视化报告', 'DATA']
        # 检索条件
        saleDateFrom = DateTimeUtils.Format_changed(formWigdet.lncreaseDate_From.text(), '%Y年%M月%d日', '%Y%M%d')
        saleDateTo = DateTimeUtils.Format_changed(formWigdet.lncreaseDate_To.text(), '%Y年%M月%d日', '%Y%M%d')
        # zhangFuC = formWigdet.lncrease_zhangFu.text()
        zhangFuC = ''
        xianJiaC = formWigdet.lncrease_xianJia.text()
        # 现价比较条件
        condition_xj = formWigdet.lncrease_condition_xj.currentIndex()
        lncreaseStockTypeC = formWigdet.lncrease_stockType.currentIndex()
        for name, groupbyCol in groupSuoShuHangYe:
            # 统计行业所有的股票
            num = len(groupbyCol)
            sortXianJiaData = groupbyCol.sort_values(by=['涨幅(%)', '现价(元)'], ascending=False)
            stockNames = {row['股票No']:row['名称'] for _, row in sortXianJiaData.iterrows()}
            stockXianJia ={row['股票No']:row['现价(元)'] for _, row in sortXianJiaData.iterrows()}
            stockZhangFu = {row['股票No']:row['涨幅(%)'] for _, row in sortXianJiaData.iterrows()}
            stockDepthDataUrls = {row['股票No']: row['数据URL'] for _, row in sortXianJiaData.iterrows()}
            stockF10Urls = {row['股票No']: row['F10URL'] for _, row in sortXianJiaData.iterrows()}
            stockReportchartUrls = {row['股票No']: row['可视化报告'] for _, row in sortXianJiaData.iterrows()}
            stockNos = [f"'{stockNo}'" for stockNo in sortXianJiaData['股票No']]
            stockNo = ', '.join(stockNos)
            increaseFiveCondition = MainCapitalCondition(saleDateFrom, saleDateTo, stockNo, '', name,
                                                        zhangFuC,
                                                        xianJiaC,
                                                        lncreaseStockTypeC, condition_xj, 'M', ' ORDER BY GS.ZHANG_FU DESC ')
            stockInfoDatas = getIncreaseFiveWLWData(increaseFiveCondition)
            pandasStockInfoData = pandas.DataFrame(data=stockInfoDatas, columns=commonColumns)
            sortGroupSuoShuHangYe.append([name, num, stockNames, stockXianJia, stockZhangFu, stockNos, stockDepthDataUrls, stockF10Urls, stockReportchartUrls, pandasStockInfoData])

        pandasSortData = pandas.DataFrame(data=sortGroupSuoShuHangYe, columns=sortGroupSuoShuHangYeColumns).sort_values(by='数量', ascending=False)
        return pandasSortData
    return pandas.DataFrame()

# 持股机构总览数据检索SQL
def getInstitutionHoldingDetail(reportDate, stockNo):
    # 检索SQL
    sql_start = f"""
            SELECT row_num,
            STOCK_CODE, 
            REPORT_DATE, 
            INSTITUTION_TYPE, 
            INSTITUTION_COUNT,
            HOLDING_QUANTITY, 
            HOLDING_VALUE, 
            TOTAL_SHARE_RATIO, 
            FLOAT_SHARE_RATIO 
        FROM (
            SELECT *,  ROW_NUMBER() OVER(ORDER BY REPORT_DATE DESC) AS row_num 
            FROM idiom.INSTITUTION_HOLDING_DETAIL 
            """

    where_sql = ' WHERE 1 = 1'
    # 报告时间
    if conditionString(reportDate):
        where_sql += f" AND DATE_FORMAT(REPORT_DATE, '%Y-%m-%d') = '{reportDate}'"

    # 股票No
    if conditionString(stockNo):
        where_sql += f" AND STOCK_CODE = '{stockNo}'"

    endSql = ' ORDER BY INSTITUTION_COUNT ASC) AS T'
    # 检索SQL文
    select_sql = sql_start + where_sql + endSql
    logger.info(f'检索SQL：{select_sql}')

    return getAll(select_sql)

# 持仓机构数据检索SQL
def getPositionHoldingDetail(reportDate, stockNo, institutionType):
    # 检索SQL
    sql_start = f"""
            SELECT row_num,
            STOCK_CODE, 
            REPORT_DATE, 
            INSTITUTION_NAME, 
            INSTITUTION_TYPE, 
            HOLDING_QUANTITY, 
            HOLDING_VALUE, 
            TOTAL_SHARE_RATIO, 
            FLOAT_SHARE_RATIO 
        FROM (
            SELECT *,  ROW_NUMBER() OVER(ORDER BY REPORT_DATE DESC) AS row_num 
            FROM idiom.POSITION_HOLDING_DETAIL  
            """

    where_sql = ' WHERE 1 = 1'
    # 报告时间
    if conditionString(reportDate):
        where_sql += f" AND DATE_FORMAT(REPORT_DATE, '%Y-%m-%d') = '{reportDate}'"

    # 股票No
    if conditionString(stockNo):
        where_sql += f" AND STOCK_CODE = '{stockNo}'"

    # 机构属性(如:一般法人/基金/QFII等)
    if conditionString(institutionType) and institutionType != '全部':
        where_sql += f" AND INSTITUTION_TYPE LIKE '%{institutionType}%'"

    endSql = ' ) AS T'
    # 检索SQL文
    select_sql = sql_start + where_sql + endSql
    logger.info(f'检索SQL：{select_sql}')

    return getAll(select_sql)

def getAll(sql):
    resutlData = {}
    dbconnection = connect_to_mysql('WLW')
    try:
        if dbconnection:
            cursor = dbconnection.cursor()

            resutlData = select_data(cursor, sql)
            cursor.close()
    except Exception as ex:
        raise ex
    finally:
        if dbconnection:
            dbconnection.close()
    return resutlData