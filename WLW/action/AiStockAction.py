# _*_ coding: utf-8 _*_
# @Time : 2026/3/3 星期二 17:10
# @Author : 韦丽
# @Version: V 1.0
# @File : AiStockAction.py
# @desc : Ai诊股处理
import copy
import os
from functools import partial
from typing import Dict, Any

import pandas
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import QDate, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QStandardItemModel, QIcon, QPixmap, QFont, QTextCursor
from PyQt6.QtWidgets import QVBoxLayout, QTextEdit, QHBoxLayout, QLineEdit, QPushButton, QMessageBox
from openai import OpenAI

from WLW.StockBase import DateTimeUtils
from WLW.Tools.CommonUtils import setQStandardItem
from WLW.Tools.LoggingEx import logger
from WLW.action import StockInfoAction, PlateFundAction, IncreaseFiveAction
from WLW.action.MultiDailySortProxyModel import CustomProxyModel as StockCustomProxyModel
from WLW.action.MultiPlateFundSortProxyModel import CustomProxyModel as PlateFundCustomProxyModel
from WLW.action.MultiIncreaseSortProxyModel import CustomProxyModel as IncreaseCustomProxyModel
from WLW.model import StockInfoModel, PlateFundModel, IncreaseFiveModel
from WLW.model.IncreaseFiveCondition import IncreaseFiveCondition
from WLW.model.PlateFundCondition import PlateFundCondition
from WLW.model.StockInfoCondition import StockInfoCondition

# 涨停板行标题
headerDailylimitTitles = ['交易日期', '所属行业', '股票No', '名称', '涨跌幅(%)', '最新价(元)', '连板数', '炸板次数', '风险种类', '游资',
     '成交额(亿)',
     '换手率(%)', 'F封板时间', 'L封板时间', '封板资金', '涨停统计', '涨停主题', '涨停原因', '机构持股数量', 'hidden']
# 设定项目值显示
showDailylimitHeaderLables = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

# 板块/概念标题
headerPlateFundTitles = ['交易日期', '板块代码', '板块名称', '最新价', '涨跌幅', '主力B(净额)', '主力B(净占比)', '优秀股名称',
 '优秀股代码',
 '持股机构数', '涨停主题', '概念', '涨停原因', '涨幅', '价格', '成交量(手)', '成交额', '换手率', 'hidden']
# 板块/概念设定项目值显示
showPlateFundHeaderLables = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]

# 4%以上涨幅标题
headerIncreaseTitles = ['股票No', '名称', '交易日期', '所属行业', '涨幅', '现价(元)', '风险种类', '涨跌额', '成交量(手)', '成交额',
         '振幅', '换手率', '市盈率',
         '量比', '涨停主题', '概念', '涨停原因', '机构数', '上榜次数', '首次交易日', 'hidden']
