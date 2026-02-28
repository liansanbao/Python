# _*_ coding: utf-8 _*_
# @Time : 2025/6/25 0025 15:24
# @Author : 韦丽
# @Version: V 1.0
# @File : DataOpreationModel.py
# @desc :
from WLW.StockBase import DateTimeUtils

from WLW.StockBase.sqlite_db import SQLiteDB

db = SQLiteDB()

def getDataInterval(operation_type: str = ''):
    sql = f"""select interval from DATA_OPERATION where operation_type = '{operation_type}'"""
    data = db.process_stock_data_select(sql)
    if len(data) == 1:
        return data[0][0]
    return 0

def insert(saleDay, data_list):
    tableName = 'DATA_OPERATION'
    insert_columns = ['system_date', 'interval', 'operation_type', 'insert_date', 'update_date']
    # 日期
    if saleDay == '':
        saleDay = DateTimeUtils.saleDate()

    if data_list:
        operation_type = data_list[0][2]
        # 先删除旧数据
        condition = f"operation_type = '{operation_type}' "
        # print(f'Delete condition: {condition}')
        return db.process_stock_data_insert(tableName, condition, insert_columns, data_list)
