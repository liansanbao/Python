# _*_ coding: utf-8 _*_
# @Time : 2026/3/3 星期二 17:10
# @Author : 韦丽
# @Version: V 1.1
# @File : AiStockAction.py
# @desc : Ai诊股处理
import copy
import json
from functools import partial
from string import Template
from typing import Dict, Any, List, Optional

import pandas
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import QDate, QTimer, QThread, pyqtSignal, Qt
from PyQt6.QtGui import QStandardItemModel, QIcon, QPixmap, QFont, QTextCursor, QColor
from PyQt6.QtWidgets import (
    QVBoxLayout, QTextEdit, QHBoxLayout, QLineEdit, QPushButton, QMessageBox
)
from openai import OpenAI

from WLW.StockBase import DateTimeUtils
from WLW.Tools.CommonUtils import setQStandardItem, setQStandardItemPlateFund
from WLW.Tools.LoggingEx import logger
from WLW.action import StockInfoAction, PlateFundAction, IncreaseFiveAction
from WLW.action.MultiDailySortProxyModel import CustomProxyModel as StockCustomProxyModel
from WLW.action.MultiPlateFundSortProxyModel import CustomProxyModel as PlateFundCustomProxyModel
from WLW.action.MultiIncreaseSortProxyModel import CustomProxyModel as IncreaseCustomProxyModel
from WLW.model import StockInfoModel, PlateFundModel, IncreaseFiveModel
from WLW.model.IncreaseFiveCondition import IncreaseFiveCondition
from WLW.model.PlateFundCondition import PlateFundCondition
from WLW.model.StockInfoCondition import StockInfoCondition

# ====================== 常量定义区 ======================
# 涨停板
HEADER_DAILY_LIMIT = [
    '交易日期', '所属行业', '股票No', '名称', '涨跌幅', '最新价', '连板数', '炸板次数',
    '风险种类', '游资', '成交额', '换手率', 'F封板时间', 'L封板时间', '封板资金',
    '涨停统计', '涨停主题', '涨停原因', '机构持股数量', 'hidden'
]
LIMIT_AI_KEYS = [
    '交易日期', '所属行业', '股票代码', '名称', '涨跌幅', '最新价', '连板数', '炸板次数',
    '风险种类', '游资', '成交额', '换手率', 'F封板时间', 'L封板时间', '封板资金',
    '涨停统计', '涨停主题', '涨停原因', '机构持股数量'
]
SHOW_DAILY_LIMIT_HEADER = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

# 板块/概念
HEADER_PLATE_FUND = [
    '交易日期', '板块代码', '板块名称', '最新价', '涨跌幅', '主力B(净额)', '主力B(净占比)',
    '优秀股名称', '优秀股代码', '持股机构数', '涨停主题', '概念', '涨停原因', '涨幅',
    '价格', '成交量(手)', '成交额', '换手率', 'hidden'
]
PLATE_FUND_AI_KEYS = [
    '交易日期', '板块代码', '板块名称', '最新价', '涨跌幅', '主力B(净额)', '主力B(净占比)',
    '优秀股名称', '优秀股代码', '持股机构数', '涨停主题', '概念', '涨停原因', '涨幅',
    '价格', '成交量(手)', '成交额', '换手率'
]
SHOW_PLATE_FUND_HEADER = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]

# 涨幅4%以上
HEADER_INCREASE = [
    '股票No', '名称', '交易日期', '所属行业', '涨幅', '现价(元)', '风险种类', '涨跌额',
    '成交量(手)', '成交额', '振幅', '换手率', '市盈率', '量比', '涨停主题', '概念',
    '涨停原因', '机构数', '上榜次数', '首次交易日', 'hidden'
]
INCREASE_AI_KEYS = [
    '股票No', '名称', '交易日期', '所属行业', '涨幅', '现价(元)', '风险种类', '涨跌额',
    '成交量(手)', '成交额', '振幅', '换手率', '市盈率', '量比', '涨停主题', '概念',
    '涨停原因', '机构数', '上榜次数', '首次交易日'
]
SHOW_INCREASE_HEADER = [2, 3, 0, 1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 21, 22, 23]

