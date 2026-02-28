# _*_ coding: utf-8 _*_
# @Time : 2025/5/23 0023 9:38
# @Author : 韦丽
# @Version: V 1.0
# @File : ProcessesModel.py
# @desc : 子工序主表数据检索
from PyQt5.QtSql import QSqlTableModel


class ProcessesOption:
    def __init__(self, logger):
        self.logger = logger
        self.search()

    def search(self):
        model = QSqlTableModel()
        model.setTable("processes")
        model.select()

        # 调试输出
        self.logger.logger.info(f"有效行数: {model.rowCount()}")

        # 输出原始SQL
        self.logger.logger.info(f"执行SQL: {model.query().executedQuery()}")

        sub_list = []
        # 遍历模型所有行和列
        for row in range(model.rowCount()):
            row_data = ['', '', '', '']
            for col in range(1, model.columnCount()):
                index = model.index(row, col)
                row_data.append(model.data(index))
            sub_list.append(row_data)
            # 添加按钮数据
            if row == 0:
                self.sub_add = row_data

        self.sub_dict = sub_list