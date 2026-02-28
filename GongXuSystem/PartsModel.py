# _*_ coding: utf-8 _*_
# @Time : 2025/5/23 0023 9:26
# @Author : 韦丽
# @Version: V 1.0
# @File : PartsModel.py
# @desc : 部品表数据检索
from PyQt5.QtSql import QSqlTableModel

class PartsOption:
    def __init__(self, sub_dict, logger):
        self.sub_dict = sub_dict
        self.logger = logger

    def search(self, inputWord):
        model = QSqlTableModel()
        model.setTable("Parts")
        model.setFilter(
            f"part_name LIKE '%{inputWord}%' "
            f"OR part_code LIKE '%{inputWord}%'"
        )
        model.select()

        # 调试输出
        self.logger.logger.info(f"过滤条件: {model.filter()}")
        self.logger.logger.info(f"有效行数: {model.rowCount()}")

        # 输出原始SQL
        self.logger.logger.info(f"执行SQL: {model.query().executedQuery()}")

        result = []
        # 遍历模型所有行和列
        for row in range(model.rowCount()):
            row_data = []
            for col in range(1, model.columnCount()):
                index = model.index(row, col)
                row_data.append(str(model.data(index)))

            result.append({
                'main': row_data,
                'sub': self.sub_dict
            })
        return result