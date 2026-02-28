# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/3/8 15:43
# @Author : 连三保
# @Version: V 1.0
# @File : StockInfoAction.py
# @desc :涨停板Tab数据处理
# 禁用metrics收集
import os
from functools import partial
from pathlib import Path
from typing import Dict, Any

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *   # 从 PyQt6 中导入所需的类

from WLW.StockBase import DateTimeUtils
from WLW.StockBase.DateTimeUtils import get_quarter_dates
from WLW.Tools.CommonUtils import setQStandardItem
from WLW.action import CapitalAction
from WLW.action.MultiDailySortProxyModel import CustomProxyModel
from WLW.action.RowMenuAction import create_menu
from WLW.model import StockInfoModel
from WLW.model.StockInfoCondition import StockInfoCondition
from WLW.Tools.LoggingEx import logger

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)

# 获取所在文件夹路径
dir_path = str(os.path.dirname(script_path))

dir_path = dir_path.replace('\\', '/')

# 画面初期设定
def stockInfoInitContent(windows, formWidget):
    # 游资有无
    windows.youZi = ''

    # 股票No、股票名称、连板数、换手率、涨停次数、所属行业、炸板次数、涨停主题、最新价输入框空白设定
    formWidget.stockNo.setText('')
    # formWidget.stockNo.setIntegerOnly()
    # 设置只能输入6位0-9的数字
    formWidget.stockNo.setNumberWithRange(6)
    formWidget.stockName.setText('')
    formWidget.lianBanShu.setText('')
    formWidget.huanShouLv.setText('')
    formWidget.zhangTingCiShu.setText('')
    formWidget.suoShuHangYe.setText('')
    formWidget.zhaBanCiShu.setText('')
    formWidget.le_ztzt.setText('')
    formWidget.le_zxj.setText('')

    # condition_comboBox 设定
    # 连板数检索条件设定
    formWidget.condition_lbs.clear()
    formWidget.condition_lbs.addItems(['=', '>', '<'])
    formWidget.condition_lbs.setCurrentIndex(0)
    formWidget.condition_lbs.setMinimumHeight(26)  # 设置最小高度为26px
    # 涨停次数检索条件设定
    formWidget.condition_ztcs.clear()
    formWidget.condition_ztcs.addItems(['=', '>', '<'])
    formWidget.condition_ztcs.setCurrentIndex(0)
    formWidget.condition_ztcs.setMinimumHeight(26)
    # 换手率检索条件设定
    formWidget.condition_hsl.clear()
    formWidget.condition_hsl.addItems(['=', '>', '<'])
    formWidget.condition_hsl.setCurrentIndex(0)
    formWidget.condition_hsl.setMinimumHeight(26)
    # 最新价检索条件设定
    formWidget.condition_zxj.clear()
    formWidget.condition_zxj.addItems(['=', '>', '<'])
    formWidget.condition_zxj.setCurrentIndex(0)
    formWidget.condition_zxj.setMinimumHeight(26)
    # 炸板次数检索条件设定
    formWidget.condtion_zbcs.clear()
    formWidget.condtion_zbcs.addItems(['=', '>', '<'])
    formWidget.condtion_zbcs.setCurrentIndex(0)
    formWidget.condtion_zbcs.setMinimumHeight(26)

    # 游资 combox设定
    formWidget.youzi_comboBox.clear()
    formWidget.youzi_comboBox.addItems(['全部', '有', '无'])
    formWidget.youzi_comboBox.setCurrentIndex(1)
    formWidget.youzi_comboBox.setMinimumHeight(26)

    # 风险种类 '全部'设定
    formWidget.stock_stockType.clear()
    formWidget.stock_stockType.addItems(['全部', '频发风险', '触发风险', '商誉风险', '近期解禁', '退市风险', '立案调查', '无风险'])
    formWidget.stock_stockType.setCurrentIndex(7)
    formWidget.stock_stockType.setMinimumHeight(26)

    # 当前周開始日取得
    weekFromDay = DateTimeUtils.Week_Day_Date(weekDay=1)
    # 当前周终了日取得
    # weekToDay = DateTimeUtils.Week_Day_Date(weekDay=5)

    # 交易日期From 显示格式
    formWidget.saleDateFrom.setDate(QDate(weekFromDay.year, weekFromDay.month, weekFromDay.day))
    # 交易日期From 可选最大日期
    formWidget.saleDateFrom.setMaximumDate(QDate.currentDate().addDays(0))
    # 交易日期From 可选最小日期
    # formWidget.saleDateFrom.setMinimumDate(QDate.currentDate().addDays(-30))
    # 交易日期From 日历控件弹出
    formWidget.saleDateFrom.setCalendarPopup(True)

    # 交易日期To 显示格式
    formWidget.saleDateTo.setDate(QDate.currentDate())
    # 交易日期To 可选最大日期
    formWidget.saleDateTo.setMaximumDate(QDate.currentDate().addDays(0))
    # 交易日期To 可选最小日期
    # formWidget.saleDateTo.setMinimumDate(QDate.currentDate().addDays(-30))
    # 交易日期To 日历控件弹出
    formWidget.saleDateTo.setCalendarPopup(True)

    # 上一页
    upIcon = QIcon()
    upIcon.addPixmap(QPixmap("_internal/image/upPage.svg"), QIcon.Mode.Normal, QIcon.State.Off)
    formWidget.upStockPage.setIcon(upIcon)
    # 下一页
    nextIcon = QIcon()
    nextIcon.addPixmap(QPixmap("_internal/image/nextPage.svg"), QIcon.Mode.Normal, QIcon.State.Off)
    formWidget.nextStockPage.setIcon(nextIcon)

    # 设置行右键菜单功能
    if formWidget.passKey == 'WLW':
        formWidget.showStockTable.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        formWidget.showStockTable.customContextMenuRequested.connect(
            lambda pos: show_menu(pos, windows, formWidget))

