import akshare as ak
from WLW.StockBase import DateTimeUtils
from WLW.StockBase.sqlite_db import SQLiteDB
from WLW.Tools.LoggingEx import logger

# SHowWLW执行时的设定
db = SQLiteDB()

def exec(saleDay:str = ''):
    data_list = []

    # 日期
    if saleDay == '':
        saleDay = DateTimeUtils.saleDate()

    # --------------------------------------------------
    # 东方财富-个股人气榜-人气榜
    # --------------------------------------------------
    logger.info(f'检索日期：{saleDay}')

    # 涨停板行情
    stock_zt_pool_em = ak.stock_zt_pool_em(date=saleDay)
    if len(stock_zt_pool_em) > 0:
        zhangfu_list = stock_zt_pool_em.sort_values(by='涨跌幅', ascending=False)
        logger.info(f"今日[{saleDay}]有{zhangfu_list.size}个股票涨停。")
        # 删除ST开头的股票
        for rowNo in zhangfu_list.index:
            # 判断股票名称是否以ST开头
            if zhangfu_list.loc[rowNo, '名称'].startswith('ST') or zhangfu_list.loc[rowNo, '名称'].startswith('*ST'):
                # print(f"ST：{zhangfu_list.loc[rowNo, '名称']}")
                zhangfu_list.drop(rowNo, inplace=True)

        # 添加列名
        zhangfu_list['游资有无'] = {}
        # 向添加列中加入值
        for rowNo in zhangfu_list.index:
            try:
                zhangfu_list.loc[rowNo, '游资有无'] = '有'
            except (Exception) as e:
                try:
                    zhangfu_list.loc[rowNo, '游资有无'] = '有'
                except (Exception) as e:
                    zhangfu_list.loc[rowNo, '游资有无'] = '无'

        logger.info(f"处理数据：{len(zhangfu_list)} 件")

        # 交易日期
        sale_date = DateTimeUtils.Format_date(ymd = saleDay, format ='%Y-%m-%d')

        for rowNo in zhangfu_list.index:
            rowdata = (
                sale_date,
                zhangfu_list.loc[rowNo, '代码'],
                zhangfu_list.loc[rowNo, '名称'].ljust(7),
                float(round(zhangfu_list.loc[rowNo, '涨跌幅'], 2)),
                float(zhangfu_list.loc[rowNo, '最新价']),
                int(zhangfu_list.loc[rowNo, '连板数']),
                zhangfu_list.loc[rowNo, '所属行业'],
                zhangfu_list.loc[rowNo, '游资有无'],
                float(round(zhangfu_list.loc[rowNo, '成交额'] / 100000000, 2)),
                float(round(zhangfu_list.loc[rowNo, '换手率'], 2)),
                DateTimeUtils.format_hms(hms= zhangfu_list.loc[rowNo, '首次封板时间']),
                DateTimeUtils.format_hms(hms= zhangfu_list.loc[rowNo, '最后封板时间']),
                float(round(zhangfu_list.loc[rowNo, '封板资金'] / 10000, 0)),
                zhangfu_list.loc[rowNo, '涨停统计'],
                int(zhangfu_list.loc[rowNo, '炸板次数'])
            )
            data_list.append(rowdata)

        logger.info(f"DB处理数据：{len(data_list)} 件")
    else:
        logger.info(f'{saleDay}数据没有！')

    return data_list

def insert(saleDay, data_list):
    # 数据插入
    insert_columns = [
        'STOCK_DATE',
        'STOCK_NO',
        'STOCK_NAME',
        'ZHANG_DIE_FU',
        'ZUI_XING_JIA',
        'LIAN_BAN_SHU',
        'SUO_SHU_HANG_YE',
        'YOU_ZI_YOU_WU',
        'CHENG_JIAO_E',
        'HUAN_SHOU_LV',
        'FIRST_FENG_BAN_TIME',
        'LAST_FENG_BAN_TIME',
        'FENG_BAN_JIN_E',
        'ZHANG_TING_TOTAL',
        'ZHA_BAN_CI_SHU'
    ]
    # 日期
    if saleDay == '':
        saleDay = DateTimeUtils.saleDate()

    # 数据操作
    if data_list:
        tableName = 'STOCK_INFO_WLW'
        # 交易日期
        sale_date = DateTimeUtils.Format_date(ymd=saleDay, format='%Y-%m-%d')
        stock_nos = [f"'{col[1]}'" for col in data_list]
        # 先删除旧数据
        condition = f"STOCK_DATE = '{sale_date}' AND STOCK_NO IN ({', '.join(stock_nos)}) "
        # print(f'Delete condition: {condition}')
        return db.process_stock_data_insert(tableName, condition, insert_columns, data_list)

if __name__ == "__main__":
    flag = exec(saleDay='20250620', tableName='STOCK_INFO_WLW')
    print(f'inset suess: {flag}')

    sql = '''
        SELECT strftime('%Y年%m月%d日', SIW.STOCK_DATE) AS formatted_date,
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
                       SIW.ZHANG_TING_TOTAL
                FROM STOCK_INFO_WLW SIW
                LEFT JOIN (SELECT STOCK_NO, 
                                 group_concat(STOCK_TYPE_LNAME, ',') AS STOCK_TYPE_NAME,
                                 group_concat(STOCK_TYPE, ',') AS STOCK_TYPE
                            FROM STOCK_INFO_QUESTION 
                            GROUP BY STOCK_NO) SIQ
                ON SIW.STOCK_NO = SIQ.STOCK_NO
                 WHERE 1 = 1 AND strftime('%Y%m%d', SIW.STOCK_DATE) >= '20250616' AND strftime('%Y%m%d', SIW.STOCK_DATE) <= '20250622' ORDER BY SIW.SUO_SHU_HANG_YE   DESC
    '''
    resutl = db.process_stock_data_select(sql)
    print(resutl)