# 4%以上涨幅设定项目值显示
showIncreaseHeaderLables = [2, 3, 0, 1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 21, 22, 23]
# AI 千问大模型
class ModelWorker(QThread):
    response_received = pyqtSignal(str, int)
    error_occurred = pyqtSignal(str)

    def __init__(self, messages):
        super().__init__()
        # 初始化OpenAI客户端
        self.client = OpenAI(
            # 如果没有配置环境变量，请用阿里云百炼API Key替换：api_key="sk-xxx"
            # api_key=os.getenv("DASHSCOPE_API_KEY"),
            api_key= 'sk-6396cd26c2204d5b8854c4b2e5ac0eec',
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.messages = messages
    # 千问大模型执行
    def run(self):
        try:
            completion = self.client.chat.completions.create(
                model="deepseek-v3.2",
                messages=self.messages,
                # 通过 extra_body 设置 enable_thinking 开启思考模式
                extra_body={"enable_thinking": True},
                stream=True,
                stream_options={
                    "include_usage": True
                },
            )

            full_response = ""
            for chunk in completion:
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta

                # 只收集思考内容
                if hasattr(delta, "reasoning_content") and delta.reasoning_content is not None:
                    full_response += delta.reasoning_content
                    self.response_received.emit(full_response, 0)

                # 收到content，开始进行回复
                if hasattr(delta, "content") and delta.content:
                    full_response += delta.content
                    self.response_received.emit(full_response, 0)
        except Exception as e:
            self.error_occurred.emit(str(e))

# 画面初期设定
def aiStockInitContent(windows, formWidget):
    # 股票No、板块No、概念No
    formWidget.aiStock_No.setText('')
    # 股票名称、板块名称、概念名称
    formWidget.aiStock_Name.setText('')
    # 总件数format
    formWidget.aiStock_count_number.setText(f'一共 0 件数据')

    # 当前周開始日取得
    weekFromDay = DateTimeUtils.Week_Day_Date(weekDay=1)

    # 交易日期From 显示格式
    formWidget.aiStock_From.setDate(QDate(weekFromDay.year, weekFromDay.month, weekFromDay.day))
    # 交易日期From 可选最大日期
    formWidget.aiStock_From.setMaximumDate(QDate.currentDate().addDays(0))
    # 交易日期From 日历控件弹出
    formWidget.aiStock_From.setCalendarPopup(True)

    # 交易日期To 显示格式
    formWidget.aiStock_To.setDate(QDate.currentDate())
    # 交易日期To 可选最大日期
    formWidget.aiStock_To.setMaximumDate(QDate.currentDate().addDays(0))
    # 交易日期To 日历控件弹出
    formWidget.aiStock_To.setCalendarPopup(True)

    # AI layout START
    vbox = QVBoxLayout()

    # 对话显示区域
    formWidget.chat_display = QTextEdit()
    formWidget.chat_display.setStyleSheet("""
                QTextEdit {
                    border: none;
                    background-color: #f0f8ff;
                    padding: 5px;
                }
            """)
    formWidget.chat_display.setReadOnly(True)
    vbox.addWidget(formWidget.chat_display)

    # 输入区域和按钮
    hbox = QHBoxLayout()
    formWidget.input_box = QLineEdit()
    formWidget.input_box.setStyleSheet("""
            QLineEdit {
                border: none;
                background-color: #f0f8ff;
                padding: 5px;
            }
        """)  # 无边框输入框
    formWidget.input_box.setPlaceholderText('请输入你的问题...')
    formWidget.input_box.setFont(QFont("微软雅黑", 11))
    formWidget.send_btn = QPushButton('发送')
    formWidget.send_btn.setFixedSize(75, 30)
    formWidget.send_btn.setStyleSheet("""
            QPushButton {
                border: 1px solid #000000;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover {
                border: 1px solid #FF0000;
            }
            QPushButton:pressed {
                border: 1px solid #00FF00;
            }
    """)
    formWidget.send_btn.clicked.connect(partial(ask_model, windows, formWidget))
    formWidget.input_box.returnPressed.connect(formWidget.send_btn.click)  # 回车发送

    hbox.addWidget(formWidget.input_box)
    hbox.addWidget(formWidget.send_btn)
    vbox.addLayout(hbox)

    formWidget.aiStock_groupBox.setLayout(vbox)

    # 初始化计时器和工作线程
    windows.timer = QTimer()
    windows.timer.timeout.connect(partial(update_timer, windows, formWidget))
    windows.seconds_elapsed = 0

    windows.worker = None
    # AI layout END

    # 数据类型
    formWidget.aiStock_dataTypeContion.clear()
    formWidget.aiStock_dataTypeContion.addItems(['涨停板', '板块', '概念', '涨幅%4以上'])
    formWidget.aiStock_dataTypeContion.setCurrentIndex(0)
    formWidget.aiStock_dataTypeContion.setMinimumHeight(26)
    formWidget.aiStock_dataTypeContion.currentIndexChanged.connect(
        lambda index: on_aiStock_dataTypeContion_selection_change(formWidget.aiStock_dataTypeContion.currentIndex(), formWidget, windows))

    # 上一页
    upIcon = QIcon()
    upIcon.addPixmap(QPixmap("_internal/image/upPage.svg"), QIcon.Mode.Normal, QIcon.State.Off)
    formWidget.aiStock_upPlate.setIcon(upIcon)
    # 下一页
    nextIcon = QIcon()
    nextIcon.addPixmap(QPixmap("_internal/image/nextPage.svg"), QIcon.Mode.Normal, QIcon.State.Off)
    formWidget.aiStock_nextPlate.setIcon(nextIcon)

# 千问大模型执行
def ask_model(windows, formWidget):
    windows.user_input = formWidget.input_box.text().strip()
    msgContent = ""
    if not windows.user_input:
        msgContent = "请描述你的问题。"

    # 股票数据验证
    if windows.showAiStockData == None or len(windows.showAiStockData) == 0:
        msgContent += "\n数据没有了，不能使用AI大模型。"

    if msgContent:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.NoIcon)
        msg.setWindowTitle('数据采集')
        msg.setWindowIcon(QtGui.QIcon("_internal/image/wlw.svg"))
        msg.setText(msgContent)
        # 设置消息框大小
        msg.setFixedSize(800, 800)  # 宽度800像素，高度800像素
        # 添加确定按钮
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
        return

    messages = [
        {"role": "user", "content": f"{windows.user_input}, {windows.showAiStockData}"}]
    # 清空显示区域
    formWidget.chat_display.clear()
    windows.seconds_elapsed = 0
    windows.is_streaming = True
    start_timer(windows, formWidget)

    # 显示初始等待信息
    formWidget.chat_display.setPlainText(f"[等待中] 正在请求千问大模型...\n已等待 0 秒")

    windows.worker = ModelWorker(messages)
    windows.worker.response_received.connect(partial(handle_response, windows, formWidget))
    windows.worker.error_occurred.connect(partial(handle_error, windows, formWidget))
    windows.worker.finished.connect(windows.worker.deleteLater)
    windows.worker.start()