# 表格行右键菜单
def show_menu(pos, windows, formWigdet):
    try:
        index = formWigdet.showStockTable.indexAt(pos)
        # 获取当前行所有列的值
        model = formWigdet.showStockTable.model()
        # 持股机构数
        institutionCount = int(model.index(index.row(), 18).data())
        # 鼠标单击行焦点取得
        qPoint = formWigdet.showStockTable.viewport().mapToGlobal(pos)

        if index.isValid() and institutionCount > 0:
            # 以交易日期转换成机构持股报告日期
            reportDate = get_quarter_dates("%Y-%m-%d", model.index(index.row(), 0).data(), "%Y-%m-%d")["end_date"]
            # 获取行业名称
            hyname = model.index(index.row(), 1).data()
            # 获取股票代码
            stockNo = model.index(index.row(), 2).data()
            # 获取股票名称
            stockName = model.index(index.row(), 3).data()
            # 获取涨停主题
            zhangtingTitle = model.index(index.row(), 16).data()
            # 数据采集日期
            holdingDate = model.index(index.row(), 19).data()
            # 调用机构持股详细画面
            create_menu(reportDate, stockNo, stockName, holdingDate, '', zhangtingTitle, index, qPoint, windows)
    except Exception as ex:
        logger.error(f'右击菜单处理出错了：{str(ex)}')

# 事件绑定 注意参数传递:在这里functools.partial(方法名, 参数1, 参数2) 在主程序里就是方法名
def stockInfoActionSetting(windows, formWidget):
    # 事件绑定 -- 检索
    formWidget.stockSubmit.clicked.connect(partial(AddClickedStockSubmit, windows, formWidget))
    # 事件绑定 -- 清除
    formWidget.stockClear.clicked.connect(partial(AddClickedStockClear, windows, formWidget))
    # 事件绑定 -- 预览
    formWidget.stockDialog.clicked.connect(partial(addClickedStockPreview, windows, formWidget))
    # 事件绑定 -- 上一页
    formWidget.upStockPage.clicked.connect(partial(AddClickedStockPage, 'up', windows, formWidget))
    # 事件绑定 -- 下一页
    formWidget.nextStockPage.clicked.connect(partial(AddClickedStockPage, 'next', windows, formWidget))

# 事件绑定 -- 翻页处理
def AddClickedStockPage(type, windows, formWigdet):
    try:
        if type == 'up':
            windows.current_StockPage -= 1
        elif type == 'next':
            windows.current_StockPage += 1
        # 分页处理
        data = get_page(windows.showStockData, windows.current_StockPage, 20)
        # 数据显示处理
        showTableData(data, windows, formWigdet)
        # 表格设定
        setingStockTable(formWigdet.showStockTable)
    except Exception as ex:
        logger.error(f'翻页处理出错了：{str(ex)}')

