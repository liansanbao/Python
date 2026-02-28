import datetime
import time
import random
from PyQt6.QtWidgets import (QMainWindow, QProgressBar,
                             QPushButton, QVBoxLayout, QWidget, QLabel,
                             QGroupBox, QHBoxLayout)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6 import QtGui
from PyQt6.QtCore import QTimer

from WLW.StockBase import DateTimeUtils, WaringStockServer, ZhuLiZiJinServer, DailyLimitServer, IncreaseFiveServer, \
    PlateFundServer, StockHoldingServer, WlwAllServer, NoticesServer
from WLW.model import DataOpreationModel
from WLW.Tools.LoggingEx import logger

# 采集所有
class DatabaseWorkerAll(QThread):
    progress = pyqtSignal(int, str)  # 进度值, 状态信息
    finished = pyqtSignal(bool, str)  # 成功状态, 消息

    def __init__(self, opreationType, data_list, saleDay):
        super().__init__()
        self.total = data_list[0]['total']
        self.opreationType = opreationType
        self.data_list = data_list
        self.saleDay = saleDay

    def run(self):
        try:
            rowCount = 80 # 每次处理件数
            # listlent = len(self.data_list[0]['total'])
            if self.total <= 5000:
                rowCount = 200
            elif self.total > 10000:
                rowCount = 500

            i = 0
            for key, item in dict(self.data_list[0]).items():
                start = 0
                itemRow = 0
                if key == 'total':
                    continue

                data_len = len(item)
                if data_len == 0:
                    continue
                itemTotal = data_len
                # 数据库插入过程
                while True:
                    end = data_len if rowCount >= data_len else rowCount
                    list_data = item[start: start + end]

                    # 数据插入
                    if key == 'D':
                        DailyLimitServer.insert(self.saleDay, list_data)
                        messageContent = '涨停板'
                    # elif key == 'M':
                    #     ZhuLiZiJinServer.insert(self.saleDay, list_data)
                    elif key == 'I':
                        IncreaseFiveServer.insert(self.saleDay, list_data)
                        messageContent = '涨幅(4%)以上'
                    elif key == 'N':
                        NoticesServer.insert(self.saleDay, list_data)
                        messageContent = '公告'
                    elif key == 'P':
                        PlateFundServer.insert(self.saleDay, list_data)
                        messageContent = '板块资金'
                    elif key == 'S':
                        StockHoldingServer.insert('', list_data)
                        messageContent = '机构持股'
                    elif key == 'Q':
                        WaringStockServer.insert(list_data)
                        messageContent = '风险个股'

                    # 模拟插入单条数据耗时
                    time.sleep(0.02 + random.random() * 0.05)

                    i += end
                    itemRow += end
                    # 计算进度
                    percent = int(i / self.total * 100)
                    status = f" 已采集 {i}/{self.total} 条 ({(i / self.total) * 100:.1f}%)"
                    itemStatus = f"{messageContent} 已采集 {itemRow}/{itemTotal} 条 ({(i / self.total) * 100:.1f}%)"
                    logger.info(itemStatus)
                    self.progress.emit(percent, status)
                    data_len -= end
                    if data_len <= 0:
                        break
                    start += end

                # DataOpreation 数据更新
                # 数据插入
                if key == 'D':
                    opreationType = 'STOCK_INFO_WLW'
                    interval = DataOpreationModel.getDataInterval(opreationType) + 1

                # elif key == 'M':
                #     opreationType = 'ZJLX_CRAWL'
                #     interval = DataOpreationModel.getDataInterval(opreationType) + 1

                elif key == 'I':
                    opreationType = 'GRIDIST_STOCK'
                    interval = DataOpreationModel.getDataInterval(opreationType) + 1

                elif key == 'N':
                    opreationType = 'NOTICE_CRAWL'
                    interval = DataOpreationModel.getDataInterval(opreationType) + 1

                elif key == 'P':
                    opreationType = 'HYZJL_CRAWL'
                    interval = DataOpreationModel.getDataInterval(opreationType) + 1

                elif key == 'S':
                    opreationType = 'STOCK_HOLDING'
                    interval = DataOpreationModel.getDataInterval(opreationType) + 1

                elif key == 'Q':
                    opreationType = 'STOCK_INFO_QUESTION'
                    interval = int(datetime.datetime.today().strftime('%Y%m'))

                ymd = datetime.datetime.today().strftime('%Y-%m-%d')
                ymdhms = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
                DataOpreationModel.insert('', [(ymd, interval, opreationType, ymdhms, ymdhms)])

            success_msg = f'[{self.saleDay}]一共有[{self.total}]条数据采集完成'
            self.finished.emit(True, success_msg)
        except Exception as e:
            self.finished.emit(False, f"错误: {str(e)}")