# AI 配置
AI_BATCH_SIZE = 13
AI_MAX_SEND_COUNT = 13
PAGE_SIZE = 11
OLLAMA_BASE_URL= 'https://ai.lisibao.top/v1'
# OLLAMA_BASE_URL = "http://192.168.56.100:11434/v1"
# OLLAMA_BASE_URL = "http://192.168.1.17:11434/v1"
OLLAMA_API_KEY = "sk-ollama-model-lisibao"
OLLAMA_MODEL_NAME = "qwen2.5:1.5b-instruct"

# Prompt模板
SYSTEM_PROMPT_TPL = Template("""
<|im_start|>system
你是短线资金分析师。
=====【强制禁令，优先级最高，违反即错误】=====
1. 只能使用本次给到的涨停个股原始数据，**严禁编造数据、严禁预测涨跌**
2. 禁止输出任何K线、股票理论、指标科普、通用炒股知识
3. 禁止引入外部行情、新闻、大盘信息，只看传入数据
4. 不允许自由发挥文字，严格按指定顺序、指定模块输出

=====【可用指标，仅下面7个，只认这7个字段】=====
1. 连板数：首板/2连板/3连板；越高=题材抱团越强
2. 游资标记：有=存在游资跟踪标记
3. 换手率：数值越高筹码交换越活跃
4. 量比：＞3 = 当日放量、主力异动
5. 封单金额：数值越大，主力做多意愿越强
6. 封板时间：早盘封板资金更强；封板时间≠开板时间=炸板、分歧大
7. 题材：同一题材涨停个股数量越多，为主线题材，是主力主攻方向

=====【固定输出顺序&格式，严格遵守，缺数据写“无”】=====
1. 题材归类汇总：主线题材（题材名+涨停家数）、次主线题材（题材名+涨停家数）、零散题材（题材名+涨停家数）
2. 主力资金偏好方向：明确结论；理由**只能从这5点选取：涨停家数、放量个股(量比>3)数量、封单大小、连板高度、炸板分歧情况**，不要用其他理由
3. 题材风险提示：列出炸板多、封单偏小、分歧大的题材；没有则写：无

=====【执行步骤】=====
第一步：先统计所有个股，按题材分组，统计每个题材涨停数量、炸板数量、量比>3数量、最高连板、封单情况；
第二步：对照统计结果，按上面3段格式输出；
第三步：输出前自查：有没有科普、有没有预测涨跌、有没有编造数据。

=====【传入数据】=====
涨停个股数据：${stock_json_data}
用户提问：${user_input}
<|im_end|>
<|im_start|>user
请按规则分析
<|im_end|>
<|im_start|>assistant
""")

# ====================== 线程Worker ======================
class ModelWorker(QThread):
    response_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, messages: List[Dict[str, str]]):
        super().__init__()
        self.messages = messages
        self.client = OpenAI(
            api_key=OLLAMA_API_KEY,
            base_url=OLLAMA_BASE_URL,
        )
        self.model_type = OLLAMA_MODEL_NAME
        self._stop_flag = False

    # 千问大模型执行
    def run(self):
        try:
            completion = self.client.chat.completions.create(
                model=self.model_type,
                messages=self.messages,
                # 通过 extra_body 设置 enable_thinking 开启思考模式
                # extra_body={"enable_thinking": True},
                stream=True,
                stream_options={
                    "include_usage": True
                },
            )

            full_response = ""
            for chunk in completion:
                if self._stop_flag:
                    break
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta

                # # 只收集思考内容
                # if hasattr(delta, "reasoning_content") and delta.reasoning_content is not None:
                #     full_response += delta.reasoning_content
                #     self.response_received.emit(full_response, 0)
                #
                # # 收到content，开始进行回复
                # if hasattr(delta, "content") and delta.content:
                #     full_response += delta.content
                #     self.response_received.emit(full_response, 0)
                content = ""
                if hasattr(delta, "reasoning_content") and delta.reasoning_content:
                    content = delta.reasoning_content
                if hasattr(delta, "content") and delta.content:
                    content = delta.content
                if content:
                    self.response_received.emit(content)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def stop(self):
        self._stop_flag = True

