# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/3/8 17:05
# @Author : 连三保
# @Version: V 1.0
# @File : WaringStockAction.py
# @uptime: 2026/11/21 17:04
# @desc : 风险个股Tab数据处理

from functools import partial
from typing import Dict, Any

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *   # 从 PyQt6 中导入所需的类

from WLW.StockBase import DateTimeUtils
from WLW.Tools.CommonUtils import setQStandardItem
from WLW.Tools.LoggingEx import logger
from WLW.action.CustomVerticalHeader import CustomVerticalHeader
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
        # windows.waringStockModel.appendRow([setQStandardItem(str(value), str(value)) for value in item])
        row_items = []
        for value, key in enumerate(item):
            std_item = setQStandardItem(str(key), str(key))
            if value in (7, 8):
                # 字体加粗
                bold_font = QFont()
                bold_font.setBold(True)
                std_item.setFont(bold_font)
                # 红色 #d92121
                std_item.setForeground(QColor("#d92121"))
                # ========== 文字居左 ==========
                std_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            else:
                # ========== 文字居中 ==========
                std_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            row_items.append(std_item)
        windows.waringStockModel.appendRow(row_items)

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
    # ===================== 新增：连续行号 =======================================================
    page_no = data["current_page"]
    page_size = data["page_size"]
    offset = (page_no - 1) * page_size
    v_header = formWigdet.waring_showStockTable.verticalHeader()
    if hasattr(v_header, "setStartOffset"):
        logger.info(f"page_no: {page_no}, page_size: {page_size}, offset: {offset}")
        v_header.setStartOffset(offset)
    # ==========================================================================================

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
    if windows.showWaringStockData:
        # 风险个股Tab--数据显示设定
        setingWaringStockTable(formWigdet.waring_showStockTable)

# 风险个股Tab--数据显示设定
def setingWaringStockTable(waringTable):
    # 统一样式表设置
    style_sheet = """
            QTableView {
                border: none;
                alternate-background-color: #f4f6f9;
                selection-background-color: #1967c2;
                selection-color: white;
            }
            /* ========== 顶部水平表头（列标题，保留原有样式不变） ========== */
            QHeaderView::section:horizontal {
                background-color: #dce3ec;
                border: none;
                padding: 1px;
                font-weight: bold;
                color: #111111;
            }

            QHeaderView::section:horizontal:hover {
                background-color: #c8d2df;
            }

            QHeaderView::section:horizontal:selected {
                color: #dd2222;
            }
            /* ========== 垂直表头【行号列：清除全部样式】 ========== */
            QHeaderView::section:vertical {
                background-color: transparent;
                border: none;
                padding: 0px;
                font-weight: normal;
                color: #444444;
                min-width:45px;
            }

            QHeaderView::section:vertical:hover {
                background-color: transparent;
            }

            QTableView::item:hover {
                background-color: #d7e6f8;
            }

            QTableView::item:selected {
                background-color: #1967c2;
                color: white;
            }
            /* 左上角角落按钮，也跟着行号一起透明，统一观感 */
            QTableCornerButton::section {
                border: none;
                background-color: transparent;
            }
        """
    waringTable.setStyleSheet(style_sheet)

    # ========= 【重点修改这里】只初次替换一次垂直表头，不要重复新建 =====================================
    vh = waringTable.verticalHeader()
    if not isinstance(vh, CustomVerticalHeader):
        # 只有原生表头的时候，才替换一次
        new_vh = CustomVerticalHeader(waringTable)
        waringTable.setVerticalHeader(new_vh)
        # 绑定点击事件，只绑定一次
        from PyQt6.QtCore import QItemSelectionModel
        new_vh.sectionClicked.connect(lambda row: waringTable.selectionModel().select(
            waringTable.model().index(row, 0),
            QItemSelectionModel.SelectionFlag.Rows | QItemSelectionModel.SelectionFlag.ClearAndSelect
        ))
    # ==========================================================================================

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
    # 去掉网格线
    waringTable.setShowGrid(False)
    # 设置行交替
    waringTable.setAlternatingRowColors(True)

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
    waringTable.setColumnWidth(7, 215)
    waringTable.setColumnWidth(8, 665)

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
    count = 0
    enableFlag = False
    if windows.showWaringStockData:
        enableFlag = True
        count = len(windows.showWaringStockData)
        # 页码初始化
        windows.current_WaringPage = 1
        # 分页处理
        data = get_page(windows.showWaringStockData, windows.current_WaringPage, 20)
        # 数据显示处理
        showTableData(data, windows, formWigdet)
    else:
        # windows.waringStockModel.clear()  # 清除所有数据及表头
        # 分页按钮不显示
        formWigdet.upWaringPage.setVisible(False)
        formWigdet.nextWaringPage.setVisible(False)
        # 页码格式化
        formWigdet.plateWaringNo.setText('')
    # 总件数format
    formWigdet.waring_count_number.setText(f'共 {count} 条')
    # data 不显示
    formWigdet.waring_showStockTable.setVisible(enableFlag)

# 事件绑定 -- 清除
def AddWaringClickedStockClear(windows, formWigdet):
    try:
        waringStockInitContent(windows, formWigdet)
    except Exception as ex:
        logger.error(f'清除处理出错了：{str(ex)}')