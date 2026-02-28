import pandas

from WLW.StockBase import DateTimeUtils
from WLW.StockBase.sqlite_db import SQLiteDB
from WLW.model.StockInfoCondition import StockInfoCondition
from WLW.Tools.LoggingEx import logger

# SHowWLW执行时的设定
db = SQLiteDB()

def getStockInfoWLWData(stockInfoCondition):
    # 报告时间
    reportDate = DateTimeUtils.get_quarter_dates()['end_date']

    # 检索SQL
    show_sql = f"""
                    SELECT strftime('%Y-%m-%d', SIW.STOCK_DATE) AS formatted_date,
                       SIW.SUO_SHU_HANG_YE,
                       SIW.STOCK_NO,
                       SIW.STOCK_NAME,
                       SIW.ZHANG_DIE_FU,
                       SIW.ZUI_XING_JIA,
                       COALESCE(CASE SIW.LIAN_BAN_SHU
                          WHEN 1 THEN ' 首板'
                          ELSE SIW.LIAN_BAN_SHU || '连板'
                       END, '') AS LIAN_BAN_SHU,
                       SIW.ZHA_BAN_CI_SHU,
                       COALESCE(SIQ.STOCK_TYPE_NAME, '无风险') AS STOCK_TYPE_NAME,
                       SIW.YOU_ZI_YOU_WU,
                       SIW.CHENG_JIAO_E,
                       SIW.HUAN_SHOU_LV,
                       SIW.FIRST_FENG_BAN_TIME,
                       SIW.LAST_FENG_BAN_TIME,
                       SIW.FENG_BAN_JIN_E,
                       SIW.ZHANG_TING_TOTAL,
                       SIW.LIMIT_TITLE,
                       SIW.LIMIT_WHY,
                       COALESCE(SH.INSTITUTION_COUNT, 0) AS INSTITUTION_COUNT,
					   SIW.DEPTHDATAURL,
		               SIW.F10URL,
		               SIW.REPORTCHARTURL,
		               strftime('%Y-%m-%d %H:%M:%S', SH.create_time) AS create_time
                FROM STOCK_INFO_WLW SIW
                LEFT JOIN STOCK_HOLDING SH
                ON SIW.STOCK_NO = SH.STOCK_CODE
                AND strftime('%Y%m%d', SH.REPORT_DATE) = '{reportDate}'
                LEFT JOIN (SELECT STOCK_NO, 
                                 group_concat(STOCK_TYPE_LNAME, ',') AS STOCK_TYPE_NAME,
                                 group_concat(STOCK_TYPE, ',') AS STOCK_TYPE
                            FROM STOCK_INFO_QUESTION 
                            GROUP BY STOCK_NO) SIQ
                ON SIW.STOCK_NO = SIQ.STOCK_NO
                """

    where_sql = ' WHERE 1 = 1'

    condition_list = ['=', '>', '<']

    if stockInfoCondition:
        # 交易日期
        if conditionString(stockInfoCondition.saleDayFrom):
            where_sql += f" AND strftime('%Y%m%d', SIW.STOCK_DATE) >= '{stockInfoCondition.saleDayFrom}'"
        if conditionString(stockInfoCondition.saleDayTo):
            where_sql += f" AND strftime('%Y%m%d', SIW.STOCK_DATE) <= '{stockInfoCondition.saleDayTo}'"

        # 股票No
        if conditionString(stockInfoCondition.stockNo):
            if stockInfoCondition.saleDateType == 'D':
                where_sql += f" AND SIW.STOCK_NO LIKE '{stockInfoCondition.stockNo}%'"
            elif stockInfoCondition.saleDateType == 'M':
                where_sql += f" AND SIW.STOCK_NO in ({stockInfoCondition.stockNo})"

        # 股票名称
        if conditionString(stockInfoCondition.stockName):
            where_sql += f" AND SIW.STOCK_NAME LIKE '%{stockInfoCondition.stockName}%'"

        # 连板数
        if conditionString(stockInfoCondition.lianBanShu):
            where_sql += f" AND SIW.LIAN_BAN_SHU {condition_list[stockInfoCondition.condition_lbs]} '{stockInfoCondition.lianBanShu}'"

        # 换手率
        if conditionString(stockInfoCondition.huanShouLv):
            where_sql += f" AND SIW.HUAN_SHOU_LV {condition_list[stockInfoCondition.condition_hsl]} '{stockInfoCondition.huanShouLv}'"

        # 涨停次数
        if conditionString(stockInfoCondition.zhangTingCiShu):
            where_sql += f" AND SIW.ZHANG_TING_TOTAL {condition_list[stockInfoCondition.condition_ztcs]} '{stockInfoCondition.zhangTingCiShu}'"

        # 游资有无
        if conditionString(stockInfoCondition.youZiYouWu):
            youzi_list = ['全部', '有', '无']
            if stockInfoCondition.youZiYouWu != 0:
                where_sql += f" AND SIW.YOU_ZI_YOU_WU = '{youzi_list[stockInfoCondition.youZiYouWu]}'"

        # 所属行业
        if conditionString(stockInfoCondition.suoShuHangYe):
            where_sql += f" AND SIW.SUO_SHU_HANG_YE like '%{stockInfoCondition.suoShuHangYe}%'"

        # 炸板次数
        if conditionString(stockInfoCondition.zhaBanCiShu):
            where_sql += f" AND SIW.ZHA_BAN_CI_SHU {condition_list[stockInfoCondition.condtion_zbcs]} '{stockInfoCondition.zhaBanCiShu}'"

        # 风险类型
        if conditionString(stockInfoCondition.stockType) and stockInfoCondition.stockType != 0:
            where_sql += f" AND COALESCE(SIQ.STOCK_TYPE, '7') like '%{stockInfoCondition.stockType}%'"

        # 最新价
        if conditionString(stockInfoCondition.le_zxj):
            where_sql += f" AND SIW.ZUI_XING_JIA {condition_list[stockInfoCondition.condition_zxj]} '{stockInfoCondition.le_zxj}'"

        # 涨停主题
        if conditionString(stockInfoCondition.le_ztzt):
            where_sql += f" AND SIW.LIMIT_TITLE like '%{stockInfoCondition.le_ztzt}%'"

    # 检索SQL文
    select_sql = show_sql + where_sql + stockInfoCondition.orderByOption
    logger.info(f'检索SQL：{select_sql}')
    return db.process_stock_data_select(select_sql)


