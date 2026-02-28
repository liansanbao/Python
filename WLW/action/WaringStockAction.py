# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/3/8 17:05
# @Author : 连三保
# @Version: V 1.0
# @File : WaringStockAction.py
# @desc : 风险个股Tab数据处理

from functools import partial
from typing import Dict, Any

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *   # 从 PyQt6 中导入所需的类

from WLW.StockBase import DateTimeUtils
from WLW.Tools.CommonUtils import setQStandardItem
from WLW.Tools.LoggingEx import logger
from WLW.action.MultiWaringSortProxyModel import CustomProxyModel
from WLW.model import WaringStockModel
from WLW.model.WaringStockCondition import WaringStockCondition

# 风险个股Tab(初期化)
def waringStockInitContent(windows, formWigdet):
    # 股票No、股票名称、所属行业输入框空白设定
    formWigdet.waring_stockNo.setText('')
    # 设置只能输入6位0-9的数字
    formWigdet.waring_stockNo.setNumberWithRange(6)
    formWigdet.waring_stockName.setText('')
    formWigdet.waring_suoShuHangYe.setText('')
    # 风险种类 '全部'设定
    formWigdet.waring_stockType.clear()
    formWigdet.waring_stockType.addItems(['全部', '频发风险', '触发风险', '商誉风险', '近期解禁', '退市风险', '立案调查'])
    formWigdet.waring_stockType.setCurrentIndex(5)
    formWigdet.waring_stockType.setMinimumHeight(26)
    # formWigdet.label_19.setText(str(formWigdet.waring_stockType.currentIndex()))

    # 当前周開始日取得
    weekFromDay = DateTimeUtils.Week_Day_Date(weekDay=1)

    # 交易日期From 显示格式
    formWigdet.waringDateFrom.setDate(QDate(weekFromDay.year, 1, 1))
    # 交易日期From 可选最大日期
    formWigdet.waringDateFrom.setMaximumDate(QDate.currentDate().addDays(0))
    # 交易日期From 可选最小日期
    # formWigdet.waringDateFrom.setMinimumDate(QDate.currentDate().addDays(-30))
    # 交易日期From 日历控件弹出
    formWigdet.waringDateFrom.setCalendarPopup(True)

    # 交易日期To 显示格式
    formWigdet.waringDateTo.setDate(QDate(weekFromDay.year, 12, 31))
    # 交易日期To 可选最大日期
    # formWigdet.waringDateTo.setMaximumDate(QDate.currentDate().addDays(0))
    # 交易日期To 可选最小日期
    # formWigdet.waringDateTo.setMinimumDate(QDate.currentDate().addDays(-30))
    # 交易日期To 日历控件弹出
    formWigdet.waringDateTo.setCalendarPopup(True)

    # 上一页
    upIcon = QIcon()
    upIcon.addPixmap(QPixmap("_internal/image/upPage.svg"), QIcon.Mode.Normal, QIcon.State.Off)
    formWigdet.upWaringPage.setIcon(upIcon)
    # 下一页
    nextIcon = QIcon()
    nextIcon.addPixmap(QPixmap("_internal/image/nextPage.svg"), QIcon.Mode.Normal, QIcon.State.Off)
    formWigdet.nextWaringPage.setIcon(nextIcon)

# 风险个股Tab(事件绑定)
def waringStockActionSetting(windows, formWigdet):
    # 事件绑定 -- 检索
    formWigdet.waring_stockSubmit.clicked.connect(partial(AddWaringClickedStockSubmit, windows, formWigdet))
    # 事件绑定 -- 清除
    formWigdet.waring_stockClear.clicked.connect(partial(AddWaringClickedStockClear, windows, formWigdet))
    # 事件绑定 -- 上一页
    formWigdet.upWaringPage.clicked.connect(partial(AddClickedWaringPage, 'up', windows, formWigdet))
    # 事件绑定 -- 下一页
    formWigdet.nextWaringPage.clicked.connect(partial(AddClickedWaringPage, 'next', windows, formWigdet))

