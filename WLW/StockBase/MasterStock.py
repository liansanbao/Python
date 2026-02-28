import pandas as pd

from WLW.StockBase import DateTimeUtils
from WLW.StockBase.sqlite_db import SQLiteDB
from WLW.Tools.LoggingEx import logger

'''
分析主力资金分布情况
操作手法：
    1.通达信中单击发现菜单
    2.单击行情统计--市场表现--A股表现
    3.点击涨幅%降序排列
    4.右击鼠标--数据导出

'''
# 数据插入
insert_columns = ['STOCK_NO',
                   'STOCK_NAME',
                   'ZHANG_FU',
                   'XIAN_JIA',
                   'HANG_QING_DATE',
                   'SHOU_PAN_JIA',
                   'DAY_CHENG_JIAO_E',
                   'DAY_5_ZHANG_FU',
                   'DAY_5_CHENG_JIAO_E',
                   'DAY_20_ZHANG_FU',
                   'DAY_60_ZHANG_FU',
                   'MONTH_ZHANG_FU',
                   'YEAR_ZHANG_FU',
                   'SHI_YING_LV',
                   'ZONG_SHI_ZHI',
                   'HANG_YE']

def exec(paraFilePath: str = ''):
    data = load(paraFilePath)
    data_list = editData(data)
    insertASIW(data_list)

def load(paraFilePath: str = ''):
    logger.info('分析开始：')
    if paraFilePath != '':
        try:
            with open(paraFilePath, mode='r', encoding='936') as r:
                dataContent = r.readlines()

            titles = []
            cols = []
            for no, col in enumerate(dataContent):
                newClo = col.replace('\n','').replace('="','').replace('"','').split('	')
                if newClo[2].startswith('ST') or newClo[2].startswith('*ST') or newClo[3] == '-- ' or newClo[4] == '-- ' or newClo[5] == '-- ':
                    continue

                if no == 0:
                    newClo[0] = 'Sort'
                    titles = newClo
                else:
                    if float(newClo[3]) < -2:
                        continue
                    cols.append(newClo)

            data = cols
            titles = titles
            # 数据转pandas模式
            pandasData = pd.DataFrame(cols)
            pandasData.columns = titles
            pandasData["涨幅%"] = pd.to_numeric(pandasData["涨幅%"], errors="coerce")
            #sortData = pandasData.sort_values(by='涨幅%', ascending=False)
            groupHangye = pandasData.groupby(by='行业')
            groupHangyeTitle = ['行业名称', '行业数量']
            groupTotalData = []
            for name, groupContent in groupHangye:
                groupTotalData.append([name, len(groupContent)])

            groupTotalPandas = pd.DataFrame(groupTotalData)
            groupTotalPandas.columns = groupHangyeTitle
            groupTotalPandasSort = groupTotalPandas.sort_values(by='行业数量', ascending=False)

            conditionData = {}
            topCount = 5
            for index in groupTotalPandasSort.index:
                if topCount == 0:
                    break
                conditionData[groupTotalPandasSort.loc[index, '行业名称']] = int(groupTotalPandasSort.loc[index, '行业数量'])
                topCount -= 1

            return data
        except Exception as ex:
            logger.error(ex)

def editData(data):
    data_list = []

    for rowContent in data:
        # 交易日期
        sale_date = DateTimeUtils.Format_date(ymd=str(rowContent[5]), format='%Y-%m-%d')

        rowdata = (
            rowContent[1],
            rowContent[2],
            convertFloat(value = rowContent[3]),
            convertFloat(value = rowContent[4]),
            sale_date,
            convertFloat(value = rowContent[6]),
            rowContent[7],
            convertFloat(value = rowContent[8]),
            rowContent[9],
            convertFloat(value = rowContent[10]),
            convertFloat(value = rowContent[11]),
            convertFloat(value = rowContent[12]),
            convertFloat(value = rowContent[13]),
            convertFloat(value = rowContent[14]),
            rowContent[15],
            rowContent[16]
        )
        data_list.append(rowdata)
    return data_list

def convertFloat(value:object):
    try:
        return float(value)
    except Exception as ex:
        logger.error('convertFloat Error:', ex)
    return 0.0

def insertASIW(data_list):
    db = SQLiteDB()
    tableName = 'A_STOCK_INFO_WLW'
    sale_date = DateTimeUtils.nowDate().strftime('%Y-%m-%d')
    if data_list:
        # 数据删除
        condition = f"HANG_QING_DATE = '{sale_date}'"
        db.process_stock_data_insert(tableName, condition, insert_columns, data_list)



# if __name__ == '__main__':
#     exec(paraFilePath='A_20250228.xls')