# ====================== UI初始化 ======================
def aiStockInitContent(windows, formWidget, optionType: str = '0'):
    # 基础控件重置
    # 股票No、板块No、概念No
    formWidget.aiStock_No.setText('')
    # 股票名称、板块名称、概念名称
    formWidget.aiStock_Name.setText('')
    # 总件数format
    formWidget.aiStock_count_number.setText(f'一共 0 件数据')

    # 当前周開始日取得
    weekFromDay = DateTimeUtils.Week_Day_Date(weekDay=1)

    q_week_start = QDate(weekFromDay.year, weekFromDay.month, weekFromDay.day)
    q_today = QDate.currentDate()

    # 交易日期From 显示格式
    formWidget.aiStock_From.setDate(q_week_start)
    # 交易日期From 可选最大日期
    formWidget.aiStock_From.setMaximumDate(q_today)
    # 交易日期From 日历控件弹出
    formWidget.aiStock_From.setCalendarPopup(True)

    # 交易日期To 显示格式
    formWidget.aiStock_To.setDate(q_today)
    # 交易日期To 可选最大日期
    formWidget.aiStock_To.setMaximumDate(q_today)
    # 交易日期To 日历控件弹出
    formWidget.aiStock_To.setCalendarPopup(True)

    if optionType == '0':
        # AI layout START
        vbox = QVBoxLayout()

        # 聊天区域
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

        # 输入行
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
        formWidget.send_btn = QPushButton('诊股')
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
        # 处理中，发送按钮不可操作
        formWidget.send_btn.setEnabled(True)

        hbox.addWidget(formWidget.input_box)
        hbox.addWidget(formWidget.send_btn)
        vbox.addLayout(hbox)

        formWidget.aiStock_groupBox.setLayout(vbox)

        # 计时器
        windows.timer = QTimer()
        windows.timer.timeout.connect(partial(update_timer, windows, formWidget))

    formWidget.chat_display.setText('')
    formWidget.input_box.setText('')
    windows.seconds_elapsed = 0
    windows.worker: Optional[ModelWorker] = None
    windows.is_streaming = False
    windows._stream_started = False
    # AI layout END

    # 数据类型
    formWidget.aiStock_dataTypeContion.clear()
    formWidget.aiStock_dataTypeContion.addItems(['涨停板', '板块', '概念', '涨幅%4以上'])
    formWidget.aiStock_dataTypeContion.setCurrentIndex(0)
    formWidget.aiStock_dataTypeContion.setMinimumHeight(26)
    formWidget.aiStock_dataTypeContion.currentIndexChanged.connect(
        lambda index: on_aiStock_dataTypeContion_selection_change(index, formWidget, windows)
    )

    # 翻页图标
    upIcon = QIcon()
    upIcon.addPixmap(QPixmap("_internal/image/upPage.svg"), QIcon.Mode.Normal, QIcon.State.Off)
    formWidget.aiStock_upPlate.setIcon(upIcon)
    # 下一页
    nextIcon = QIcon()
    nextIcon.addPixmap(QPixmap("_internal/image/nextPage.svg"), QIcon.Mode.Normal, QIcon.State.Off)
    formWidget.aiStock_nextPlate.setIcon(nextIcon)
    # 股票类型数据
    windows.showAiStockData = None

# ====================== AI数据清洗 ======================
def editAskAIData(messages: list):
    clean_list = []
    for item in messages:
        # 截取前17项，丢弃后面url、无用数字
        row = item[:17]
        obj = dict(zip(LIMIT_AI_KEYS, row))
        # 清理空格
        obj["连板数"] = obj["连板数"].strip()
        clean_list.append(obj)

    # 分批，每批10条（适配1.5B）
    batches = [clean_list[i:i + AI_BATCH_SIZE] for i in range(0, len(clean_list), AI_BATCH_SIZE)]
    return json.dumps(batches[0], ensure_ascii=False, indent=2)