# 事件绑定 -- 翻页处理
def AddClickedWaringPage(type, windows, formWigdet):
    try:
        if type == 'up':
            windows.current_WaringPage -= 1
        elif type == 'next':
            windows.current_WaringPage += 1
        # 分页处理
        data = get_page(windows.showWaringStockData, windows.current_WaringPage, 20)
        # 数据显示处理
        showTableData(data, windows, formWigdet)
        # 表格设定
        setingWaringStockTable(formWigdet.waring_showStockTable)
    except Exception as ex:
        logger.error(f'翻页处理出错了：{str(ex)}')

# 数据显示处理
def showTableData(data, windows, formWigdet):
    # ListView model 4Row 3 coloumn
    windows.waringStockModel = QStandardItemModel(0, 8)
    # 创建行标题
    windows.waringStockModel.setHorizontalHeaderLabels(
        [ '股票No', '名称', '个股日期', '所属行业','风险种类', '更新日期', '安全分', '预警类型', '预警详情'])
    # 设定项目值显示
    for row, item in enumerate(data['data']):
        windows.waringStockModel.appendRow([setQStandardItem(str(value), str(value)) for value in item])

    # 页码格式化
    formWigdet.plateWaringNo.setText(f' 第 {data["current_page"]} 页 ')
    if data["current_page"] == 1:
        # 第一页时，上一页按钮不显示【setVisible(True)】
        formWigdet.upWaringPage.setVisible(False)
        nextFlag = True
        if len(windows.showWaringStockData) <= 20:
            nextFlag = False
        formWigdet.nextWaringPage.setVisible(nextFlag)

    elif data["current_page"] == data["total_pages"]:
        # 最后一页时，下一页按钮不显示【setVisible(True)】
        formWigdet.upWaringPage.setVisible(True)
        formWigdet.nextWaringPage.setVisible(False)

    else:
        formWigdet.upWaringPage.setVisible(True)
        formWigdet.nextWaringPage.setVisible(True)

    # 自定义排序Model
    customSortmodel = CustomProxyModel()
    customSortmodel.setSourceModel(windows.waringStockModel)
    formWigdet.waring_showStockTable.setModel(customSortmodel)

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

# 风险个股Tab--检索按钮事件
def AddWaringClickedStockSubmit(windows, formWigdet):
    try:
        # 风险个股--数据绑定
        editWaringStockTable(windows, formWigdet)
    except Exception as ex:
        logger.error(f'检索处理出错了：{str(ex)}')

# 风险个股--数据绑定
def editWaringStockTable(windows, formWigdet):
    # 风险个股Tab--数据绑定
    getWaringStockData(windows, formWigdet)
    # 风险个股Tab--数据显示设定
    setingWaringStockTable(formWigdet.waring_showStockTable)

