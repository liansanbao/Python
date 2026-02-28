from WLW.StockBase.sqlite_db import SQLiteDB
from WLW.Tools.LoggingEx import logger
from WLW.model.WaringStockCondition import WaringStockCondition

# SHowWLW执行时的设定
db = SQLiteDB()

def getWaringStockWLWData(waringStockCondition):
    # 检索SQL
    show_sql = f"""
        Select NSIQ.STOCK_NO,
               NSIQ.STOCK_NA,
               strftime('%Y-%m-%d', NSIQ.C_DATE) as C_DATE,
               LTRIM(NSIQ.SUO_SHU_HANG_YE, ',') as SUO_SHU_HANG_YE,
               NSIQ.STOCK_TYPE_NAME,
               strftime('%Y年%m月%d日', NSIQ.U_DATE) as U_DATE,
               LTRIM(NSIQ.AN_QUAN_FENG, ',') as AN_QUAN_FENG,
               COALESCE(NSIQ.YU_JING_TYPE, '') AS YU_JING_TYPE,
               TRIM(NSIQ.YU_JING_XIANG_QI, ',') AS YU_JING_XIANG_QI
               FROM (SELECT STOCK_NO, C_DATE,U_DATE,STOCK_NA,
                                 GROUP_CONCAT(STOCK_TYPE_LNAME) AS STOCK_TYPE_NAME,
                                 GROUP_CONCAT(STOCK_TYPE) AS STOCK_TYPE,
                                 GROUP_CONCAT(DISTINCT YU_JING_XIANG_QI) AS YU_JING_XIANG_QI,
                                 GROUP_CONCAT(DISTINCT YU_JING_TYPE) AS YU_JING_TYPE,
                                 GROUP_CONCAT(DISTINCT AN_QUAN_FENG) AS AN_QUAN_FENG,
                                 GROUP_CONCAT(DISTINCT SUO_SHU_HANG_YE) AS SUO_SHU_HANG_YE
                            FROM STOCK_INFO_QUESTION 
                            GROUP BY STOCK_NO) NSIQ
                """

    where_sql = ' WHERE 1 = 1'
    if waringStockCondition:
        # 个股日期From
        if conditionString(waringStockCondition.cDateFrom):
            where_sql += f" AND strftime('%Y%m%d', NSIQ.C_DATE) >= '{waringStockCondition.cDateFrom}'"
        # 个股日期To
        if conditionString(waringStockCondition.cDateTo):
            where_sql += f" AND strftime('%Y%m%d', NSIQ.C_DATE) <= '{waringStockCondition.cDateTo}'"

        # 股票No
        if conditionString(waringStockCondition.waringStockNo):
            where_sql += f" AND NSIQ.STOCK_NO LIKE '%{waringStockCondition.waringStockNo}%'"

        # 股票名称
        if conditionString(waringStockCondition.waringStockName):
            where_sql += f" AND NSIQ.STOCK_NA LIKE '%{waringStockCondition.waringStockName}%'"

        # 风险种类
        if conditionString(waringStockCondition.waringStockType) and waringStockCondition.waringStockType != 0:
            where_sql += f" AND NSIQ.STOCK_TYPE LIKE '%{waringStockCondition.waringStockType}%'"

        # 所属行业
        if conditionString(waringStockCondition.waringHangYe):
            where_sql += f" AND NSIQ.SUO_SHU_HANG_YE LIKE '%{waringStockCondition.waringHangYe}%'"


    # 检索SQL文
    select_sql = show_sql + where_sql + waringStockCondition.orderByOption
    # print(f'检索SQL：{select_sql}')
    logger.info(f'select_sql : {select_sql}')

    return db.process_stock_data_select(select_sql)

def conditionString(strValue : str = ''):
    if strValue == None or strValue == '':
        return False
    return True

if __name__ == '__main__':
    waringStockCondition = WaringStockCondition('20250101', '20251231', '', '', '', '', '')
    data = getWaringStockWLWData(waringStockCondition)
    print(len(data))
    if (data):
        historyHolidays = [[row] for row in data]
        for row, va in enumerate(historyHolidays):
            print(type[row], type(va), va)