# ====================== AI问答主逻辑 ======================
def ask_model(windows, formWidget):
    # 防重复提交锁
    if getattr(windows, "is_streaming", False):
        return

    try:
        windows.user_input = formWidget.input_box.text().strip()
        msgContent = ""
        execFlag = False

        if not windows.user_input:
            msgContent = "请描述你的问题。"

        # 股票数据验证
        elif not windows.showAiStockData or len(windows.showAiStockData) == 0:
            msgContent = "数据没有了，不能使用AI大模型。"
        elif len(windows.showAiStockData) > AI_MAX_SEND_COUNT:
            msgContent = f"诊股件数超过{AI_MAX_SEND_COUNT}件了，自动截取TOP{AI_MAX_SEND_COUNT}件数据进行诊股。"
            execFlag = True

        if msgContent:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.NoIcon)
            msg.setWindowTitle('AI诊股')
            msg.setWindowIcon(QtGui.QIcon("_internal/image/wlw.svg"))
            msg.setText(msgContent)
            # 设置消息框大小
            msg.setFixedSize(800, 800)  # 宽度800像素，高度800像素
            # 添加确定按钮
            if not execFlag:
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            else:
                msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)

            # 可选：默认选中OK按钮
            msg.setDefaultButton(QMessageBox.StandardButton.Ok)
            ret = msg.exec()
            # 判断：点击取消 → 终止；点击OK → 继续往下走
            if ret == QMessageBox.StandardButton.Cancel:
                return

            if not execFlag and ret == QMessageBox.StandardButton.Ok:
                return

        # 开始流式
        formWidget.chat_display.clear()
        windows.seconds_elapsed = 0
        windows.is_streaming = True
        windows._stream_started = False
        start_timer(windows, formWidget)
        # 处理中，发送按钮不可操作
        formWidget.send_btn.setEnabled(False)

        aiAskData = copy.deepcopy(windows.showAiStockData)

        # 零时编辑数据
        resultData = editAskAIData(aiAskData)
        # 组装prompt
        # system_content = SYSTEM_PROMPT_TPL.substitute(
        #     stock_json_data=resultData,
        #     user_input=windows.user_input
        # )

        messages = [
            {"role": "user", "content": f"{windows.user_input}，\n下面是个股数据：{resultData}"}]

        # messages = [
        #     {"role": "system", "content": system_prompt},
        #     {"role": "user", "content": f"下面是个股数据：{resultData}\n{windows.user_input}，按照上面规则输出"}]

        # 显示初始等待信息
        formWidget.chat_display.setPlainText(f"思考中...\n已等待 0 秒")

        windows.worker = ModelWorker(messages)
        windows._stream_started = False
        windows.worker.response_received.connect(partial(handle_response, windows, formWidget))
        windows.worker.error_occurred.connect(partial(handle_error, windows, formWidget))
        windows.worker.finished.connect(windows.worker.deleteLater)
        windows.worker.start()
    except Exception as e:
        logger.error(f'ask_model出错误了：{e}', exc_info=True)
        # 处理中，发送按钮可操作
        formWidget.send_btn.setEnabled(True)
        windows.is_streaming = False

def start_timer(windows, formWidget):
    windows.timer.start(1000)  # 每秒触发一次

def update_timer(windows, formWidget):
    if not windows.is_streaming:
        return

    windows.seconds_elapsed += 1
    # 更新计时显示，但不覆盖已有的回复内容
    current_text = formWidget.chat_display.toPlainText()
    if "思考中..." in current_text:
        # 如果还在等待阶段，更新计时
        lines = current_text.split('\n')
        if len(lines) > 1:
            lines[1] = f"已等待 {windows.seconds_elapsed} 秒"
            formWidget.chat_display.setPlainText('\n'.join(lines))

def handle_response(windows, formWidget, response_text: str):
    # 首个增量到达：停止等待计时，写入问题标题
    if windows.is_streaming:
        windows.timer.stop()
        windows.is_streaming = False
        # 清空问题区域
        formWidget.input_box.clear()
        # 处理完了，发送按钮可操作
        formWidget.send_btn.setEnabled(True)
        formWidget.chat_display.setPlainText(f"问题：{windows.user_input}\n"
                                             f"-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n"
                                             f"AI耗时 {windows.seconds_elapsed} 秒\n\n")
        windows._stream_started = True

    # 增量追加，避免每个 token 都重设整段文本（O(n²) 布局开销）
    display = formWidget.chat_display
    cursor = display.textCursor()
    cursor.movePosition(QTextCursor.MoveOperation.End)
    display.setTextCursor(cursor)
    display.insertPlainText(response_text)