# 单一任务
class DatabaseWorker(QThread):
    progress = pyqtSignal(int, str)  # 进度值, 状态信息
    finished = pyqtSignal(bool, str)  # 成功状态, 消息

    def __init__(self, opreationType, data_list, saleDay):
        super().__init__()
        self.total = len(data_list)
        self.opreationType = opreationType
        self.data_list = data_list
        self.saleDay = saleDay
        self._is_running = True

    def run(self):
        try:
            rowCount = 50 # 每次处理件数
            listlent = len(self.data_list)
            if listlent < 1000:
                rowCount = 100
            else:
                rowCount = 500
            start = 0
            data_len = self.total
            i = 0
            # 数据库插入过程
            while True:
                if not self._is_running:
                    break
                end = data_len if rowCount >= data_len else rowCount
                list_data = self.data_list[start: start + end]

                # 数据插入
                if self.opreationType == 'D':
                    DailyLimitServer.insert(self.saleDay, list_data)
                elif self.opreationType == 'M':
                    ZhuLiZiJinServer.insert(self.saleDay, list_data)
                elif self.opreationType == 'I':
                    IncreaseFiveServer.insert(self.saleDay, list_data)
                elif self.opreationType == 'N':
                    NoticesServer.insert(self.saleDay, list_data)
                elif self.opreationType == 'P':
                    PlateFundServer.insert(self.saleDay, list_data)
                elif self.opreationType == 'S':
                    StockHoldingServer.insert('', list_data)
                elif self.opreationType == 'Q':
                    WaringStockServer.insert(list_data)

                # 模拟插入单条数据耗时
                time.sleep(0.02 + random.random() * 0.05)

                i = start + end
                # 计算进度
                percent = int(i / self.total * 100)
                status = f"已采集 {i}/{self.total} 条 ({(i / self.total) * 100:.1f}%)"
                logger.info(status)
                self.progress.emit(percent, status)
                data_len -= end
                if data_len <= 0:
                    break
                start += end

            # DataOpreation 数据更新
            success_msg = f'[{self.saleDay}]一共有[{self.total}]条数据采集完成'
            # 数据插入
            if self.opreationType == 'D':
                opreationType = 'STOCK_INFO_WLW'
                interval = DataOpreationModel.getDataInterval(opreationType) + 1

            elif self.opreationType == 'M':
                opreationType = 'ZJLX_CRAWL'
                interval = DataOpreationModel.getDataInterval(opreationType) + 1

            elif self.opreationType == 'I':
                opreationType = 'GRIDIST_STOCK'
                interval = DataOpreationModel.getDataInterval(opreationType) + 1

            elif self.opreationType == 'N':
                opreationType = 'NOTICE_CRAWL'
                interval = DataOpreationModel.getDataInterval(opreationType) + 1

            elif self.opreationType == 'P':
                opreationType = 'HYZJL_CRAWL'
                interval = DataOpreationModel.getDataInterval(opreationType) + 1

            elif self.opreationType == 'S':
                opreationType = 'STOCK_HOLDING'
                interval = DataOpreationModel.getDataInterval(opreationType) + 1

            elif self.opreationType == 'Q':
                opreationType = 'STOCK_INFO_QUESTION'
                interval = int(datetime.datetime.today().strftime('%Y%m'))

            ymd = datetime.datetime.today().strftime('%Y-%m-%d')
            ymdhms = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            DataOpreationModel.insert('', [(ymd, interval, opreationType, ymdhms, ymdhms)])
            self.finished.emit(True, success_msg)
        except Exception as e:
            self.finished.emit(False, f"错误: {str(e)}")