def conditionString(strValue : str = ''):
    if strValue == None or strValue == '':
        return False
    return True

def editSuoShuHangYeAndSort(showStockData, formWigdet):
    if showStockData:
        commonColumns = ['交易日期', '所属行业', '股票No', '名称', '涨跌幅(%)', '最新价(元)', '连板数', '炸板次数', '风险种类', '游资有无', '成交额(亿)',
         '换手率(%)', 'F封板时间', 'L封板时间', '封板资金', '涨停统计', '涨停主题', '涨停原因', '机构持股数量', '数据URL', 'F10URL', '可视化报告', 'hidden']
        pandasData = pandas.DataFrame(data=showStockData, columns=commonColumns)
        # 以股票No为条件删除重复行，默认保留第一次出现的行:drop_duplicates
        # groupZhangTingZhuTi = pandasData.drop_duplicates(subset=['股票No']).groupby(by='涨停主题')
        # 按交易日期降序排列后，取每个股票No第一次出现的数据（即最新日期）
        groupZhangTingZhuTi = (
            pandasData
            .sort_values('交易日期', ascending=False)  # 先按日期降序
            .drop_duplicates(subset=['股票No'])  # 保留每个股票最新记录
            .groupby(by='涨停主题')  # 按涨停主题分组
        )
        sortGroupSuoShuHangYe = []

        # 检索条件
        # saleDateFrom = DateTimeUtils.Format_changed(formWigdet.saleDateFrom.text(), '%Y年%M月%d日', '%Y%M%d')
        # saleDateTo = DateTimeUtils.Format_changed(formWigdet.saleDateTo.text(), '%Y年%M月%d日', '%Y%M%d')
        sortGroupSuoShuHangYeColumns = ['涨停主题', '数量', '股票名称', '现价', '涨幅', '股票No', '数据URL', 'F10URL', '可视化报告', 'DATA']

        for zhangTingZhuTi, groupbyCol in groupZhangTingZhuTi:
            num = len(groupbyCol)
            sortXianJiaData = groupbyCol.sort_values(by=['涨跌幅(%)', '最新价(元)'], ascending=False)
            stockNames = {row['股票No']: row['名称'] for _, row in sortXianJiaData.iterrows()}
            stockXianJia = {row['股票No']: row['最新价(元)'] for _, row in sortXianJiaData.iterrows()}
            stockZhangFu = {row['股票No']: row['涨跌幅(%)'] for _, row in sortXianJiaData.iterrows()}
            stockDepthDataUrls = {row['股票No']: row['数据URL'] for _, row in sortXianJiaData.iterrows()}
            stockF10Urls = {row['股票No']: row['F10URL'] for _, row in sortXianJiaData.iterrows()}
            stockReportchartUrls = {row['股票No']: row['可视化报告'] for _, row in sortXianJiaData.iterrows()}
            stockNos = [f"'{stockNo}'" for stockNo in sortXianJiaData['股票No']]
            stockNo = ', '.join(stockNos)
            # 20251105 START 保留股票NO其它检索条件删除
            # stockInfoCondition = StockInfoCondition(saleDateFrom, saleDateTo, stockNo, '', lianBanShu,
            #                                             huanShouLv, zhangTingCiShu, youZiYouWu,
            #                                             '', zhaBanCiShu,
            #                                             stockType, zhangTingZhuTi, le_zxj, condition_zxj,
            #                                 condition_lbs, condition_hsl, condition_ztcs, condtion_zbcs, 'M', ' ORDER BY SIW.ZUI_XING_JIA DESC')
            stockInfoCondition = StockInfoCondition('', '', stockNo, '', '',
                                                    '', '', '',
                                                    '', '',
                                                    '', '', '', '',
                                                    '', '', '', '', 'M',
                                                    ' ORDER BY SIW.ZUI_XING_JIA DESC')
            # 20251105 END
            stockInfoDatas = getStockInfoWLWData(stockInfoCondition)
            pandasStockInfoData = pandas.DataFrame(data=stockInfoDatas, columns=commonColumns)
            sortGroupSuoShuHangYe.append([zhangTingZhuTi, num, stockNames, stockXianJia, stockZhangFu, stockNos, stockDepthDataUrls, stockF10Urls, stockReportchartUrls, pandasStockInfoData])

        pandasSortData = pandas.DataFrame(data=sortGroupSuoShuHangYe, columns=sortGroupSuoShuHangYeColumns).sort_values(by='数量', ascending=False)
        return pandasSortData
    return pandas.DataFrame()

if __name__ == '__main__':
    stockInfoCondition = StockInfoCondition('20250601', '20250630', '', '', '', '', '','', '', '', '', 'D', '')
    data = getStockInfoWLWData(stockInfoCondition)
    if (data):
        historyHolidays = [[row[0], row[1], row[2], row[3], row[4], row[5],
                            row[6], row[7], row[8], row[9], row[10], row[11],
                            row[12], row[13]] for row in data]
        for row, va in enumerate(historyHolidays):
            print(type[row], type(va), va)