def handle_error(windows, formWidget, error_msg):
    windows.timer.stop()
    windows.is_streaming = False
    windows._stream_started = False
    formWidget.chat_display.setPlainText(f"[错误]\n请求失败: {error_msg}")
    # 处理完了，发送按钮可操作
    formWidget.send_btn.setEnabled(True)

# ====================== 下拉切换事件 ======================
def on_aiStock_dataTypeContion_selection_change(currentIndex, formWigdet, windows):
    try:
        _translate = QtCore.QCoreApplication.translate
        if currentIndex in (0, 3):
            placeText = '股票'
        elif currentIndex == 1:
            placeText = '板块'
        elif currentIndex == 2:
            placeText = '概念'
        else:
            placeText = '股票'
        formWigdet.aiStock_No.setPlaceholderText(_translate("WLW", f"{placeText}代码"))
        formWigdet.aiStock_Name.setPlaceholderText(_translate("WLW", f"{placeText}名称"))
        clearShowTable(windows, formWigdet)
    except Exception as ex:
        logger.error(f'涨幅下拉框处理出错了：{str(ex)}', exc_info=True)

# ====================== 表格清空 ======================
def clearShowTable(windows, formWigdet):
    windows.showAiStockData = None
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
    # 数据绑定
    editAiStockTable(windows, formWigdet)

# ====================== 事件绑定入口 ======================
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

def AddClickedNoticClear(windows, formWidget):
    try:
        aiStockInitContent(windows, formWidget, '1')
    except Exception as ex:
        logger.error(f'清除处理出错了：{str(ex)}', exc_info=True)

# ====================== 分页逻辑 ======================
def get_page(cached_data: Optional[List], page: int, page_size: int) -> Dict[str, Any]:
    if not cached_data:
        return {
            "data": [],
            "current_page": page,
            "page_size": page_size,
            "total_items": 0,
            "total_pages": 0
        }
    total = len(cached_data)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = cached_data[start:end]
    total_pages = (total + page_size - 1) // page_size
    return {
        "data": paginated,
        "current_page": page,
        "page_size": page_size,
        "total_items": total,
        "total_pages": total_pages
    }

# 事件绑定 -- 翻页处理
def AddClickedStockPage(page_type: str, windows, formWidget):
    try:
        if page_type == 'up':
            windows.current_AiStockPage -= 1
        elif page_type == 'next':
            windows.current_AiStockPage += 1
        # 分页处理
        page_data = get_page(windows.showAiStockData, windows.current_AiStockPage, 11)
        # 数据类型
        currentIndex = formWidget.aiStock_dataTypeContion.currentIndex()
        # 涨停板
        if currentIndex == 0:
            # 数据显示处理
            showTableData(page_data, windows, formWidget, currentIndex, 19, HEADER_DAILY_LIMIT,
                          SHOW_DAILY_LIMIT_HEADER, StockCustomProxyModel())
            # 表格设定
            StockInfoAction.setingStockTable(formWidget.aiStock_Table)
        # 板块1/概念2
        elif currentIndex == 1 or currentIndex == 2:
            # 数据显示处理
            showTableData(page_data, windows, formWidget, currentIndex, 18, HEADER_PLATE_FUND, SHOW_PLATE_FUND_HEADER,
                          PlateFundCustomProxyModel())
            # 表格设定
            PlateFundAction.setingPlateFundTable(formWidget.aiStock_Table)
        elif currentIndex == 3:
            # 数据显示处理
            showTableData(page_data, windows, formWidget, currentIndex, 21, HEADER_INCREASE, SHOW_INCREASE_HEADER,
                          IncreaseCustomProxyModel())
            # 涨幅(4%)以上--数据显示设定
            IncreaseFiveAction.setingTable(formWidget.aiStock_Table)
    except Exception as ex:
        logger.error(f'翻页处理出错了：{str(ex)}')