# 风险个股Tab--数据显示设定
def setingWaringStockTable(waringTable):
    # 统一样式表设置
    style_sheet = f"""
                    /* 表格主体样式 */
                    QTableView {{
                        border: 1px solid #d0d0d0;
                        gridline-color: #e0e0e0;
                        alternate-background-color: #f8f8f8;
                        selection-background-color: #2a82da;
                        selection-color: white;
                    }}

                    /* 表头样式 */
                    QHeaderView::section {{
                        background-color: #f0f0f0;
                        border: 1px solid #c0c0c0;
                        padding: 2px;
                        font-weight: bold;
                    }}

                    /* 单元格悬停效果 */
                    QTableView::item:hover {{
                        background-color: #ddeeff;
                    }}

                    /* 选中行样式 */
                    QTableView::item:selected {{
                        background-color: #2a82da;
                        color: white;
                    }}
                """
    waringTable.setStyleSheet(style_sheet)

    # 设置样式表添加边框
    waringTable.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)  # 禁止调整行高
    waringTable.verticalHeader().setDefaultSectionSize(28)  # 设置默认行高为30像素（可选）
    waringTable.horizontalHeader().setMinimumHeight(28)
    # waringTable.horizontalHeader().setSectionsClickable(True)  # 设置列头可点击（可选）
    # waringTable.verticalHeader().setSectionsClickable(True)  # 设置行头可点击（可选）
    # waringTable.horizontalHeader().setSectionsMovable(True)  # 设置列头可移动（可选）
    # waringTable.verticalHeader().setSectionsMovable(True)  # 设置行头可移动（可选）
    # waringTable.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置列头文本居中显示（可选）
    # waringTable.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置行头文本居中显示（可选）
    # 列设置保持可调整（默认状态）
    # waringTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    # 设置行交替
    # waringTable.setAlternatingRowColors(True)

    # 禁止编辑
    waringTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    # 设置列宽 1450
    waringTable.setColumnWidth(0, 70)
    waringTable.setColumnWidth(1, 80)
    waringTable.setColumnWidth(2, 88)
    waringTable.setColumnWidth(3, 85)
    waringTable.setColumnWidth(4, 72)
    waringTable.setColumnWidth(5, 114)
    waringTable.setColumnWidth(6, 68)
    waringTable.setColumnWidth(7, 110)
    # 统计行数
    rowCount = waringTable.model().rowCount()
    # 行数 小于 10
    if rowCount < 10:
        waringTable.setColumnWidth(8, 792)
    else:
        waringTable.setColumnWidth(8, 785)

    # 启用数据排序和过滤
    waringTable.setSortingEnabled(True)
    # 设置表格为整行选择 QAbstractItemView.SelectionBehavior(1) 单元格选中：QAbstractItemView.SelectionBehavior(0) 列选中：QAbstractItemView.SelectionBehavior(2)
    waringTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior(1))
    # 禁止列宽调整
    waringTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
    waringTable.horizontalHeader().setSectionsMovable(False)

    # 获取列宽 用来手动调节每列列宽
    # waringTable.horizontalHeader().sectionResized.connect(
    #     lambda index, old_size, new_size: print(f"列{index}宽度变为{new_size}"))

# 风险个股Tab--数据绑定
def getWaringStockData(windows, formWigdet):
    # 检索条件获取
    # 个股日期
    cDateFrom = DateTimeUtils.Format_changed(formWigdet.waringDateFrom.text(), '%Y年%M月%d日', '%Y%M%d')
    # 个股日期
    cDateTo = DateTimeUtils.Format_changed(formWigdet.waringDateTo.text(), '%Y年%M月%d日', '%Y%M%d')
    # 股票No
    waringStockNo = formWigdet.waring_stockNo.text()
    # 股票名称
    waringStockName = formWigdet.waring_stockName.text()
    # 所属行业
    waringHangYe = formWigdet.waring_suoShuHangYe.text()
    # 风险种类
    waringStockType = formWigdet.waring_stockType.currentIndex()

    # 排序选项
    orderByOption = ' ORDER BY NSIQ.STOCK_NO ASC '
    # 检索条件设定
    waringStockCondition = WaringStockCondition(cDateFrom, cDateTo, waringStockNo, waringStockName, waringHangYe,
                                                waringStockType, orderByOption)
    # 数据检索
    windows.showWaringStockData = WaringStockModel.getWaringStockWLWData(waringStockCondition)
    # 总件数format
    formWigdet.waring_count_number.setText(f'一共 {len(windows.showWaringStockData)} 件数据')

    # 页码初始化
    windows.current_WaringPage = 1
    # 分页处理
    data = get_page(windows.showWaringStockData, windows.current_WaringPage, 20)
    # 数据显示处理
    showTableData(data, windows, formWigdet)

# 事件绑定 -- 清除
def AddWaringClickedStockClear(windows, formWigdet):
    try:
        waringStockInitContent(windows, formWigdet)
    except Exception as ex:
        logger.error(f'清除处理出错了：{str(ex)}')