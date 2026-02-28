# _*_ coding: utf-8 _*_
# @Time : 2025/6/25 0025 15:24
# @Author : 韦丽
# @Version: V 1.0
# @File : UserMemoryModel.py
# @desc : 用户记忆操作
from WLW.StockBase import DateTimeUtils

from WLW.StockBase.sqlite_db import SQLiteDB

db = SQLiteDB()

def getDataInterval(mac_address: str = ''):
    sql = f"""select username, password from USER_MEMORY where mac_address = '{mac_address}' AND option_type = 'CheckState.Checked'"""
    data = db.process_stock_data_select(sql)
    result = {}
    if len(data) == 1:
        result = {'username': data[0][0], 'password': data[0][1]}
    return result

def insert(data_list):
    tableName = 'USER_MEMORY'
    insert_columns = ['username', 'password', 'mac_address', 'option_type']

    if data_list:
        operation_type = data_list[0][2]
        # 先删除旧数据
        condition = f"mac_address = '{operation_type}' "
        # print(f'Delete condition: {condition}')
        return db.process_stock_data_insert(tableName, condition, insert_columns, data_list)
