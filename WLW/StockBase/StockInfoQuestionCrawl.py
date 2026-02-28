from WLW.StockBase.sqlite_db import SQLiteDB
from WLW.Tools.LoggingEx import logger
from WLW.StockBase import DateTimeUtils

'''问题股票信息表数据采集'''
# 风险类型
risk = ['无风险','频发风险','触发风险','商誉风险','近期解禁','退市风险','立案调查']
risk_jc = ['正常','频','触','誉','禁','退','案']
# 数据插入
insert_columns = ['STOCK_NO', 'STOCK_NA', 'STOCK_TYPE', 'STOCK_TYPE_LNAME', 'YU_JING_TYPE', 'YU_JING_XIANG_QI', 'AN_QUAN_FENG', 'SUO_SHU_HANG_YE', 'U_DATE', 'C_DATE']

def exec(paraFilePath: str = '', fileType = ''):
    data = load(paraFilePath)
    data_list = editData(data, fileType)
    insertASIW(data_list, fileType)

def load(paraFilePath: str = ''):
    cols = []
    if paraFilePath != '':
        try:
            with open(paraFilePath, mode='r', encoding='936') as r:
                dataContent = r.readlines()

            for no, col in enumerate(dataContent):
                newClo = col.replace('\n', '').replace('="', '').replace('"', '').split('	')
                if newClo[2].startswith('ST') or newClo[2].startswith('*ST') :
                    continue

                if no == 0:
                    newClo[0] = 'Sort'
                else:
                    cols.append(newClo)

        except Exception as ex:
            logger.info(ex)

    return cols

def editData(data, fileType):
    data_list = []
    stock_type = risk.index(fileType)
    stock_type_lname = risk_jc[stock_type]
    # 更新/新规日期
    new_date = DateTimeUtils.nowDateTime().strftime('%Y-%m-%d')

    for rowContent in data:
        # 风险种类(0:无风险 1:频发风险 2:触发风险 3:商誉风险 4:近期解禁 5:退市风险 6:立案调查)
        if stock_type in [1, 2]:
            rowdata = (
                rowContent[1],
                rowContent[2],
                stock_type,
                stock_type_lname,
                rowContent[7],
                rowContent[8],
                convertFloat(value=rowContent[9]),
                rowContent[10],
                new_date,
                new_date
            )
        elif stock_type == 3:
            rowdata = (
                rowContent[1],
                rowContent[2],
                stock_type,
                stock_type_lname,
                '',
                '',
                0,
                rowContent[16],
                new_date,
                new_date
            )
        elif stock_type == 4:
            rowdata = (
                rowContent[1],
                rowContent[2],
                stock_type,
                stock_type_lname,
                '',
                rowContent[10],
                0,
                '',
                new_date,
                new_date
            )
        elif stock_type == 5:
            rowdata = (
                rowContent[1],
                rowContent[2],
                stock_type,
                stock_type_lname,
                rowContent[5],
                rowContent[6],
                0,
                '',
                new_date,
                new_date
            )
        elif stock_type == 6:
            rowdata = (
                rowContent[1],
                rowContent[2],
                stock_type,
                stock_type_lname,
                rowContent[7],
                rowContent[8],
                0,
                rowContent[11],
                new_date,
                new_date
            )
        data_list.append(rowdata)
        logger.info(f'data_list: {data_list}')
    return data_list

def convertFloat(value: object):
    try:
        return float(value)
    except Exception as ex:
        # print('convertFloat Error:', ex)
        pass
    return 0.0

def insertASIW(data_list, fileType):
    db = SQLiteDB()
    stock_type = risk.index(fileType)
    tableName = 'STOCK_INFO_QUESTION'
    if data_list:
        # 数据删除
        condition = f"STOCK_TYPE = '{stock_type}'"
        db.process_stock_data_insert(tableName, condition, insert_columns, data_list)

@staticmethod
def getAll():
    db = SQLiteDB()
    tableName = 'STOCK_INFO_QUESTION'
    # 数据查询
    select_sql = f""" SELECT * FROM {tableName}  """
    resutlData = db.process_stock_data_select(select_sql)
    return resutlData

if __name__ == '__main__':
    # for type in StockInfoQuestion.risk:
    #     if type == '无风险':
    #         continue
    #     stockInfoQuestion = StockInfoQuestion(paraFilePath=f'{type}_20250124.xls', fileType=type)
    #     stockInfoQuestion.editData()
    #     stockInfoQuestion.insertASIW()
    # stockInfoQuestion = StockInfoQuestion(paraFilePath='频发风险_20250124.xls', fileType='频发风险')
    exec(paraFilePath='立案调查_20250611.xls', fileType='立案调查')


    # columns = ['主键', '股票代码', '股票名称', '风险种类(0:无风险 1:频发风险 2:触发风险 3:商誉风险 4:近期解禁 5:退市风险 6:立案调查)', '更新时间', '新建时间', '安全分', '所属行业', '预警类型', '预警详情']
    resutlData = getAll()
    # print(resutlData[0])
    # resultPandas = pd.DataFrame(resutlData)
    # resultPandas.columns = columns
    # groupbyData = resultPandas.groupby(by='所属行业')
    # for name, groupbyCol in groupbyData:
    #     print(groupbyCol)
    #     num = len(groupbyCol)
    #     print(name, num)