# 数据显示处理
def showTableData(data, windows, formWigdet):
    # ListView model 4Row 3 coloumn
    windows.stockModel = QStandardItemModel(0, 19)
    # 创建行标题
    windows.stockModel.setHorizontalHeaderLabels(
        ['交易日期', '所属行业', '股票No', '名称', '涨跌幅(%)', '最新价(元)', '连板数', '炸板次数', '风险种类', '游资',
         '成交额(亿)',
         '换手率(%)', 'F封板时间', 'L封板时间', '封板资金', '涨停统计', '涨停主题', '涨停原因', '机构持股数量', 'hidden'])
    # 设定项目值显示
    showHeaderLables = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
    if data['data']:
        for row, item in enumerate(data['data']):
            windows.stockModel.appendRow([setQStandardItem(str(item[value]), str(item[value])) for value in showHeaderLables])
    # 页码格式化
    formWigdet.plateStockNo.setText(f' 第 {data["current_page"]} 页 ')
    if data["current_page"] == 1:
        # 第一页时，上一页按钮不显示【setVisible(True)】
        formWigdet.upStockPage.setVisible(False)
        nextFlag = True
        if len(windows.showStockData) <= 20:
            nextFlag = False
        formWigdet.nextStockPage.setVisible(nextFlag)

    elif data["current_page"] == data["total_pages"]:
        # 最后一页时，下一页按钮不显示【setVisible(True)】
        formWigdet.upStockPage.setVisible(True)
        formWigdet.nextStockPage.setVisible(False)

    else:
        formWigdet.upStockPage.setVisible(True)
        formWigdet.nextStockPage.setVisible(True)

    # 自定义排序Model
    customSortModel = CustomProxyModel()
    customSortModel.setSourceModel(windows.stockModel)
    formWigdet.showStockTable.setModel(customSortModel)

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

# 事件绑定 -- 清除按钮事件
def AddClickedStockClear(windows, formWidget):
    try:
        stockInfoInitContent(windows, formWidget)
    except Exception as ex:
        logger.error(f'清除处理出错了：{str(ex)}')

# 事件绑定 -- 分类显示
def addClickedStockPreview(windows, formWidget):
    try:
        CapitalAction.create_page(windows, formWidget)
    except Exception as ex:
        logger.error(f'addClickedStockDialog:{str(ex)}')

# 删除 PDF/chart/Png 文件
def deleteFile():
    # 确认存放PDF文件的目录是否存在
    pdf_file = f'{dir_path}/PDF'
    if os.path.exists(pdf_file):
        remove_files_with_progress(pdf_file)

    # 确认存放chart文件的目录是否存在
    pdf_file = f'{dir_path}/chart'
    if os.path.exists(pdf_file):
        remove_files_with_progress(pdf_file, ['echarts.min.js', 'PlateFund_NoData.html'])

    # 确认存放PNG文件的目录是否存在
    pdf_file = f'{dir_path}/PNG'
    if os.path.exists(pdf_file):
        remove_files_with_progress(pdf_file)

# 带进度显示 的文件删除
def remove_files_with_progress(folder_path, exce: list = []):
    folder = Path(folder_path)

    # 删除所有文件（保留空目录）
    for file_path in folder.glob("*"):
        # 跳过非必要删除的文件
        if file_path.name in exce:
            continue
        if file_path.is_file():
            file_path.unlink()
            logger.info(f'{file_path.name} 已删除！')

# 事件绑定 -- 检索
def AddClickedStockSubmit(windows, formWidget):
    # 数据绑定
    editStockTable(windows, formWidget)

# 数据绑定
def editStockTable(windows, formWidget):
    # 涨停板Tab--数据绑定
    getStockData(windows, formWidget)
    # 涨停板Tab--数据显示设定
    setingStockTable(formWidget.showStockTable)