def start_timer(windows, formWidget):
    windows.timer.start(1000)  # 每秒触发一次

def update_timer(windows, formWidget):
    if windows.is_streaming:
        windows.seconds_elapsed += 1
        # 更新计时显示，但不覆盖已有的回复内容
        current_text = formWidget.chat_display.toPlainText()
        if "[等待中]" in current_text:
            # 如果还在等待阶段，更新计时
            lines = current_text.split('\n')
            if len(lines) > 1:
                lines[1] = f"已等待 {windows.seconds_elapsed} 秒"
                formWidget.chat_display.setPlainText('\n'.join(lines))

def handle_response(windows, formWidget, response_text, _):
    windows.timer.stop()
    # 清空问题区域
    formWidget.input_box.clear()
    final_text = f"[问题]：{windows.user_input}\n\n{response_text}\n\n总计耗时: {windows.seconds_elapsed} 秒"
    formWidget.chat_display.setPlainText(final_text)
    # 自动滚动到底部
    cursor = formWidget.chat_display.textCursor()
    cursor.movePosition(QTextCursor.MoveOperation.End)
    formWidget.chat_display.setTextCursor(cursor)

def handle_error(windows, formWidget, error_msg):
    windows.timer.stop()
    formWidget.chat_display.setPlainText(f"[错误]\n请求失败: {error_msg}")

# 数据类型下拉框事件
def on_aiStock_dataTypeContion_selection_change(currentIndex, formWigdet, windows):
    try:
        _translate = QtCore.QCoreApplication.translate
        placeText = '股票'
        if currentIndex == 1:
            placeText = '板块'
        elif currentIndex == 2:
            placeText = '概念'
        elif currentIndex == 3:
            placeText = '股票'
        formWigdet.aiStock_No.setPlaceholderText(_translate("WLW", f"{placeText}代码"))
        formWigdet.aiStock_Name.setPlaceholderText(_translate("WLW", f"{placeText}名称"))
        clearShowTable(windows, formWigdet)
    except Exception as ex:
        logger.error(f'涨幅下拉框处理出错了：{str(ex)}')

# 数据显示区域清空
def clearShowTable(windows, formWigdet):
    windows.aiStockModel.clear()  # 清除所有数据及表头
    # 分页按钮不显示
    formWigdet.aiStock_upPlate.setVisible(False)
    formWigdet.aiStock_nextPlate.setVisible(False)
    # 总件数format
    formWigdet.aiStock_count_number.setText('一共 0 件数据')
    # 页码格式化
    formWigdet.aiStock_PageNo.setText('')
    # data 不显示
    formWigdet.aiStock_Table.setVisible(False)

