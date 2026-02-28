# _*_ coding: utf-8 _*_
# @Time : 2025/6/22 0022 13:35
# @Author : 韦丽
# @Version: V 1.0
# @File : sqlite_db.py
# @desc : sqlite数据库操作
import os
import sqlite3
from typing import List, Tuple

from WLW.Tools.LoggingEx import logger

class DatabaseHandler:
    STOCK_INFO_WLW = """
            CREATE TABLE STOCK_INFO_WLW (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                STOCK_DATE TEXT NOT NULL,
                STOCK_NO TEXT NOT NULL,
                STOCK_NAME TEXT,
                ZHANG_DIE_FU REAL,
                ZUI_XING_JIA REAL,
                LIAN_BAN_SHU INTEGER,
                SUO_SHU_HANG_YE TEXT,
                YOU_ZI_YOU_WU TEXT,
                CHENG_JIAO_E REAL,
                HUAN_SHOU_LV REAL,
                FIRST_FENG_BAN_TIME TEXT,
                LAST_FENG_BAN_TIME TEXT,
                FENG_BAN_JIN_E REAL,
                ZHANG_TING_TOTAL TEXT,
                ZHA_BAN_CI_SHU INTEGER NOT NULL,
                LIU_TONG_SHI_ZHI REAL,
                ZONG_SHI_ZHI REAL,
                LIMIT_TITLE TEXT,
                LIMIT_WHY TEXT,
                CONCEPT TEXT,
                DEPTHDATAURL TEXT,
                F10URL TEXT,
                REPORTCHARTURL TEXT,
                UNIQUE (STOCK_DATE, STOCK_NO)
            );
            """
    DATA_OPERATION = """
                CREATE TABLE DATA_OPERATION (
                    id             INTEGER   PRIMARY KEY AUTOINCREMENT,
                    system_date    DATE      NOT NULL,
                    interval       INTEGER   NOT NULL,
                    operation_type TEXT,
                    insert_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    update_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
    STOCK_INFO_QUESTION = """
            CREATE TABLE STOCK_INFO_QUESTION (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                STOCK_NO TEXT NOT NULL,
                STOCK_NA TEXT NOT NULL,
                STOCK_TYPE INTEGER NOT NULL,
                STOCK_TYPE_LNAME TEXT,
                U_DATE TEXT NOT NULL,
                C_DATE TEXT NOT NULL,
                AN_QUAN_FENG INTEGER NOT NULL,
                SUO_SHU_HANG_YE TEXT,
                YU_JING_TYPE TEXT,
                YU_JING_XIANG_QI TEXT
            );
            """
    China_Holidays = """
            CREATE TABLE China_Holidays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER,
                month INTEGER,
                holidays TEXT NOT NULL,
                holidays_content TEXT NOT NULL
            );
            """
    ZJLX_CRAWL = """
            CREATE TABLE ZJLX_CRAWL (
              ID INTEGER PRIMARY KEY AUTOINCREMENT,
              HANG_QING_DATE TEXT NOT NULL,
              STOCK_NO TEXT NOT NULL,
              STOCK_NAME TEXT DEFAULT NULL,
              ZHANG_FU REAL,
              XIAN_JIA REAL,
              F62 TEXT DEFAULT NULL,
              F184 TEXT DEFAULT NULL,
              F66 TEXT DEFAULT NULL,
              F69 TEXT DEFAULT NULL,
              F72 TEXT DEFAULT NULL,
              F75 TEXT DEFAULT NULL,
              F78 TEXT DEFAULT NULL,
              F81 TEXT DEFAULT NULL,
              F84 TEXT DEFAULT NULL,
              F87 TEXT DEFAULT NULL,
              HANG_YE TEXT DEFAULT NULL,
              DEPTHDATAURL TEXT,
              F10URL TEXT,
              REPORTCHARTURL TEXT,
              UNIQUE (STOCK_NO, HANG_QING_DATE)
            );
            """
    USER_MEMORY = """
            CREATE TABLE IF NOT EXISTS USER_MEMORY (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                mac_address TEXT NOT NULL,
                option_type TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """
    GRIDIST_STOCK = """
            CREATE TABLE GRIDIST_STOCK (
                CREATE_DATE DATE NOT NULL,
                F12 TEXT NOT NULL,
                F14 TEXT DEFAULT NULL,
                F2 TEXT DEFAULT NULL,
                F3 TEXT DEFAULT NULL,
                F4 TEXT DEFAULT NULL,
                F5 TEXT DEFAULT NULL,
                F6 TEXT DEFAULT NULL,
                F7 TEXT DEFAULT NULL,
                F8 TEXT DEFAULT NULL,
                F9 TEXT DEFAULT NULL,
                F10 TEXT DEFAULT NULL,
                F15 TEXT DEFAULT NULL,
                F16 TEXT DEFAULT NULL,
                F17 TEXT DEFAULT NULL,
                F18 TEXT DEFAULT NULL,
                F23 TEXT DEFAULT NULL,
                hybk TEXT DEFAULT NULL,
                DEPTHDATAURL TEXT,
                F10URL TEXT,
                REPORTCHARTURL TEXT,
                PRIMARY KEY(F12, CREATE_DATE)
            );
            """
    STOCK_HOLDING = """
            CREATE TABLE STOCK_HOLDING (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                STOCK_CODE TEXT NOT NULL,
                STOCK_NAME TEXT NOT NULL,
                REPORT_DATE DATE NOT NULL,
                INDUSTRY TEXT,
                INSTITUTION_COUNT INTEGER,
                HOLDING_QUANTITY DECIMAL(12,2),
                HOLDING_VALUE DECIMAL(15,2),
                TOTAL_SHARE_RATIO DECIMAL(5,2),
                FLOAT_SHARE_RATIO DECIMAL(5,2),
                CHANGE_QUANTITY DECIMAL(12,2),
                CHANGE_RATIO DECIMAL(5,2),
                POSITION_TYPE TEXT,
                create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(STOCK_CODE, REPORT_DATE)
            );
            """
    HYZJL_CRAWL = """
            CREATE TABLE HYZJL_CRAWL (
                CREATE_DATE DATE NOT NULL,
                F12 TEXT NOT NULL,
                F14 TEXT,
                F2 TEXT,
                F3 TEXT,
                F62 TEXT,
                F184 TEXT,
                F66 TEXT,
                F69 TEXT,
                F72 TEXT,
                F75 TEXT,
                F78 TEXT,
                F81 TEXT,
                F84 TEXT,
                F87 TEXT,
                F204 TEXT,
                F205 TEXT,
                ActivateType TEXT DEFAULT '1',
                hyType TEXT DEFAULT '1',
                PRIMARY KEY(CREATE_DATE, F12)
            );
        """
    NOTICE_CRAWL = """
                CREATE TABLE NOTICE_CRAWL (
                    ART_CODE TEXT NOT NULL,
                    STOCK_CODE TEXT,
                    STOCK_NAME TEXT,
                    NOTICE_DATE DATE,
                    NOTICE_TYPE TEXT,
                    NOTICE_TITLE TEXT,
                    NOTICE_INFO_URL TEXT,
                    INDUSTRY TEXT,
                    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY(ART_CODE)
                );
            """

    wlw_tables = ['STOCK_INFO_WLW', 'DATA_OPERATION', 'STOCK_INFO_QUESTION', 'China_Holidays', 'ZJLX_CRAWL', 'USER_MEMORY', 'GRIDIST_STOCK', 'STOCK_HOLDING', 'HYZJL_CRAWL', 'NOTICE_CRAWL']

    """创建初始表结构"""
    queries = {
        'STOCK_INFO_WLW': STOCK_INFO_WLW,
        'DATA_OPERATION': DATA_OPERATION,
        'STOCK_INFO_QUESTION': STOCK_INFO_QUESTION,
        'China_Holidays': China_Holidays,
        'ZJLX_CRAWL': ZJLX_CRAWL,
        'USER_MEMORY': USER_MEMORY,
        'GRIDIST_STOCK': GRIDIST_STOCK,
        'STOCK_HOLDING': STOCK_HOLDING,
        'HYZJL_CRAWL': HYZJL_CRAWL,
        'NOTICE_CRAWL': NOTICE_CRAWL
    }

class SQLiteDB:
    # def __init__(self, db_path: str = './_internal/db/wlw.db'): Develop
    def __init__(self, db_path: str='./_internal/config/wlw.db'):
        self.db_path = db_path
        self.connection = None
        self.in_transaction = False
        self.initialize()

    def initialize(self):
        # 判断数据库是否存在，不存在则自动创建
        is_new_db = not os.path.exists(self.db_path)
        if is_new_db:
            self.create_tables(DatabaseHandler.wlw_tables)
        else:
            # 数据库存在，确认表是否存在
            self._single_create_tables()
        # self.close()

    def create_tables(self, tables):
        connection = sqlite3.connect(self.db_path)
        with connection as conn:
            cursor = conn.cursor()
            for key in tables:
                cursor.execute(DatabaseHandler.queries[key])
            cursor.close()

    def _single_create_tables(self):
        db_tables = self.get_all_tables()
        if db_tables:
            new_tables = set(DatabaseHandler.wlw_tables) - set(db_tables)
            # new_tables有值就是需要新规
            if new_tables:
                self.create_tables(new_tables)

    def get_all_tables(self):
        """获取SQLite数据库中所有表名"""
        tables = []
        select_data = self.process_stock_data_select("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        for col in select_data:
            tables.append(col[0])
        return tables

    # 数据库操作 START
    def connect(self) -> bool:
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.isolation_level = None  # 启用显式事务控制
            return True
        except sqlite3.Error as e:
            logger.error(f"connect_SQLite连接失败: {e}")
            return False

    def begin_transaction(self):
        if self.connection and not self.in_transaction:
            self.connection.execute("BEGIN")
            self.in_transaction = True

    def commit_transaction(self):
        if self.connection and self.in_transaction:
            self.connection.execute("COMMIT")
            self.in_transaction = False

    def rollback_transaction(self):
        if self.connection and self.in_transaction:
            self.connection.execute("ROLLBACK")
            self.in_transaction = False

    def execute_query(self, query: str, params: Tuple = None) -> bool:
        try:
            self.begin_transaction()
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.commit_transaction()
            return True
        except sqlite3.Error as e:
            self.rollback_transaction()
            logger.error(f"execute_query_SQL执行失败: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def batch_insert(self, table: str, columns: List[str], data: List[Tuple]) -> bool:
        placeholders = ",".join(["?"] * len(columns))
        columns_str = ",".join(columns)
        query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"

        try:
            self.begin_transaction()
            cursor = self.connection.cursor()
            cursor.executemany(query, data)
            self.commit_transaction()
            return True
        except sqlite3.Error as e:
            self.rollback_transaction()
            logger.error(f"batch_insert_批量插入失败: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def _execute_db_delete(self, table_name, condition):
        try:
            return self.delete_by_condition(table_name, condition)
        except Exception as e:
            logger.error(f"_execute_db_operations_数据库操作异常: {e}")
            return False

    def delete_by_condition(self, table: str, condition: str) -> bool:
        query = f"DELETE FROM {table} WHERE {condition}"
        logger.info(f'DELETE {table}: {query}')
        return self.execute_query(query)

    def _execute_db_operations(self, table_name, condition, columns, data_list):
        try:
            # 先删除旧数据
            if condition != '':
                if not self.delete_by_condition(table_name, condition):
                    return False
            return self.batch_insert(table_name, columns, data_list)
        except Exception as e:
            logger.error(f"_execute_db_operations_数据库操作异常: {e}")
            return False

    def delete_by_condition(self, table: str, condition: str) -> bool:
        query = f"DELETE FROM {table} WHERE {condition}"
        logger.info(f'DELETE {table}: {query}')
        return self.execute_query(query)

    def close(self):
        if self.connection:
            if self.in_transaction:
                self.rollback_transaction()
            self.connection.close()

    # 数据库操作 END

    # 数据插入
    # para：table_name 表名称
    #       condition  删除条件
    #       columns    插入数据时表对应的字段
    #       zhangfu_list 数据
    def process_stock_data_delete(self, table_name: str, condition: str):
        if not self.connect():
            return False
        try:
            # 开始事务
            self.begin_transaction()
            # 执行数据库操作
            if not self._execute_db_delete(table_name, condition):
                self.rollback_transaction()
                return False
            # 提交事务
            self.commit_transaction()
            return True
        except Exception as e:
            logger.error(f"数据删除异常: {e}")
            self.rollback_transaction()
            return False
        finally:
            self.close()

    # 数据插入
    # para：table_name 表名称
    #       condition  删除条件
    #       columns    插入数据时表对应的字段
    #       zhangfu_list 数据
    def process_stock_data_insert(self, table_name: str, condition: str, columns, zhangfu_list):
        if not self.connect():
            return False
        try:
            # 开始事务
            self.begin_transaction()
            # 执行数据库操作
            if not self._execute_db_operations(table_name, condition, columns, zhangfu_list):
                self.rollback_transaction()
                return False
            # 提交事务
            self.commit_transaction()
            return True
        except Exception as e:
            logger.error(f"数据处理异常: {e}")
            self.rollback_transaction()
            return False
        finally:
            self.close()

    # 数据检索
    # para: selectSql 查询SQL
    def process_stock_data_select(self, selectSql):
        cursor = None
        try:
            self.connect()
            self.begin_transaction()
            # 开始事务
            cursor = self.connection.cursor()
            cursor.execute(selectSql)
            logger.info(f"process_stock_data_select: {selectSql}")
            return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"数据处理异常: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
            self.close()