# 涨停板Tab--数据绑定
def getStockData(windows, formWidget):
    # 检索条件获取
    # 交易日期From
    saleDayFrom = DateTimeUtils.Format_changed(formWidget.saleDateFrom.text(), '%Y年%M月%d日', '%Y%M%d')
    # 交易日期To
    saleDayTo = DateTimeUtils.Format_changed(formWidget.saleDateTo.text(), '%Y年%M月%d日', '%Y%M%d')
    # 股票No
    stockNo = formWidget.stockNo.text()
    # 股票名称
    stockName = formWidget.stockName.text()
    # 连板数
    lianBanShu = formWidget.lianBanShu.text()
    # 换手率
    huanShouLv = formWidget.huanShouLv.text()
    # 涨停次数
    zhangTingCiShu = formWidget.zhangTingCiShu.text()
    # 游资有无
    youZiYouWu = formWidget.youzi_comboBox.currentIndex()
    # 所属行业
    suoShuHangYe = formWidget.suoShuHangYe.text()
    # 炸板次数
    zhaBanCiShu = formWidget.zhaBanCiShu.text()
    # 风险种类
    stockType = formWidget.stock_stockType.currentIndex()
    # 涨停主题值
    le_ztzt = formWidget.le_ztzt.text()
    # 最新价和比较条件
    le_zxj = formWidget.le_zxj.text()
    condition_zxj = formWidget.condition_zxj.currentIndex()
    # 连板数比较条件
    condition_lbs = formWidget.condition_lbs.currentIndex()
    # 换手率比较条件
    condition_hsl = formWidget.condition_hsl.currentIndex()
    # 涨停次数比较条件
    condition_ztcs = formWidget.condition_ztcs.currentIndex()
    # 炸板次数
    condtion_zbcs = formWidget.condtion_zbcs.currentIndex()

    # 排序选项
    orderByOption = 'ORDER BY SIW.STOCK_DATE DESC'
    # 检索条件设定
    stockInfoCondition = StockInfoCondition(saleDayFrom, saleDayTo, stockNo, stockName, lianBanShu, huanShouLv,
                                            zhangTingCiShu,
                                            youZiYouWu, suoShuHangYe, zhaBanCiShu, stockType, le_ztzt, le_zxj, condition_zxj,
                                            condition_lbs, condition_hsl, condition_ztcs, condtion_zbcs, 'D', orderByOption)

    # 数据检索;
    windows.showStockData = StockInfoModel.getStockInfoWLWData(stockInfoCondition)
    enableFlag = False

    # 设定项目值显示
    if windows.showStockData:
        enableFlag = True
    # 总件数format
    formWidget.count_number.setText(f'一共 {len(windows.showStockData)} 件数据')
    formWidget.stockDialog.setEnabled(enableFlag)

    # 页码初始化
    windows.current_StockPage = 1
    # 分页处理
    data = get_page(windows.showStockData, windows.current_StockPage, 20)
    # 数据显示处理
    showTableData(data, windows, formWidget)

# 涨停板Tab--数据显示设定
def setingStockTable(tableView):
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
                        padding: 1px;
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
    tableView.setStyleSheet(style_sheet)

    # 设置样式表添加边框
    tableView.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)  # 禁止调整行高
    tableView.verticalHeader().setDefaultSectionSize(28)  # 设置默认行高为30像素（可选）
    tableView.horizontalHeader().setMinimumHeight(28)
    # tableView.horizontalHeader().setSectionsClickable(True)  # 设置列头可点击（可选）
    # tableView.verticalHeader().setSectionsClickable(True)  # 设置行头可点击（可选）
    # tableView.horizontalHeader().setSectionsMovable(True)  # 设置列头可移动（可选）
    # tableView.verticalHeader().setSectionsMovable(True)  # 设置行头可移动（可选）
    # tableView.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置列头文本居中显示（可选）
    # tableView.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置行头文本居中显示（可选）
    # 列设置保持可调整（默认状态）
    # tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    # 设置行交替
    # tableView.setAlternatingRowColors(True)

    # 禁止编辑
    tableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    # 设置列宽 1461
    tableView.setColumnWidth(0, 88)
    tableView.setColumnWidth(1, 70)
    tableView.setColumnWidth(2, 65)
    tableView.setColumnWidth(3, 70)
    tableView.setColumnWidth(4, 70)
    tableView.setColumnWidth(5, 72)
    tableView.setColumnWidth(6, 52)
    tableView.setColumnWidth(7, 60)
    tableView.setColumnWidth(8, 68)
    tableView.setColumnWidth(9, 50)
    tableView.setColumnWidth(10, 70)
    tableView.setColumnWidth(11, 72)
    tableView.setColumnWidth(12, 68)
    tableView.setColumnWidth(13, 68)
    tableView.setColumnWidth(14, 90)
    tableView.setColumnWidth(15, 60)
    tableView.setColumnWidth(16, 90)
    tableView.setColumnWidth(17, 206)
    # 统计行数
    rowCount = tableView.model().rowCount()
    # 行数 小于 10
    if rowCount < 10:
        tableView.setColumnWidth(18, 92)
    else:
        tableView.setColumnWidth(18, 85)

    # 第20列隐藏 机构数据采集日期
    tableView.setColumnHidden(19, True)

    # 启用数据排序和过滤
    tableView.setSortingEnabled(True)
    # 设置表格为整行选择
    tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    # 禁止列宽调整
    tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
    tableView.horizontalHeader().setSectionsMovable(False)

    # 获取列宽 用来手动调节每列列宽
    # tableView.horizontalHeader().sectionResized.connect(
    #     lambda index, old_size, new_size: print(f"列{index}宽度变为{new_size}"))