# 事件绑定 注意参数传递:在这里functools.partial(方法名, 参数1, 参数2) 在主程序里就是方法名
def aiStockActionSetting(windows, formWidget):
    # 事件绑定 -- 检索
    formWidget.aiStockSubmit.clicked.connect(partial(AddClickedAiStockSubmit, windows, formWidget))
    # 事件绑定 -- 清除
    formWidget.aiStockClear.clicked.connect(partial(AddClickedNoticClear, windows, formWidget))
    # 事件绑定 -- 上一页
    formWidget.aiStock_upPlate.clicked.connect(partial(AddClickedStockPage, 'up', windows, formWidget))
    # 事件绑定 -- 下一页
    formWidget.aiStock_nextPlate.clicked.connect(partial(AddClickedStockPage, 'next', windows, formWidget))

# 事件绑定 -- 检索
def AddClickedAiStockSubmit(windows, formWidget):
    # 数据绑定
    editAiStockTable(windows, formWidget)

# 事件绑定 -- 翻页处理
def AddClickedStockPage(type, windows, formWigdet):
    try:
        if type == 'up':
            windows.current_AiStockPage -= 1
        elif type == 'next':
            windows.current_AiStockPage += 1
        # 分页处理
        data = get_page(windows.showAiStockData, windows.current_AiStockPage, 11)
        # 数据类型
        currentIndex = formWigdet.aiStock_dataTypeContion.currentIndex()
        # 涨停板
        if currentIndex == 0:
            # 数据显示处理
            showTableData(data, windows, formWigdet, currentIndex, 19, headerDailylimitTitles, showDailylimitHeaderLables,
                          StockCustomProxyModel())
            # 表格设定
            StockInfoAction.setingStockTable(formWigdet.aiStock_Table)
        # 板块1/概念2
        elif currentIndex == 1 or currentIndex == 2:
            # 数据显示处理
            showTableData(data, windows, formWigdet, currentIndex, 18, headerPlateFundTitles, showPlateFundHeaderLables,
                          PlateFundCustomProxyModel())
            # 表格设定
            PlateFundAction.setingPlateFundTable(formWigdet.aiStock_Table)
        elif currentIndex == 3:
            # 数据显示处理
            showTableData(data, windows, formWigdet, currentIndex, 21, headerIncreaseTitles, showIncreaseHeaderLables,
                          IncreaseCustomProxyModel())
            # 涨幅(4%)以上--数据显示设定
            IncreaseFiveAction.setingTable(formWigdet.aiStock_Table)
    except Exception as ex:
        logger.error(f'翻页处理出错了：{str(ex)}')

# 数据绑定
def editAiStockTable(windows, formWidget):
    # 数据类型
    currentIndex = formWidget.aiStock_dataTypeContion.currentIndex()
    # 检索条件获取
    # 交易日期From
    aiDateFrom = DateTimeUtils.Format_changed(formWidget.aiStock_From.text(), '%Y年%M月%d日', '%Y%M%d')
    # 交易日期To
    aiDateTo = DateTimeUtils.Format_changed(formWidget.aiStock_To.text(), '%Y年%M月%d日', '%Y%M%d')
    # 股票No
    aiStockNo = formWidget.aiStock_No.text()
    # 股票名称
    aiStockName = formWidget.aiStock_Name.text()
    # 涨停板
    if currentIndex == 0:
        getStockData(windows, formWidget, currentIndex, aiDateFrom, aiDateTo, aiStockNo, aiStockName)
        # 涨停板Tab--数据显示设定
        StockInfoAction.setingStockTable(formWidget.aiStock_Table)
    # 板块
    elif currentIndex == 1:
        getPlateFundData(windows, formWidget, 'S', '1', currentIndex, aiDateFrom, aiDateTo, aiStockNo, aiStockName)
        # 板块--数据显示设定
        PlateFundAction.setingPlateFundTable(formWidget.aiStock_Table)
    elif currentIndex == 2:
        getPlateFundData(windows, formWidget, 'S', '2', currentIndex, aiDateFrom, aiDateTo, aiStockNo, aiStockName)
        # 概念--数据显示设定
        PlateFundAction.setingPlateFundTable(formWidget.aiStock_Table)
    elif currentIndex == 3:
        getIncreaseFiveData(windows, formWidget, currentIndex, aiDateFrom, aiDateTo, aiStockNo, aiStockName)
        # 涨幅(4%)以上--数据显示设定
        IncreaseFiveAction.setingTable(formWidget.aiStock_Table)

