# _*_ coding: utf-8 _*_
# @Time : 2025/5/23 0023 17:36
# @Author : 韦丽
# @Version: V 1.0
# @File : MasterModel.py
# @desc :
from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlTableModel


class MasterOption:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.exec()

    def exec(self):
        # 车种
        self.config.machine_combox = self.searchMaster(self.config.machine_key)
        # 动作描述
        self.config.action_combox = self.searchMaster(self.config.action_key)
        # 长度
        self.config.length_combox = self.searchMaster(self.config.length_key)
        # 级别
        self.config.level_combox = self.searchMaster(self.config.level_key)
        # 频率
        self.config.frequency_combox = self.searchMaster(self.config.frequency_key)

    def searchMaster(self, searchWord):
        model = QSqlTableModel()
        model.setTable("Master")
        model.setFilter(
            f"category = '{searchWord}' "
        )
        model.setSort(3, Qt.SortOrder.AscendingOrder)
        model.select()
        # 输出原始SQL
        self.logger.logger.info(f"执行SQL: {model.query().executedQuery()}")

        result = []
        # 遍历模型所有行和列
        for row in range(model.rowCount()):
            index = model.index(row, 2)
            result.append(str(model.data(index)))
        self.logger.logger.info(f'Master: {result}')
        return result