# ====================== 检索主入口 ======================
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
    # 检索条件输出
    logger.info(
        f'检索条件: 数据类型={currentIndex}, 交易日期:({aiDateFrom}--{aiDateTo}), 股票No={aiStockNo}, 股票名称={aiStockName}')

    # 涨停板
    if currentIndex == 0:
        getStockData(windows, formWidget, currentIndex, aiDateFrom, aiDateTo, aiStockNo, aiStockName)
    # 板块
    elif currentIndex == 1:
        getPlateFundData(windows, formWidget, 'S', '1', currentIndex, aiDateFrom, aiDateTo, aiStockNo, aiStockName)
    elif currentIndex == 2:
        getPlateFundData(windows, formWidget, 'S', '2', currentIndex, aiDateFrom, aiDateTo, aiStockNo, aiStockName)
    elif currentIndex == 3:
        getIncreaseFiveData(windows, formWidget, currentIndex, aiDateFrom, aiDateTo, aiStockNo, aiStockName)

# ====================== 数据源：涨幅4%以上 ======================
def getIncreaseFiveData(windows, formWidget, indexNo, hangQingDateFrom, hangQingDateTo, masterStockNo, masterStockName):
    # 排序选项
    orderByOption = ' ORDER BY GS.CREATE_DATE DESC'
    # 数据检索
    increaseFiveCondition = IncreaseFiveCondition(hangQingDateFrom, hangQingDateTo, masterStockNo, masterStockName, '',
                                                  '', '', '', '', 'D', orderByOption)
    # 添加数据;
    windows.showIncreaseFiveData = IncreaseFiveModel.getIncreaseFiveWLWData(increaseFiveCondition)
    # 数据处理
    windows.reportData = editAiIncreaseFiveData(windows.showIncreaseFiveData)
    windows.showAiStockData = copy.deepcopy(windows.reportData)

    # 设定项目值显示
    if windows.showAiStockData:
        # 总件数format
        formWidget.aiStock_count_number.setText(f'共 {len(windows.showAiStockData)} 条')
        # 页码初始化
        windows.current_AiStockPage = 1
        # 分页处理
        page_data = get_page(windows.showAiStockData, windows.current_AiStockPage, 11)
        # 数据显示处理
        showTableData(page_data, windows, formWidget, indexNo, 21, HEADER_INCREASE, SHOW_INCREASE_HEADER,
                      IncreaseCustomProxyModel())
    else:
        # 分页按钮不显示
        formWidget.aiStock_upPlate.setVisible(False)
        formWidget.aiStock_nextPlate.setVisible(False)
        # 页码格式化
        formWidget.aiStock_PageNo.setText('')

    # 涨幅(4%)以上--数据显示设定
    IncreaseFiveAction.setingTable(formWidget.aiStock_Table)

# 数据处理
def editAiIncreaseFiveData(showIncreaseFiveData) -> List:
    resultData = []
    if not showIncreaseFiveData:
        return resultData

    # 检索数据再次处理
    pandasData = pandas.DataFrame(data=showIncreaseFiveData,
                                  columns=[
                                      '交易日期', '所属行业', '股票No', '名称', '涨幅', '现价(元)', '风险种类',
                                           '涨跌额', '成交量(手)', '成交额', '振幅', '换手率', '市盈率（动态）',
                                           '量比', '涨停主题', '概念', '涨停原因', '机构持股数量', 'DEPTH',
                                           'F10URL', 'REPORT', 'hidden'
                                      ]
                                  )
    groupStockNo = (pandasData.sort_values('交易日期', ascending=False).groupby(by='所属行业'))
    # 数据栏检索条件处理 END
    for _, group_df in groupStockNo:
        # 按股票No分组后，取每组最大交易日期对应的股票No
        max_data = group_df.loc[group_df['交易日期'].idxmax()].reset_index(drop=True)
        min_data = group_df.loc[group_df['交易日期'].idxmin()].reset_index(drop=True)
        qushi = len(group_df)
        max_data[21] = qushi
        max_data[22] = min_data[0]
        # 机构数据采集日期
        max_data[23] = min_data[21]
        resultData.append(max_data.tolist())

    return resultData

