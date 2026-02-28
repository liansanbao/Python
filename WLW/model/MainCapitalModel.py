import pandas

from WLW.StockBase import DateTimeUtils
from WLW.StockBase.sqlite_db import SQLiteDB
from WLW.Tools.LoggingEx import logger
from WLW.model.MainCapitalCondition import MainCapitalCondition

# SHowWLW执行时的设定
db = SQLiteDB()

def getMainCapitalWLWData(mainCapitalCondition, tableName = 'ZJLX_CRAWL'):
    # 检索SQL
    sql_start = f"""
        Select strftime('%Y-%m-%d', SIW.HANG_QING_DATE) as HANG_QING_DATE,
               SIW.HANG_YE,
               SIW.STOCK_NO,
               SIW.STOCK_NAME,
               SIW.ZHANG_FU,
               SIW.XIAN_JIA,
               COALESCE(SIQ.STOCK_TYPE_NAME, '无风险') AS STOCK_TYPE_NAME,
                """

    if tableName == 'ZJLX_CRAWL':
        sql_content = """
               SIW.F62,
               SIW.F184,
               SIW.F66,
               SIW.F69,
               SIW.F72,
               SIW.F75,
               SIW.F78,
               SIW.F81,
               SIW.F84,
               SIW.F87,
               SIW.DEPTHDATAURL,
               SIW.F10URL,
               SIW.REPORTCHARTURL
                """
    else:
        sql_content = """
               SIW.SHOU_PAN_JIA,
               SIW.DAY_CHENG_JIAO_E,
               SIW.DAY_5_ZHANG_FU,
               SIW.DAY_5_CHENG_JIAO_E,
               SIW.DAY_20_ZHANG_FU,
               SIW.DAY_60_ZHANG_FU,
               SIW.MONTH_ZHANG_FU,
               SIW.YEAR_ZHANG_FU,
               SIW.SHI_YING_LV,
               SIW.ZONG_SHI_ZHI
        """

    sql_end = f"""
               FROM {tableName} SIW
               LEFT JOIN (SELECT STOCK_NO, 
                                 GROUP_CONCAT(STOCK_TYPE_LNAME) AS STOCK_TYPE_NAME,
                                 GROUP_CONCAT(STOCK_TYPE) AS STOCK_TYPE
                            FROM STOCK_INFO_QUESTION 
                            GROUP BY STOCK_NO) SIQ
               ON SIW.STOCK_NO = SIQ.STOCK_NO
    """

    where_sql = ' WHERE 1 = 1'
    condition = ['=', '>', '<']
    if mainCapitalCondition:
        # 交易日期From
        if conditionString(mainCapitalCondition.hangQingDateFrom):
            where_sql += f" AND strftime('%Y%m%d', SIW.HANG_QING_DATE) >= '{mainCapitalCondition.hangQingDateFrom}'"

        # 交易日期To
        if conditionString(mainCapitalCondition.hangQingDateTo):
            where_sql += f" AND strftime('%Y%m%d', SIW.HANG_QING_DATE) <= '{mainCapitalCondition.hangQingDateTo}'"

        # 股票No
        if conditionString(mainCapitalCondition.masterStockNo):
            if mainCapitalCondition.saleDateType == 'D':
                where_sql += f" AND SIW.STOCK_NO = '{mainCapitalCondition.masterStockNo}'"
            elif mainCapitalCondition.saleDateType == 'M':
                where_sql += f" AND SIW.STOCK_NO in ({mainCapitalCondition.masterStockNo})"

        # 股票名称
        if conditionString(mainCapitalCondition.masterStockName):
            where_sql += f" AND SIW.STOCK_NAME LIKE '%{mainCapitalCondition.masterStockName}%'"

        # 涨幅 大于等于
        if conditionString(mainCapitalCondition.masterZhangFu):
            where_sql += f" AND SIW.ZHANG_FU >= '{mainCapitalCondition.masterZhangFu}'"

        # 现价
        if conditionString(mainCapitalCondition.masterXianJia):
            where_sql += f" AND SIW.XIAN_JIA {condition[mainCapitalCondition.condition_xj]} '{mainCapitalCondition.masterXianJia}' "

        # 所属行业
        if conditionString(mainCapitalCondition.masterHangYe):
            where_sql += f" AND SIW.HANG_YE = '{mainCapitalCondition.masterHangYe}'"

        # 风险类型
        if conditionString(mainCapitalCondition.masterStockType) and mainCapitalCondition.masterStockType != 0:
            where_sql += f" AND COALESCE(SIQ.STOCK_TYPE, '7') like '%{mainCapitalCondition.masterStockType}%'"

    # 检索SQL文
    select_sql = sql_start + sql_content + sql_end + where_sql + mainCapitalCondition.orderByOption
    logger.info(f'检索SQL：{select_sql}')

    return db.process_stock_data_select(select_sql)

def conditionString(strValue : str = ''):
    if strValue == None or strValue == '':
        return False
    return True

def editSuoShuHangYeAndSort(showMainCapitalData, formWigdet):
    if showMainCapitalData:
        pandasData = pandas.DataFrame(showMainCapitalData)
        commonColumns = ['交易日期', '所属行业', '股票No', '名称', '涨幅(%)', '现价(元)', '风险种类', '主力净额(亿)', '主力净占比(%)', '超大单净额(亿)', '超大单净占比(%)', '大单净额(亿)', '大单净占比(%)',
             '中单净额(亿)', '中单净占比(%)', '小单净额(亿)', '小单净占比(%)', '数据URL', 'F10URL', '可视化报告']
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
        saleDateFrom = DateTimeUtils.Format_changed(formWigdet.hangQingDate_From.text(), '%Y年%M月%d日', '%Y%M%d')
        saleDateTo = DateTimeUtils.Format_changed(formWigdet.hangQingDate_To.text(), '%Y年%M月%d日', '%Y%M%d')
        zhangFuC = formWigdet.master_zhangFu_v.text()
        xianJiaC = formWigdet.master_xianJia_v.text()
        # 现价比较条件
        condition_xj = formWigdet.condition_xj.currentIndex()
        masterStockTypeC = formWigdet.master_stockType.currentIndex()
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
            mainCapitalCondition = MainCapitalCondition(saleDateFrom, saleDateTo, stockNo, '', name,
                                                        zhangFuC,
                                                        xianJiaC,
                                                        masterStockTypeC, condition_xj, 'M', ' ORDER BY SIW.ZHANG_FU DESC ')
            stockInfoDatas = getMainCapitalWLWData(mainCapitalCondition)
            pandasStockInfoData = pandas.DataFrame(data=stockInfoDatas, columns=commonColumns)
            sortGroupSuoShuHangYe.append([name, num, stockNames, stockXianJia, stockZhangFu, stockNos, stockDepthDataUrls, stockF10Urls, stockReportchartUrls, pandasStockInfoData])

        pandasSortData = pandas.DataFrame(data=sortGroupSuoShuHangYe, columns=sortGroupSuoShuHangYeColumns).sort_values(by='数量', ascending=False)
        return pandasSortData
    return pandas.DataFrame()


if __name__ == '__main__':
    mainCapitalCondition = MainCapitalCondition('20250225', '', '', '', '', '', '', '', 'D', '')
    data = getMainCapitalWLWData(mainCapitalCondition)
    if (data):
        historyHolidays = [[row] for row in data]
        for row, va in enumerate(historyHolidays):
            print(type[row], type(va), va)
