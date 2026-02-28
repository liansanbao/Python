# _*_ coding: utf-8 _*_
# @Time : 2025/5/22 0022 21:51
# @Author : 韦丽
# @Version: V 1.0
# @File : GongXuDb.py
# @desc : 数据库操作类
from PyQt5.QtSql import QSqlDatabase

class DBOperator:
    def __init__(self, config, logger):
        self.connection = None
        self.config = config
        self.logger = logger

    def connect(self):
        try:
            # 检查可用驱动
            self.logger.logger.info(f"检查可用驱动: {QSqlDatabase.drivers()}")
            self.connection = QSqlDatabase.addDatabase('QODBC')
            self.connection.setHostName(self.config.host)
            self.connection.setPort(int(self.config.port))
            self.connection.setUserName(self.config.user)
            self.connection.setPassword(self.config.password)
            self.connection.setDatabaseName(self.config.dbname)

            if not self.connection.open():
                raise RuntimeError(self.connection.lastError().text())

            return self.connection.open()
        except Exception as e:
            self.logger.logger.error(f"Database connection failed: {e}")
            return False

    def get_connection(self):
        return self.connection if self.connection and self.connection.isOpen() else None

    def close(self):
        if self.connection and self.connection.isOpen():
            self.connection.close()
