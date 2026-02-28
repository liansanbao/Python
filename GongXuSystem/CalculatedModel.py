# _*_ coding: utf-8 _*_
# @Time : 2025/5/23 0023 18:53
# @Author : 韦丽
# @Version: V 1.0
# @File : CalculatedModel.py
# @desc : 计算值数据

from PyQt5.QtSql import QSqlTableModel

class CalculatedOption:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.exec()

    def exec(self):
        # 车种
        self.config.machine_values = self.searchCalculated(self.config.machine_C_key)
        # 动作
        self.config.action_values = self.searchCalculated(self.config.action_C_key)
        # 长度
        self.config.length_range_values = self.searchCalculated(self.config.length_range_C_key)
        # 级别
        self.config.level_values = self.searchCalculated(self.config.level_C_key)

    def searchCalculated(self, searchWord):
        model = QSqlTableModel()
        model.setTable("Calculated")
        model.setFilter(
            f"category = '{searchWord}' "
        )
        model.select()
        # 输出原始SQL
        self.logger.logger.info(f"执行SQL: {model.query().executedQuery()}")

        result = {}
        # 遍历模型所有行和列
        for row in range(model.rowCount()):
            key = model.index(row, 2)
            val = model.index(row, 3)
            result[str(model.data(key))] = float(model.data(val))
        self.logger.logger.info(f'Calculated: {result}')
        return result