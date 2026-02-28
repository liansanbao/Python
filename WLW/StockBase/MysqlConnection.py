# _*_ coding: utf-8 _*_
# @Time : 2025/7/24 星期四 23:29
# @Author : 韦丽
# @Version: V 1.0
# @File : MysqlConnection.py
# @desc :
import platform
import json

# import pymysql

if platform.system() == 'Windows':
    import MySQLdb
elif platform.system() == 'Linux':
    import mysql.connector

with open('_internal/config/db_config.json') as f:
    config = json.load(f)


# 创建db连接
def connect_to_mysql(dbname: str='sys'):
    try:
        if platform.system() == 'Windows':
            connection = MySQLdb.connect(
                host=config['database']['Host'],
                user=config['database']['User'],
                password=config['database']['Password'],
                database=config['database']['dbname']
            )
            # connection = pymysql.connect(
            #     host=config['database']['Host'],
            #     port=3306,
            #     user=config['database']['User'],
            #     password=config['database']['Password'],
            #     db=config['database']['dbname'],
            #     charset='utf8mb4',
            #     cursorclass=pymysql.cursors.DictCursor
            # )
        elif platform.system() == 'Linux':
            connection = mysql.connector.connect(
                host=config['database']['Host'],
                user=config['database']['User'],
                password=config['database']['Password'],
                database=config['database']['dbname']
            )

        if connection:
            # print('成功连接到数据库')
            return connection

    except Exception as err:
        # print(f'连接错误：{err}')
        return None

# 创建数据库
def create_database(curson, database_name):
    try:
        curson.execute(f'CREATE DATABASE {database_name}')
        print(f'数据库 {database_name} 创建成功')
    except Exception as err:
        print(f'连接错误：{err}')

# 表创建
def create_table(cursor, tableSql):
    try:
        cursor.execute(tableSql)
        print(f'表 {tableSql} 创建成功')
    except Exception as err:
        print(f'表创建错误：{err}')

# 数据插入(1条)
def insert_data(cursor, insertSql, data):
    try:
        cursor.execute(insertSql, data)
        print(f'{cursor.rowcount}件数据插入成功')
    except Exception as err:
        print(f'{cursor.rowcount}件数据插入：{err}')

# 数据插入(多条)
def insert_data_list(cursor, insertSql, data_list):
    try:
        print(f'insertSql: {insertSql}')
        cursor.executemany(insertSql, data_list)
        print(f'{cursor.rowcount}件数据插入成功')
    except Exception as err:
        print(f'{cursor.rowcount}件数据插入错误：{err}')

# 无条件查询
def select_data(cursor, selectSql):
    try:
        cursor.execute(selectSql)
        # result = cursor.fetchall()
        # for row in result:
        #     print(row)
        return cursor.fetchall()
    except Exception as err:
        print(f'无条件查询数据错误：{err}')

# 条件查询
def select_data_with_condition(cursor, selectSql):
    try:
        cursor.execute(selectSql)
        # result = cursor.fetchall()
        # for row in result:
        #     print(row)

        return cursor.fetchall()
    except Exception as err:
        print(f'条件查询数据错误：{err}')

# 条件更新
def update_data_with_condition(cursor, updateSql):
    try:
        row = cursor.execute(updateSql)
    except Exception as err:
        print(f'数据更新错误：{err}')

# 条件更新
def delete_data_with_condition(cursor, deleteSql, tableName):
    try:
        cursor.execute(deleteSql)
        print(f'表{tableName}有{cursor.rowcount}件数据删除成功')
    except Exception as err:
        print(f'表{tableName}有{cursor.rowcount}件数据删除错误：{err}')

def mysqlConnection():
    return connect_to_mysql()

if __name__ == '__main__':
    connect = mysqlConnection()
    print(connect)
    connect.close()