# 分页处理
def get_page(cached_data, page: int, page_size: int) -> Dict[str, Any]:
    total = len(cached_data)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = cached_data[start:end]

    return {
        "data": paginated,
        "current_page": page,
        "page_size": page_size,
        "total_items": total,
        "total_pages": (total + page_size - 1) // page_size
    }

# 涨幅(4%)以上Tab--数据绑定
def getIncreaseFiveData(windows, formWigdet, indexNo, hangQingDateFrom, hangQingDateTo, masterStockNo, masterStockName):
    # 排序选项
    orderByOption = ' ORDER BY GS.CREATE_DATE DESC'
    # 数据检索
    increaseFiveCondition = IncreaseFiveCondition(hangQingDateFrom, hangQingDateTo, masterStockNo, masterStockName, '',
                                                '', '', '', '', 'D', orderByOption)
    # 添加数据;
    windows.showIncreaseFiveData = IncreaseFiveModel.getIncreaseFiveWLWData(increaseFiveCondition)
    # 数据处理
    windows.reportData = editAiIncreaseFiveData(windows.showIncreaseFiveData, windows, formWigdet)
    windows.showAiStockData = copy.deepcopy(windows.reportData)

    # 设定项目值显示
    if windows.showAiStockData:
        # 总件数format
        formWigdet.aiStock_count_number.setText(f'一共 {len(windows.showAiStockData)} 件数据')
        # 页码初始化
        windows.current_AiStockPage = 1
        # 分页处理
        data = get_page(windows.showAiStockData, windows.current_AiStockPage, 11)
        # 数据显示处理
        showTableData(data, windows, formWigdet, indexNo, 21, headerIncreaseTitles, showIncreaseHeaderLables, IncreaseCustomProxyModel())

# 数据处理
def editAiIncreaseFiveData(showIncreaseFiveData, windows, formWigdet):
    resultData = []

    # 检索数据再次处理
    if showIncreaseFiveData:
        pandasData = pandas.DataFrame(data=showIncreaseFiveData, columns=['交易日期', '所属行业', '股票No', '名称', '涨幅', '现价(元)', '风险种类', '涨跌额', '成交量(手)', '成交额', '振幅', '换手率', '市盈率（动态）',
             '量比', '涨停主题', '概念', '涨停原因', '机构持股数量', 'DEPTH', 'F10URL', 'REPORT', 'hidden'])
        groupStockNo = (pandasData.sort_values('交易日期', ascending=False).groupby(by='所属行业'))
        # 数据栏检索条件处理 END
        for key, value in groupStockNo:
            # 按股票No分组后，取每组最大交易日期对应的股票No
            max_data = value.loc[value['交易日期'].idxmax()].reset_index(drop=True)
            min_data = value.loc[value['交易日期'].idxmin()].reset_index(drop=True)
            qushi = len(value)
            max_data[21] = qushi
            max_data[22] = min_data[0]
            # 机构数据采集日期
            max_data[23] = min_data[21]
            resultData.append(max_data)

    return resultData