# 数据采集
class ProgressWindow(QMainWindow):
    def __init__(self, opreationType:str='D'):
        super().__init__()
        self.data_list = []
        self.opreationType = opreationType
        self.saleDay = DateTimeUtils.saleDate() if not opreationType in ['P', 'N'] else DateTimeUtils.plateSaleDate()
        self.setup_ui()
        self.setData()
        self.worker = None

    def setup_ui(self):
        if self.opreationType == 'D':
            self.setWindowTitle("涨停板 数据采集加载器")
        elif self.opreationType == 'M':
            self.setWindowTitle("资金流向 数据采集加载器")
        elif self.opreationType == 'I':
            self.setWindowTitle("涨幅(5%)以上 数据采集加载器")
        elif self.opreationType == 'P':
            self.setWindowTitle("板块资金 数据采集加载器")
        elif self.opreationType == 'S':
            self.setWindowTitle("机构持股 数据采集加载器")
        elif self.opreationType == 'Q':
            self.setWindowTitle("风险个股 数据采集加载器")
        elif self.opreationType == 'ALL':
            self.setWindowTitle("采集所有 数据采集加载器")
        elif self.opreationType == 'N':
            self.setWindowTitle("公告 数据采集加载器")
        else:
            self.setWindowTitle("数据采集加载器")
        self.resize(600, 200)
        self.setWindowIcon(QtGui.QIcon("_internal/image/wlw.svg"))

        # 主布局
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)

        # 进度组
        progress_group = QGroupBox("数据采集进度")
        progress_layout = QVBoxLayout(progress_group)

        # 渐变进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(30)

        # 进度条样式：单色纯绿
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #00C853;
                border-radius: 5px;
                background: #ECF0F1;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    spread:pad, x1:0, y1:0.5, x2:1, y2:0.5,
                    stop:0 #00C853, stop:1 #00C853);
                border-radius: 3px;
            }
        """)

        # 进度标签
        self.progress_label = QLabel("准备开始数据采集...")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setStyleSheet("font-size: 14px; color: #2C3E50;") # 8BC34A 2C3E50

        # 统计信息栏
        stats_group = QGroupBox("统计信息")
        stats_layout = QHBoxLayout(stats_group)

        self.speed_label = QLabel("速度: -- 条/秒")
        self.time_label = QLabel("已用时间: --")
        self.est_label = QLabel("剩余时间: --")

        for label in [self.speed_label, self.time_label, self.est_label]:
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("""
                QLabel {
                    background: #F8F9FA;
                    border: 1px solid #DEE2E6;
                    border-radius: 3px;
                    padding: 5px;
                    font-weight: bold;
                }
            """)

        stats_layout.addWidget(self.speed_label)
        stats_layout.addWidget(self.time_label)
        stats_layout.addWidget(self.est_label)

        # 控制按钮
        self.start_btn = QPushButton("开始采集")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background: #2ECC71;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #27AE60;
            }
        """)
        self.start_btn.clicked.connect(self.start_insertion)

        # 组装界面
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        layout.addWidget(progress_group)
        layout.addWidget(stats_group)
        layout.addWidget(self.start_btn)

        self.setCentralWidget(main_widget)

        # 计时器
        self.start_time = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)

    def setData(self):
        logger.info(f'saleDay: {self.saleDay}')
        # 涨停板
        if self.opreationType == 'D':
            self.data_list = DailyLimitServer.exec(saleDay=self.saleDay)
        elif self.opreationType == 'M':
            self.data_list = ZhuLiZiJinServer.exec(saleDay=self.saleDay)
        elif self.opreationType == 'I':
            self.data_list = IncreaseFiveServer.exec(saleDay=self.saleDay)
        elif self.opreationType == 'N':
            self.data_list = NoticesServer.exec(saleDay=self.saleDay)
        elif self.opreationType == 'P':
            self.data_list = PlateFundServer.exec(saleDay=self.saleDay)
            if self.data_list != None and len(self.data_list) > 0:
                PlateFundServer.delete(self.saleDay)
        elif self.opreationType == 'S':
            self.data_list = StockHoldingServer.exec('')
        elif self.opreationType == 'Q':
            self.data_list = WaringStockServer.exec()
        elif self.opreationType == 'ALL':
            self.data_list = WlwAllServer.exec()
            if self.data_list != None and len(self.data_list) > 0:
                if 'P' in dict(self.data_list[0]).keys():
                    PlateFundServer.delete(self.saleDay)

        # logger.info(f'采集数据：{self.data_list}')
        # 设置按钮是否可操作
        enabledFlag = True
        if self.data_list == None or len(self.data_list) == 0:
            enabledFlag = False
            self.progress_label.setText('数据没有，稍后再试一试。')

        self.start_btn.setEnabled(enabledFlag)

    def start_insertion(self):
        self.start_btn.setEnabled(False)
        self.start_time = time.time()
        self.timer.start(1000)  # 每秒更新统计

        # 创建并启动工作线程
        if self.opreationType == 'ALL':
            self.worker = DatabaseWorkerAll(self.opreationType, self.data_list, self.saleDay)
        else:
            self.worker = DatabaseWorker(self.opreationType, self.data_list, self.saleDay)

        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def update_progress(self, value, status):
        self.progress_bar.setValue(value)
        self.progress_label.setText(status)

    def update_stats(self):
        if self.start_time and self.progress_bar.value() > 0:
            elapsed = time.time() - self.start_time
            speed = self.progress_bar.value() * 5 / elapsed
            remaining = (100 - self.progress_bar.value()) * elapsed / self.progress_bar.value()
            self.speed_label.setText(f"速度: {speed:.1f} 条/秒")
            self.time_label.setText(f"已用时间: {int(elapsed)}秒")
            self.est_label.setText(f"剩余时间: {int(remaining)}秒")

    def on_finished(self, success, message):
        self.timer.stop()
        self.start_btn.setEnabled(True)

        if success:
            self.progress_label.setText(message)
            self.progress_bar.setValue(100)
        else:
            self.progress_label.setText(f"错误: {message}")
            self.progress_bar.setValue(0)