# ====================== 数据源：板块/概念 ======================
def getPlateFundData(windows, formWidget, activateType, hyType, indexNo, hangQingDateFrom, hangQingDateTo, plateFund_No,
                     plateFund_Name):
    # 检索条件获取
    # 排序选项
    orderByOption = ' ORDER BY CAST(HC.F62 AS INTEGER) DESC'
    plateFundCondition = PlateFundCondition(hangQingDateFrom, hangQingDateTo, plateFund_No, plateFund_Name, '', '',
                                            activateType, '', hyType, orderByOption)
    # 添加数据;
    windows.showAiStockData = PlateFundModel.getPlateFundWLWData(plateFundCondition)
    # 设定项目值显示
    if windows.showAiStockData:
        # 总件数format
        formWidget.aiStock_count_number.setText(f'共 {len(windows.showAiStockData)} 条')

        # 页码初始化
        windows.current_AiStockPage = 1
        # 分页处理
        data = get_page(windows.showAiStockData, windows.current_AiStockPage, 11)
        # 数据显示处理
        showTableData(data, windows, formWidget, indexNo, 18, HEADER_PLATE_FUND, SHOW_PLATE_FUND_HEADER,
                      PlateFundCustomProxyModel())
    else:
        # 分页按钮不显示
        formWidget.aiStock_upPlate.setVisible(False)
        formWidget.aiStock_nextPlate.setVisible(False)
        # 页码格式化
        formWidget.aiStock_PageNo.setText('')

    # 概念--数据显示设定
    PlateFundAction.setingPlateFundTable(formWidget.aiStock_Table)

# ====================== 数据源：涨停板 ======================
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
        formWidget.aiStock_count_number.setText(f'共 {len(windows.showAiStockData)} 条')

        # 页码初始化
        windows.current_AiStockPage = 1
        # 分页处理
        page_data = get_page(windows.showAiStockData, windows.current_AiStockPage, 11)
        # 数据显示处理
        showTableData(page_data, windows, formWidget, indexNo, 19, HEADER_DAILY_LIMIT, SHOW_DAILY_LIMIT_HEADER,
                      StockCustomProxyModel())
    else:
        # 分页按钮不显示
        formWidget.aiStock_upPlate.setVisible(False)
        formWidget.aiStock_nextPlate.setVisible(False)
        # 页码格式化
        formWidget.aiStock_PageNo.setText('')

    # 涨停板Tab--数据显示设定
    StockInfoAction.setingStockTable(formWidget.aiStock_Table)

