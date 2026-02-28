# _*_ coding: utf-8 _*_
# @Time : 2025/5/22 0022 21:38
# @Author : 韦丽
# @Version: V 1.0
# @File : ExpandableTable.py
# @desc : 工序管理系统表格类

from PyQt5.QtWidgets import (QTableWidget, QTableWidgetItem,
                             QPushButton, QComboBox, QHeaderView, QMessageBox, QAbstractItemView)
from PyQt5.QtCore import pyqtSignal

class ExpandableTable(QTableWidget):
    rowRemoved = pyqtSignal(int)  # 信号声明必须放在类顶层

    def __init__(self, data, cfg, logger, sub_add, headerVisible, parent=None):
        super().__init__(parent)
        self.config = cfg
        self.logger = logger
        self.sub_add = sub_add
        self.headerVisible = headerVisible
        self.setup_table(data)

    def setup_table(self, data):
        self.setColumnCount(13)
        self.setHorizontalHeaderLabels(self.config.gongXuTable_title)
        if not self.headerVisible:
            self.horizontalHeader().setVisible(False)
            self.populate_data(data)
        else:
            # 将第一行设为冻结行
            self.verticalHeader().setDefaultSectionSize(28)
            self.setFixedHeight(28)

        # 默认行号设置不显示
        self.verticalHeader().setVisible(False)
        # 横向/竖向滚动条关闭
        self.setHorizontalScrollBarPolicy(1)
        self.setVerticalScrollBarPolicy(1)
        # 设置行交替
        # self.setAlternatingRowColors(True)
        # 禁止编辑
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # 设置表格为整行选择 QAbstractItemView.SelectionBehavior(1) 单元格选中：QAbstractItemView.SelectionBehavior(0) 列选中：QAbstractItemView.SelectionBehavior(2)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior(1))
        # self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    # 悬浮提示
    def setQTableWidgetItem(self, text):
        item_tooltip = QTableWidgetItem(text)
        item_tooltip.setToolTip(text)
        return item_tooltip

    def populate_data(self, data):
        # 主工序行
        self.insertRow(0)
        toggle_btn = QPushButton(self.config.expand_button)
        toggle_btn.setProperty("expanded", False)
        # 展开/折叠
        toggle_btn.clicked.connect(self.toggle_sub_rows)
        self.setCellWidget(0, 0, toggle_btn)

        for col in range(1, 5):
            text = str(data['main'][col - 1])
            if col == 1:
                self.main_part_code = text
            # 悬浮提示
            self.setItem(0, col, self.setQTableWidgetItem(text))

        # 子工序行
        for i, sub in enumerate(data['sub'], 1):
            self.add_sub_row(i, sub)
            self.setRowHidden(i, True)

        # 添加按钮行
        self.insertRow(len(data['sub']) + 1)
        add_btn = QPushButton(self.config.rowAdd_button)
        add_btn.clicked.connect(self.add_sub_row)
        self.setCellWidget(len(data['sub']) + 1, 0, add_btn)
        # 表格自适应
        self.autoFixedHeight()

    def toggle_sub_rows(self):
        btn = self.sender()
        expanded = not btn.property("expanded")
        btn.setProperty("expanded", expanded)
        btn.setText(self.config.shrink_button if expanded else self.config.expand_button)

        for i in range(1, self.rowCount() - 1):
            self.setRowHidden(i, not expanded)

        # 表格自适应
        self.autoFixedHeight()

    def add_sub_row(self, row=None, data=None):
        try:
            if data is None:
                row = self.rowCount() - 1
                data = self.sub_add.copy()
                # 最后一条数据中序号值获取
                item = self.item(row-1, 5)
                if item is not None:
                    rowNo = int(item.text()) + 1
                    data[4] = rowNo

                self.logger.logger.info(f"部品代码[{self.main_part_code}]添加数据：{data}")

            self.insertRow(row)
            del_btn = QPushButton(self.config.delete_button)
            del_btn.clicked.connect(lambda: self.removeRow(row))
            self.setCellWidget(row, 0, del_btn)

            for col, val in enumerate(data, 1):
                if 6 <= col <= 10:  # 下拉框列
                    combo = QComboBox()
                    options = {
                        6: self.config.machine_combox,
                        7: self.config.action_combox,
                        8: self.config.length_combox,
                        9: self.config.level_combox,
                        10: self.config.frequency_combox
                    }
                    combo.addItems(options[col])
                    combo.setCurrentText(str(val))
                    combo.currentTextChanged.connect(lambda: self.calculate_values(row))
                    self.setCellWidget(row, col, combo)
                else:
                    self.setItem(row, col, self.setQTableWidgetItem(str(val)))

            # 合计(计算/时间)
            self.total_value()
            # 表格自适应
            self.autoFixedHeight()
        except Exception as ex:
            self.logger.logger.error(f'添加行出错了：{ex}')

    def autoFixedHeight(self):
        expanded_height = 2
        for row in range(self.rowCount()):
            expanded_height += self.rowHeight(row)
        self.setFixedHeight(expanded_height)

    def calculate_values(self, row):
        # 获取当前行的值
        machine_type = self.cellWidget(row, 6)
        if isinstance(machine_type, QComboBox):
            self.machine_value = self.config.machine_values[machine_type.currentText()]
        action_desc = self.cellWidget(row, 7)
        if isinstance(action_desc, QComboBox):
            self.action_value = self.config.action_values[action_desc.currentText()]
        length_range = self.cellWidget(row, 8)
        if isinstance(length_range, QComboBox):
            self.length_range_value = self.config.length_range_values[length_range.currentText()]
        level = self.cellWidget(row, 9)
        if isinstance(level, QComboBox):
            self.level_range_value = self.config.level_values[level.currentText()]
        frequency = self.cellWidget(row, 10)
        if isinstance(frequency, QComboBox):
            self.frequency_value = int(frequency.currentText())

        # 悬浮提示 计算
        calculation = round(self.frequency_value * self.machine_value * self.action_value * self.level_range_value * self.length_range_value, 4)
        self.setItem(row, 11, self.setQTableWidgetItem(str(calculation)))
        # 悬浮提示 时间
        time_value = int(round(self.frequency_value * self.machine_value * self.action_value * self.length_range_value, 0))
        self.setItem(row, 12, self.setQTableWidgetItem(str(time_value)))
        # 合计(计算/时间)
        self.total_value()

    def total_value(self):
        # 总计算
        total_calculation = float(0)
        # 总时间
        time_calculation = 0
        try:
            for rowNo in range(1, self.rowCount()):
                calculation_item = self.item(rowNo, 11)
                if calculation_item is not None:
                    total_calculation += float(calculation_item.text())

                time_item = self.item(rowNo, 12)
                if time_item is not None:
                    time_calculation += int(time_item.text())

        except Exception as ex:
            self.logger.logger.error(f'总计算/总时间出错了：{ex}')

        total_calculation = round(total_calculation, 4)
        self.setItem(0, 11, self.setQTableWidgetItem(str(total_calculation)))
        # 总时间
        self.setItem(0, 12, self.setQTableWidgetItem(str(time_calculation)))

    def removeRow(self, row: int) -> None:
        # 获取当前行的值
        bt_type = self.cellWidget(row, 0)
        if isinstance(bt_type, QPushButton):
            self.bt_type_value = bt_type.text()
            if self.config.rowAdd_button == self.bt_type_value:
                return
        # 重写removeRow
        if 0 <= row < self.rowCount():
            # 添加删除确认对话框
            reply = QMessageBox.question(
                self, '确认删除',
                f'确定要删除第{row + 1}行吗？',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                super().removeRow(row)  # 调用父类实现
                self.rowRemoved.emit(row)  # 发射自定义信号

        # 更新剩余按钮的行号
        for r in range(1, self.rowCount() -1):
            btn = self.cellWidget(r, 0)
            if btn:
                btn.clicked.disconnect()
                btn.clicked.connect(lambda _, r=r: self.removeRow(r))

        # 合计(计算/时间)
        self.total_value()
        # 表格自适应
        self.autoFixedHeight()