# 板块资金Tab--数据绑定
def getPlateFundData(windows, formWigdet, activateType, hyType, indexNo, hangQingDateFrom, hangQingDateTo, plateFund_No, plateFund_Name):
    # 检索条件获取
    # 排序选项
    orderByOption = ' ORDER BY CAST(HC.F62 AS INTEGER) DESC'

    plateFundCondition = PlateFundCondition(hangQingDateFrom, hangQingDateTo, plateFund_No, plateFund_Name, '', '', activateType, '', hyType, orderByOption)
    # 添加数据;
    windows.showAiStockData = PlateFundModel.getPlateFundWLWData(plateFundCondition)
    # 设定项目值显示
    if windows.showAiStockData:
        # 总件数format
        formWigdet.aiStock_count_number.setText(f'一共 {len(windows.showAiStockData)} 件数据')

        # 页码初始化
        windows.current_AiStockPage = 1
        # 分页处理
        data = get_page(windows.showAiStockData, windows.current_AiStockPage, 11)
        # 数据显示处理
        showTableData(data, windows, formWigdet, indexNo, 18, headerPlateFundTitles, showPlateFundHeaderLables, PlateFundCustomProxyModel())

# 涨停板--数据绑定
def getStockData(windows, formWidget, indexNo, saleDayFrom, saleDayTo, stockNo, stockName):
    # 检索条件获取
    # 排序选项
    orderByOption = 'ORDER BY SIW.STOCK_DATE DESC'
    # 检索条件设定
    stockInfoCondition = StockInfoCondition(saleDayFrom, saleDayTo, stockNo, stockName, '', '',
                                            '',
                                            '', '', '', '', '', '',
                                            '',
                                            '', '', '', '', 'D',
                                            orderByOption)

    # 数据检索;
    windows.showAiStockData = StockInfoModel.getStockInfoWLWData(stockInfoCondition)
    # 设定项目值显示
    if windows.showAiStockData:
        # 总件数format
        formWidget.aiStock_count_number.setText(f'一共 {len(windows.showAiStockData)} 件数据')

        # 页码初始化
        windows.current_AiStockPage = 1
        # 分页处理
        data = get_page(windows.showAiStockData, windows.current_AiStockPage, 11)
        # 数据显示处理
        showTableData(data, windows, formWidget, indexNo,19, headerDailylimitTitles, showDailylimitHeaderLables, StockCustomProxyModel())

# 数据显示处理
def showTableData(data, windows, formWigdet, indexNo, simCount, headerTitles, showHeaderLables, customSortmodel):
    # ListView model 4Row 3 coloumn
    windows.aiStockModel = QStandardItemModel(0, simCount)
    # 创建行标题
    windows.aiStockModel.setHorizontalHeaderLabels(headerTitles)
    if data['data']:
        for row, item in enumerate(data['data']):
            # 涨停板
            if indexNo == 0 or indexNo == 3:
                windows.aiStockModel.appendRow(
                    [setQStandardItem(str(item[value]), str(item[value])) for value in showHeaderLables])
            # 概念/板块
            elif indexNo == 1 or indexNo == 2:
                windows.aiStockModel.appendRow([PlateFundAction.setQStandardItem(str(item[value]), value) for value in showHeaderLables])

    # 页码格式化
    formWigdet.aiStock_PageNo.setText(f' 第 {data["current_page"]} 页 ')
    if data["current_page"] == 1:
        # 第一页时，上一页按钮不显示【setVisible(True)】
        formWigdet.aiStock_upPlate.setVisible(False)
        nextFlag = True
        if len(windows.showAiStockData) <= 11:
            nextFlag = False
        formWigdet.aiStock_nextPlate.setVisible(nextFlag)

    elif data["current_page"] == data["total_pages"]:
        # 最后一页时，下一页按钮不显示【setVisible(True)】
        formWigdet.aiStock_upPlate.setVisible(True)
        formWigdet.aiStock_nextPlate.setVisible(False)

    else:
        formWigdet.aiStock_upPlate.setVisible(True)
        formWigdet.aiStock_nextPlate.setVisible(True)

    customSortmodel.setSourceModel(windows.aiStockModel)
    formWigdet.aiStock_Table.setModel(customSortmodel)
    # data 显示
    formWigdet.aiStock_Table.setVisible(True)

# 事件绑定 -- 清除按钮事件
def AddClickedNoticClear(windows, formWidget):
    try:
        aiStockInitContent(windows, formWidget)
    except Exception as ex:
        logger.error(f'清除处理出错了：{str(ex)}')