# ====================== 表格渲染（统一入口） ======================
def showTableData(page_data: dict, windows, formWidget, indexNo, simCount, headerTitles, showHeaderLables, customSortmodel):
    # ListView model 4Row 3 coloumn
    windows.aiStockModel = QStandardItemModel(0, simCount)
    # 创建行标题
    windows.aiStockModel.setHorizontalHeaderLabels(headerTitles)
    if page_data['data']:
        for row, item in enumerate(page_data['data']):
            row_items = []
            # 涨停板
            if indexNo == 0:
                for col_idx, key in enumerate(showHeaderLables):
                    cell_text = str(item[key])
                    std_item = setQStandardItem(cell_text, cell_text)
                    # ========== 文字居中 ==========
                    std_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                    # 预计算颜色
                    if col_idx in (2, 3):
                        # 股票代码、名称蓝色
                        std_item.setForeground(QColor("blue"))
                    elif col_idx == 4:  # 涨跌幅
                        try:
                            val = float(cell_text.replace("%", "").replace(",", ""))
                            if val >= 0:
                                std_item.setForeground(QColor("red"))
                            else:
                                std_item.setForeground(QColor("#009455"))
                        except:
                            pass
                    elif col_idx == 5:  # 最新价
                        std_item.setForeground(QColor("red"))
                    # ✅ 加粗：F封板时间、L封板时间
                    elif col_idx in (12, 13):
                        bold_font = QFont()
                        bold_font.setBold(True)
                        std_item.setFont(bold_font)
                    row_items.append(std_item)
            # 概念/板块
            elif indexNo == 1 or indexNo == 2:
                # windows.aiStockModel.appendRow(
                #     [PlateFundAction.setQStandardItem(str(item[value]), value) for value in showHeaderLables])
                for col_idx, key in enumerate(showHeaderLables):
                    cell_text = str(item[key])
                    std_item = setQStandardItemPlateFund(cell_text, key)
                    # ========== 文字居中 ==========
                    std_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                    # 预计算颜色
                    if col_idx in (1, 2):
                        # 股票代码、名称蓝色
                        std_item.setForeground(QColor("blue"))
                    elif col_idx in (4, 5, 6, 13, 16, 17):  # 涨跌幅
                        try:
                            val = float(cell_text.replace("亿", "").replace("元", "").replace("%", "").replace(",", ""))
                            if val >= 0:
                                std_item.setForeground(QColor("red"))
                            else:
                                std_item.setForeground(QColor("#009455"))
                        except:
                            pass
                    # ✅ 加粗：F封板时间、L封板时间
                    elif col_idx in (10,):
                        bold_font = QFont()
                        bold_font.setBold(True)
                        std_item.setFont(bold_font)

                    row_items.append(std_item)
            elif indexNo == 3:
                # 涨幅4%以上
                # windows.aiStockModel.appendRow(
                #     [setQStandardItem(str(item[value]), str(item[value])) for value in showHeaderLables])
                for col_idx, key in enumerate(showHeaderLables):
                    cell_text = str(item[key])
                    std_item = setQStandardItem(cell_text, cell_text)
                    # ========== 文字居中 ==========
                    std_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                    # 预计算颜色
                    if col_idx in (0, 1):
                        # 股票代码、名称蓝色
                        std_item.setForeground(QColor("blue"))
                    elif col_idx in (4, 7):  # 涨跌幅
                        try:
                            val = float(cell_text.replace("%", "").replace(",", ""))
                            if val >= 0:
                                std_item.setForeground(QColor("red"))
                            else:
                                std_item.setForeground(QColor("#009455"))
                        except:
                            pass
                    # ✅ 加粗：F封板时间、L封板时间
                    elif col_idx in (14, 16):
                        bold_font = QFont()
                        bold_font.setBold(True)
                        std_item.setFont(bold_font)

                    row_items.append(std_item)
            windows.aiStockModel.appendRow(row_items)
    # 页码格式化
    formWidget.aiStock_PageNo.setText(f' 第 {page_data["current_page"]} 页 ')
    if page_data["current_page"] == 1:
        # 第一页时，上一页按钮不显示【setVisible(True)】
        formWidget.aiStock_upPlate.setVisible(False)
        nextFlag = True
        if len(windows.showAiStockData) <= 11:
            nextFlag = False
        formWidget.aiStock_nextPlate.setVisible(nextFlag)

    elif page_data["current_page"] == page_data["total_pages"]:
        # 最后一页时，下一页按钮不显示【setVisible(True)】
        formWidget.aiStock_upPlate.setVisible(True)
        formWidget.aiStock_nextPlate.setVisible(False)

    else:
        formWidget.aiStock_upPlate.setVisible(True)
        formWidget.aiStock_nextPlate.setVisible(True)

    customSortmodel.setSourceModel(windows.aiStockModel)
    formWidget.aiStock_Table.setModel(customSortmodel)
    # data 显示
    formWidget.aiStock_Table.setVisible(True)

    # ===================== 新增：连续行号 =======================================================
    page_no = page_data["current_page"]
    page_size = page_data["page_size"]
    offset = (page_no - 1) * page_size
    v_header = formWidget.aiStock_Table.verticalHeader()
    if hasattr(v_header, "setStartOffset"):
        logger.info(f"page_no: {page_no}, page_size: {page_size}, offset: {offset}")
        v_header.setStartOffset(offset)
    # ==========================================================================================

# 事件绑定 -- 清除按钮事件
def AddClickedNoticClear(windows, formWidget):
    try:
        aiStockInitContent(windows, formWidget, '1')
    except Exception as ex:
        logger.error(f'清除处理出错了：{str(ex)}')
