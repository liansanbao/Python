# _*_ coding: utf-8 _*_
# @Time : 2025/5/22 0022 21:38
# @Author : 韦丽
# @Version: V 1.0
# @File : MainWindow.py
# @desc : 工序管理系统主界面
import logging
import sys

import pandas as pd
from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtWidgets import (QMainWindow, QTableWidget,
                             QPushButton, QVBoxLayout, QWidget, QLineEdit, QComboBox,
                             QScrollArea, QLabel, QHBoxLayout, QFileDialog)
from PyQt5.QtCore import Qt

from GongXuSystem.CalculatedModel import CalculatedOption
from GongXuSystem.ExpandableTable import ExpandableTable
from GongXuSystem.GongXuCfg import GongXuCfg
from GongXuSystem.GongXuDb import DBOperator
from GongXuSystem.MasterModel import MasterOption
from GongXuSystem.PartsModel import PartsOption
from GongXuSystem.ProcessesModel import ProcessesOption
from GongXuSystem.TemplateModel import TemplateOption

class GongXuLogger:
    def __init__(self, config):
        self.config = config
        # 加入日志
        # 获取logger实例
        self.logger = logging.getLogger("GongXuSystem")
        # 指定输出格式
        formatter = logging.Formatter('%(asctime)s  %(levelname)-8s:%(message)s')

        # 文件日志
        errPath = f"{self.config.current_dir}\\{self.config.current_file}.log"
        file_handler = logging.FileHandler(errPath, encoding=self.config.current_encode)
        file_handler.setFormatter(formatter)

        # 控制台日志
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        # 添加具体的日志处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.INFO)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = GongXuCfg()
        self.logger = GongXuLogger(self.config)
        self.db_manager = DBOperator(self.config, self.logger)
        if not self.db_manager.connect():
            self.logger.logger.error("无法连接数据库")
            raise RuntimeError("无法连接数据库")
        QSqlTableModel(db=self.db_manager.get_connection())
        self.processesModel = ProcessesOption(self.logger)
        self.masterModel = MasterOption(self.config, self.logger)
        self.calculatedModel = CalculatedOption(self.config, self.logger)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.config.window_title)
        self.setGeometry(100, 100, 1200, 800)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # 搜索区域
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入部件代码或名称")
        search_btn = QPushButton(self.config.search_button)
        search_btn.clicked.connect(self.display_tables)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        model_btn = QPushButton(self.config.template_button)
        model_btn.clicked.connect(self.import_tables)
        search_layout.addWidget(model_btn)
        execl_btn = QPushButton(self.config.import_button)
        execl_btn.clicked.connect(self.export_to_excel)
        search_layout.addWidget(execl_btn)
        layout.addLayout(search_layout)

        # 固定表格
        self.scroll_title = QScrollArea()
        self.scroll_title.setWidgetResizable(True)
        self.scroll_title.setFixedHeight(48)
        scroll_title_content = QWidget()
        self.scroll_title_layout = QVBoxLayout(scroll_title_content)
        self.scroll_title_layout.setAlignment(Qt.AlignTop)  # 关键设置：顶部对齐
        self.scroll_title_layout.setSpacing(0)  # 全局控件间距0像素
        self.scroll_title_layout.addWidget(ExpandableTable(None, self.config, self.logger, self.processesModel.sub_add.copy(), True))
        self.scroll_title.setWidget(scroll_title_content)
        layout.addWidget(self.scroll_title)
        # 直接隐藏整个QScrollArea控件
        self.scroll_title.setHidden(True)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)  # 关键设置：顶部对齐
        self.scroll_layout.setSpacing(0)  # 全局控件间距0像素
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        # 横向/竖向滚动条关闭
        scroll.setVerticalScrollBarPolicy(1)

    def export_to_excel(self):
        try:
            # 获取表格数据
            data = []
            for i in range(self.scroll_layout.count()):
                table = self.scroll_layout.itemAt(i).widget()
                if isinstance(table, QTableWidget):
                    for row in range(table.rowCount()):
                        row_data = []
                        for col in range(table.columnCount()):
                            item = table.cellWidget(row, col)
                            if isinstance(item, QComboBox):
                                row_data.append(item.currentText())
                            elif isinstance(item, QPushButton):
                                row_data.append("")
                            else:
                                item = table.item(row, col)
                                row_data.append(item.text() if item else "")
                        data.append(row_data)

            # 使用pandas将数据保存为Excel文件
            df = pd.DataFrame(data, columns=self.config.gongXuTable_title)
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel File", "", "Excel Files (*.xlsx)")
            if file_path:
                df.to_excel(file_path, index=False, engine='openpyxl')
        except Exception as ex:
            self.logger.logger.error(f'导出Execl出错了。{ex}')

    def import_tables(self):
        self.templateModel = TemplateOption(self.processesModel.sub_dict.copy(), self.logger)
        self.sample_data = self.templateModel.searchTemplate(self.search_input.text().upper())
        self.logger.logger.info(f'应用模板结果：{self.sample_data}')
        self.setTables()

    def display_tables(self):
        self.partsModel = PartsOption(self.processesModel.sub_dict.copy(), self.logger)
        self.sample_data = self.partsModel.search(self.search_input.text().upper())
        self.logger.logger.info(f'检索结果：{self.sample_data}')
        self.setTables()

    def setTables(self):
        # 彻底清理旧控件
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 根据搜索条件过滤数据
        filtered_data = [
            data for data in self.sample_data
        ]

        # 创建并添加表格
        for data in filtered_data:
            self.table = ExpandableTable(data, self.config, self.logger, self.processesModel.sub_add.copy(), False)
            # 设置上边距为负值实现上移效果
            self.scroll_layout.addWidget(self.table)

        firstVisble = False
        if not filtered_data:
            label = QLabel("未找到匹配的部件数据")
            self.scroll_layout.addWidget(label)
            firstVisble = True

        # 直接隐藏整个QScrollArea控件
        self.scroll_title.setHidden(firstVisble)

