# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/3/8 17:02
# @Author : 连三保
# @Version: V 1.0
# @File : MainCapitalAction.py
# @desc : 资金流向Tab数据处理
# 禁用metrics收集
import datetime
import os
from functools import partial
from typing import Dict, Any

import pandas
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *   # 从 PyQt6 中导入所需的类
from pyecharts.charts import Pie, Bar, Line
from pyecharts import options as opts
from pyecharts.globals import CurrentConfig

from WLW.StockBase import DateTimeUtils
from WLW.Tools.CommonUtils import setQStandardItem
from WLW.WebView.QWebViewEx import FunctionMW
from WLW.action.MultiMainSortProxyModel import CustomProxyModel
from WLW.action.WebEngineViewEx import WebEngineView
from WLW.model import MainCapitalModel
from WLW.model.MainCapitalCondition import MainCapitalCondition
from WLW.ComplexLayoutPDF import ComplexLayoutPDF
from WLW.Ui_mainCapitalDialog import Ui_mainCapitalDialog
from WLW.Tools.LoggingEx import logger

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)

# 获取所在文件夹路径
dir_path = str(os.path.dirname(script_path))

dir_path = dir_path.replace('\\', '/')

# 主流资金Tab(初期化)
def mainCapitalInitContent(windows, formWigdet):
    # 股票No、股票名称、涨幅、现价、所属行业输入框空白设定
    formWigdet.master_stockNo_v.setText('')
    formWigdet.master_stockName_v.setText('')
    formWigdet.master_hangYe_v.setText('')
    formWigdet.master_zhangFu_v.setText('')
    formWigdet.master_xianJia_v.setText('')

    # condition_comboBox 设定
    # 现价检索条件设定
    formWigdet.condition_xj.clear()
    formWigdet.condition_xj.addItems(['=', '>', '<'])
    formWigdet.condition_xj.setCurrentIndex(0)
    formWigdet.condition_xj.setMinimumHeight(26)

    # 风险种类 '全部'设定
    formWigdet.master_stockType.clear()
    formWigdet.master_stockType.addItems(['全部', '频发风险', '触发风险', '商誉风险', '近期解禁', '退市风险', '立案调查', '无风险'])
    formWigdet.master_stockType.setCurrentIndex(7)
    formWigdet.master_stockType.setMinimumHeight(26)

    # 当前周開始日取得
    weekFromDay = DateTimeUtils.Week_Day_Date(weekDay=1)

    # 交易日期From 显示格式
    formWigdet.hangQingDate_From.setDate(QDate(weekFromDay.year, weekFromDay.month, 1))
    # 交易日期From 可选最大日期
    formWigdet.hangQingDate_From.setMaximumDate(QDate.currentDate().addDays(0))
    # 交易日期From 可选最小日期
    # formWigdet.saleDateFrom.setMinimumDate(QDate.currentDate().addDays(-30))
    # 交易日期From 日历控件弹出
    formWigdet.hangQingDate_From.setCalendarPopup(True)

    # 交易日期To 显示格式
    formWigdet.hangQingDate_To.setDate(QDate.currentDate())
    # 交易日期To 可选最大日期
    formWigdet.hangQingDate_To.setMaximumDate(QDate.currentDate().addDays(0))
    # 交易日期To 可选最小日期
    # formWigdet.hangQingDate_To.setMinimumDate(QDate.currentDate().addDays(-30))
    # 交易日期To 日历控件弹出
    formWigdet.hangQingDate_To.setCalendarPopup(True)

    # 上一页
    upIcon = QIcon()
    upIcon.addPixmap(QPixmap("_internal/image/upPage.svg"), QIcon.Mode.Normal, QIcon.State.Off)
    formWigdet.upMasterPage.setIcon(upIcon)
    # 下一页
    nextIcon = QIcon()
    nextIcon.addPixmap(QPixmap("_internal/image/nextPage.svg"), QIcon.Mode.Normal, QIcon.State.Off)
    formWigdet.nextMasterPage.setIcon(nextIcon)

# 主力资金Tab(事件绑定)
def mainCapitalActionSetting(windows, formWigdet):
    # 事件绑定 -- 分类显示
    formWigdet.showMainCapitalDialog.clicked.connect(partial(AddClickedShowMainCapitalDialog, windows, formWigdet))
    # 事件绑定 -- 检索
    formWigdet.master_stockSubmit.clicked.connect(partial(AddClickedMasterStockSubmit, windows, formWigdet))
    # 事件绑定 -- 清除
    formWigdet.master_stockClear.clicked.connect(partial(AddClickedMasterClear, windows, formWigdet))
    # 事件绑定 -- 上一页
    formWigdet.upMasterPage.clicked.connect(partial(AddClickedMasterPage, 'up', windows, formWigdet))
    # 事件绑定 -- 下一页
    formWigdet.nextMasterPage.clicked.connect(partial(AddClickedMasterPage, 'next', windows, formWigdet))

# 事件绑定 -- 翻页处理
def AddClickedMasterPage(type, windows, formWigdet):
    if type == 'up':
        windows.current_MainPage -= 1
    elif type == 'next':
        windows.current_MainPage += 1
    # 分页处理
    data = get_page(windows.showMainCapitalData, windows.current_MainPage, 20)
    # 数据显示处理
    showTableData(data, windows, formWigdet)
    # 表格设定
    setingMainCapitalTable(formWigdet.master_showStockTable)

# 数据显示处理
def showTableData(data, windows, formWigdet):
    # ListView model 4Row 3 coloumn
    windows.mainCapitalModel = QStandardItemModel(0, 16)
    # 创建行标题
    windows.mainCapitalModel.setHorizontalHeaderLabels(
        ['交易日期', '所属行业', '股票No', '名称', '涨幅(%)', '现价(元)', '风险种类', '主力净额(亿)', '主力净占比(%)',
         '超大单净额(亿)', '超大单净占比(%)', '大单净额(亿)', '大单净占比(%)',
         '中单净额(亿)', '中单净占比(%)', '小单净额(亿)', '小单净占比(%)'])
    # 设定项目值显示
    showHeaderLables = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    if data['data']:
        for row, item in enumerate(data['data']):
            windows.mainCapitalModel.appendRow([setQStandardItem(str(item[value]), str(item[value])) for value in showHeaderLables])
    # 页码格式化
    formWigdet.plateMasterNo.setText(f' 第 {data["current_page"]} 页 ')
    if data["current_page"] == 1:
        # 第一页时，上一页按钮不显示【setVisible(True)】
        formWigdet.upMasterPage.setVisible(False)
        nextFlag = True
        if len(windows.showMainCapitalData) <= 20:
            nextFlag = False
        formWigdet.nextMasterPage.setVisible(nextFlag)

    elif data["current_page"] == data["total_pages"]:
        # 最后一页时，下一页按钮不显示【setVisible(True)】
        formWigdet.upMasterPage.setVisible(True)
        formWigdet.nextMasterPage.setVisible(False)

    else:
        formWigdet.upMasterPage.setVisible(True)
        formWigdet.nextMasterPage.setVisible(True)

    # 自定义排序Model
    customSortmodel = CustomProxyModel()
    customSortmodel.setSourceModel(windows.mainCapitalModel)
    formWigdet.master_showStockTable.setModel(customSortmodel)

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

# 事件绑定 -- 分类显示
def AddClickedShowMainCapitalDialog(windows, formWigdet):
    try:
        windows.third = QMainWindow()
        windows.mainCapitalDialog = Ui_mainCapitalDialog()
        windows.mainCapitalDialog.setupUi(windows.third)
        # 所有行业饼图地址
        windows.pieOfsshyPath = ''
        # 单一行业条形图地址
        windows.barOfSingleSshyPaths = {}
        # 图形显示格式设定不显示
        windows.mainCapitalDialog.showType.setEnabled(False)
        windows.mainCapitalDialog.printDialog.setEnabled(False)
        windows.mainCapitalDialog.showType.addItems(['表格', '折线图', '资金流向', '数据中心', 'F10资料', '可视化报告'])
        windows.mainCapitalDialog.showType.setCurrentIndex(0)
        windows.mainCapitalDialog.showType.currentTextChanged.connect(partial(calculate_values, windows, formWigdet))
        # 分类显示画面初期化
        initShowMainCapitalDialog(windows, formWigdet)
        # 分类显示画面事件绑定
        actionShowMainCapitalSetting(windows, formWigdet)

        # 新增关闭事件处理
        def handle_close_event():
            windows.third.hide()  # 隐藏当前窗口
            windows._LWLW__mainWindow.show()  # 恢复主窗口显示

        # 绑定三种关闭方式
        windows.third.closeEvent = lambda e: handle_close_event()  # 点击关闭按钮

        windows.third.setWindowModality(Qt.WindowModality.ApplicationModal)  # 阻塞所有窗口操作
        windows.third.show()
        windows._LWLW__mainWindow.hide() # 隐藏主窗口显示
    except Exception as ex:
        logger.error('AddClickedShowMainCapitalDialog:' + str(ex))

# 图形显示格式切换事件
def calculate_values(windows, formWigdet):
    onSelectionChanged(windows, formWigdet)

# 分类显示画面事件绑定
def actionShowMainCapitalSetting(windows, formWigdet):
    # TreeView行选择事件
    windows.mainCapitalDialog.mainCapitalTree.selectionModel().selectionChanged.connect(partial(onSelectionChanged, windows, formWigdet))
    # 所属行业数据
    windows.mainCapitalDialog.allSshyCharts.clicked.connect(partial(clickedCapitalPreview, windows, formWigdet))
    # 预览
    windows.mainCapitalDialog.printPreview.clicked.connect(partial(clickedPrintPreview, windows, formWigdet))
    # 打印
    windows.mainCapitalDialog.printDialog.clicked.connect(partial(handlerPrint, windows, formWigdet))
    # PDF出力
    # windows.mainCapitalDialog.printOut.clicked.connect(partial(clickedStockPDF, windows, formWidget, 'Preview'))

# 打印
def handlerPrint(windows, formWidget):
    windows.webBrowser = FunctionMW(windows.browserPrinterDialogUrl, windows.third)
    windows.webBrowser.handlePrintRequest()  # 直接调用打印方法

# 预览
def clickedPrintPreview(windows, formWidget):
    windows.browserPrinterDialogUrl = ''
    clickedStockPDF(windows, formWidget, 'Preview')
    if windows.browserPrinterDialogUrl != '':
        windows.mainCapitalDialog.printDialog.setEnabled(True)
        windows.webBrowser = FunctionMW(windows.browserPrinterDialogUrl, windows.third)
        windows.webBrowser.closed.connect(lambda: windows.third.show())  # 连接关闭信号到显示原窗口
        windows.webBrowser.show()
        windows.third.hide()

# PDF出力
def clickedStockPDF(windows, formWigdet, opreationType):
    try:
        # PDF数据
        pdfData = {}

        # 确认存放PDF文件的目录是否存在
        windows.third.pdf_dir = f'{dir_path}/PDF'
        if not os.path.exists(windows.third.pdf_dir):
            os.makedirs(windows.third.pdf_dir)
        logger.info(f'存放PDF文件的目录: [{windows.third.pdf_dir}]存在！！！')

        # 全行业数据取得
        if windows.ChartSuoShuHangYe == 'all':
            pdfPageTitle = "多行业数据"
            pdfFileName = f"{windows.third.pdf_dir}/MC_{pdfPageTitle}_{DateTimeUtils.nowDateTime().strftime('%Y%m%d')}.pdf"
            for indexNo in windows.pandasSortData.index:
                # 所属行业名称取得
                sshy = windows.pandasSortData.loc[indexNo, '所属行业']
                # PDF数据编辑
                pdfData.update(editPdfData(windows, formWigdet, sshy))
        else:
            pdfFileName = f"{windows.third.pdf_dir}/MC_{windows.ChartSuoShuHangYe}_{DateTimeUtils.nowDateTime().strftime('%Y%m%d')}.pdf"
            pdfPageTitle = f"{windows.ChartSuoShuHangYe}行业数据"
            # PDF数据编辑
            pdfData.update(editPdfData(windows, formWigdet, windows.ChartSuoShuHangYe))

        logger.info(f'表格数据: {pdfData}')
        pdf_builder = ComplexLayoutPDF(windows.pdfPngFile, '主力资金情报', pdfPageTitle, pdfFileName, '', pdfData)
        pdf_builder.build_document()
        # 预览
        if opreationType == 'Preview':
            windows.browserPrinterDialogUrl = pdfFileName
    except Exception as Ex:
        logger.error(f'Error: {Ex}')

# PDF数据编辑
def editPdfData(windows, formWigdet, sshy):
    # 表格header
    tableHeader = ['交易日期', '股票No', '股票名称', '涨幅(%)', '现价(元)', '风险种类', '主力净额(亿)', '主力净占比(%)']

    # 设定项目值显示
    showHeaderLables = [0, 2, 3, 4, 5, 6, 7, 8]
    # PDF数据
    pdfData = {}

    # 表格数据
    table_data = [tableHeader]
    conditionData = windows.pandasSortData[windows.pandasSortData['所属行业'] == sshy].DATA.to_frame()
    suoShuHangYeInfoPandas = pandas.DataFrame(conditionData.values.T[0][0],
                                              columns=conditionData.values.T[0][0].columns)
    # 涨幅(%)降序 降序 SQL中已经降序了，这里无需排列
    # sortStockNos = suoShuHangYeInfoPandas.sort_values(by=['涨幅(%)'], ascending=False)

    # 行
    for nomber in suoShuHangYeInfoPandas.index:
        # 列
        table_row = [str(suoShuHangYeInfoPandas.iloc[nomber, value]) for value in showHeaderLables]
        # 2025年06月16日 转 2025/06/16
        table_row[0] = datetime.datetime.strptime(table_row[0], '%Y-%m-%d').strftime('%Y/%m/%d')
        table_data.append(table_row)

    pdfData[f'{sshy}一共有 {len(table_data) - 1}件'] = table_data

    return pdfData

# 所属行业数据
def clickedCapitalPreview(windows, formWigdet):
    windows.mainCapitalDialog.printDialog.setEnabled(False)
    windows.mainCapitalDialog.printPreview.setEnabled(True)
    # 图形显示格式设定: False不显示
    windows.mainCapitalDialog.showType.setEnabled(False)
    windows.ChartSuoShuHangYe = 'all'
    windows.mainCapitalDialog.verticalLayout.removeWidget(windows.mainCapitalBrowser)
    windows.mainCapitalBrowser.deleteLater()  # 安全删除对象
    windows.mainCapitalBrowser = None  # 清除引用
    if windows.pieOfsshyPath == '':
        # QFrame设定
        initFrame(windows, formWigdet)
    else:
        windows.mainCapitalDialog.nav_option.setText(f'行业名称：{windows.mainCapitalDialog.allSshyCharts.text()}')
        pageTwo(windows, formWigdet, windows.pieOfsshyPath)

# PageTwo显示设定
def pageTwo(windows, formWigdet, path):
    # 创建web引擎视图
    windows.mainCapitalBrowser = WebEngineView()
    windows.mainCapitalBrowser.load(QUrl(f"file:///{path}"))
    windows.mainCapitalBrowser.loadFinished.connect(partial(on_load_finished, windows, formWigdet))
    windows.mainCapitalDialog.verticalLayout.addWidget(windows.mainCapitalBrowser)
    windows.mainCapitalDialog.verticalLayoutWidget.show()
    windows.mainCapitalDialog.verticalStackedWidget.setCurrentIndex(1)

def on_load_finished(windows, formWidget):
    # QTimer.singleShot(1000, lambda :
    #                   windows.mainCapitalBrowser.grab().save(windows.pdfPngFile, "PNG"))
    QTimer.singleShot(1000, partial(save_high_res, windows))

def save_high_res(windows):
    windows.mainCapitalBrowser.page().runJavaScript("document.body.scrollHeight;",
        lambda height: windows.mainCapitalBrowser.grab().scaled(
            windows.mainCapitalBrowser.size() * 2,  # 2倍缩放
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ).save(windows.pdfPngFile, "PNG", 100)  # 100%质量
    )

# TreeView行选择事件
def onSelectionChanged(windows, formWigdet):
    windows.mainCapitalDialog.printDialog.setEnabled(False)
    indexes = windows.mainCapitalDialog.mainCapitalTree.selectionModel().selectedIndexes()  # 获取当前选中的索引列表

    if indexes:
        index = indexes[len(indexes) - 1]  # 只处理第一个索引，通常是顶层索引
        stockNo = windows.mainCapitalDialog.mainCapitalTree.model().itemFromIndex(index).text()
        windows.ChartSuoShuHangYe = windows.mainCapitalDialog.mainCapitalTree.model().itemFromIndex(
            indexes[0]).text()
        if stockNo == '':
            windows.mainCapitalDialog.nav_option.setText(f'行业名称：{windows.ChartSuoShuHangYe}')
            isShowType = False
            windows.mainCapitalDialog.verticalLayout.removeWidget(windows.mainCapitalBrowser)
            windows.mainCapitalBrowser.deleteLater()  # 安全删除对象
            windows.mainCapitalBrowser = None  # 清除引用
            barOfSingleSshyPaths = dict(windows.barOfSingleSshyPaths)
            if windows.ChartSuoShuHangYe in barOfSingleSshyPaths.keys():
                pageTwo(windows, formWigdet, windows.barOfSingleSshyPaths[windows.ChartSuoShuHangYe])
            else:
                initFrame(windows, formWigdet, 'bar')
        else:
            windows.mainCapitalDialog.nav_option.setText(f'股票名称：{windows.ChartSuoShuHangYe} No：{stockNo} ')
            isShowType = True
            # 由股票No或者所属行业查询股票历史轨迹
            index = indexes[len(indexes) - 2]
            suoShuHangYe = windows.mainCapitalDialog.mainCapitalTree.model().itemFromIndex(index).text()
            # 获取当前选择的显示类型
            display_type = windows.mainCapitalDialog.showType.currentText()
            if display_type == "表格":
                historyFromStock(windows, formWigdet, stockNo, suoShuHangYe)
                setingDialogMainCapitalTable(windows.mainCapitalDialog.tableView)
            elif display_type == "折线图":
                historyFromStockLine(windows, formWigdet, stockNo, suoShuHangYe)
            elif display_type == "数据中心":
                # 数据URL显示
                index = indexes[len(indexes) - 5]
                stockDepthDataUrls = windows.mainCapitalDialog.mainCapitalTree.model().itemFromIndex(index).text()
                showWebDataUrl(windows, stockDepthDataUrls)
            elif display_type == "F10资料":
                # F10数据URL显示
                index = indexes[len(indexes) - 4]
                stockF10Urls = windows.mainCapitalDialog.mainCapitalTree.model().itemFromIndex(index).text()
                showWebDataUrl(windows, stockF10Urls)
            elif display_type == "可视化报告":
                # 可视化报告数据URL显示
                index = indexes[len(indexes) - 3]
                stockReportchartUrls = windows.mainCapitalDialog.mainCapitalTree.model().itemFromIndex(index).text()
                showWebDataUrl(windows, stockReportchartUrls)
            elif display_type == "资金流向":
                # 资金流向数据URL显示
                stockReportchartUrls = f'https://data.eastmoney.com/zjlx/{stockNo}.html'
                showWebDataUrl(windows, stockReportchartUrls)

        # 图形显示格式设定: False不显示
        windows.mainCapitalDialog.showType.setEnabled(isShowType)
        windows.mainCapitalDialog.printPreview.setEnabled(not isShowType)

# （数据、F10、可视化报告）URL
def showWebDataUrl(windows, dataUrl):
    windows.mainCapitalDialog.verticalLayout.removeWidget(windows.mainCapitalBrowser)
    windows.mainCapitalBrowser.deleteLater()  # 安全删除对象
    windows.mainCapitalBrowser = None  # 清除引用
    # 创建web引擎视图
    windows.mainCapitalBrowser = WebEngineView()
    windows.mainCapitalBrowser.load(QUrl(dataUrl))
    windows.mainCapitalDialog.verticalLayout.addWidget(windows.mainCapitalBrowser)
    windows.mainCapitalDialog.verticalLayoutWidget.show()
    windows.mainCapitalDialog.verticalStackedWidget.setCurrentIndex(1)

# 主力资金分类显示--数据显示设定
def setingDialogMainCapitalTable(tableView):
    # 设置行选择颜色 (新增部分)
    selection_color = "#2a82da"  # 选择时的蓝色背景
    hover_color = "#ddeeff"  # 鼠标悬停时的浅蓝色
    text_color = "#ffffff"  # 选择时的白色文字

    tableView.setStyleSheet(f"""
                    QTableView::item:selected {{
                        background-color: {selection_color};
                        color: {text_color};
                    }}
                    QTableView::item:hover {{
                        background-color: {hover_color};
                    }}
                """)

    # 设置样式表添加边框
    tableView.horizontalHeader().setStyleSheet(
        "QHeaderView::section { border: 1px solid black; }")
    tableView.verticalHeader().setDefaultSectionSize(30)  # 设置默认行高为30像素（可选）
    tableView.horizontalHeader().setSectionsClickable(True)  # 设置列头可点击（可选）
    tableView.verticalHeader().setSectionsClickable(True)  # 设置行头可点击（可选）
    tableView.horizontalHeader().setSectionsMovable(True)  # 设置列头可移动（可选）
    tableView.verticalHeader().setSectionsMovable(True)  # 设置行头可移动（可选）
    tableView.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置列头文本居中显示（可选）
    tableView.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置行头文本居中显示（可选）
    # 设置行交替
    tableView.setAlternatingRowColors(True)

    # 禁止编辑
    tableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    # 设置列宽
    tableView.setColumnWidth(0, 105)
    tableView.setColumnWidth(1, 80)
    tableView.setColumnWidth(2, 80)
    tableView.setColumnWidth(3, 80)
    tableView.setColumnWidth(4, 80)
    tableView.setColumnWidth(5, 90)
    tableView.setColumnWidth(6, 90)
    tableView.setColumnWidth(7, 90)
    tableView.setColumnWidth(8, 90)
    tableView.setColumnWidth(9, 90)
    tableView.setColumnWidth(10, 90)

    # 启用数据排序和过滤
    tableView.setSortingEnabled(True)
    # 设置表格为整行选择 QAbstractItemView.SelectionBehavior(1) 单元格选中：QAbstractItemView.SelectionBehavior(0) 列选中：QAbstractItemView.SelectionBehavior(2)
    tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior(1))

# 由股票No或者所属行业查询股票历史轨迹
def historyFromStock(windows, formWigdet, stockNo:str='', suoShuHangYe:str=''):
    # ListView model 4Row 3 coloumn
    windows.historyMainCapitalModel = QStandardItemModel(0, 11)
    # 创建行标题
    windows.historyMainCapitalModel.setHorizontalHeaderLabels(
        ['交易日期', '涨幅(%)', '现价(元)', '风险种类', '主力净额(亿)', '主力净占比(%)', '超大单净额(亿)', '超大单净占比(%)', '大单净额(亿)', '大单净占比(%)',
             '中单净额(亿)', '中单净占比(%)'])

    # 设定项目值显示
    showHeaderLables = [0, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

    # 添加数据;
    # pandas.DataFrame 条件检索
    # 组合条件：&(和) | (或)
    conditionData = windows.pandasSortData[windows.pandasSortData['所属行业'] == suoShuHangYe].DATA.to_frame()
    suoShuHangYeInfoPandas = pandas.DataFrame(conditionData.values.T[0][0],
                                              columns=conditionData.values.T[0][0].columns)
    logger.info(suoShuHangYeInfoPandas)
    sortStockNos = suoShuHangYeInfoPandas.groupby(by='股票No')

    if sortStockNos:
        stockNo = stockNo.strip("'")
        for nomber, groupCols in sortStockNos:
             if nomber == stockNo:
                for index in range(0, len(groupCols.values)):
                    windows.historyMainCapitalModel.appendRow([QStandardItem(str(groupCols.values[index][value])) for value in showHeaderLables])
                break

    windows.mainCapitalDialog.tableView.setModel(windows.historyMainCapitalModel)
    # 将TableView控件设置为显示
    windows.mainCapitalDialog.verticalStackedWidget.setCurrentIndex(0)

# 由股票No或者所属行业查询股票历史轨迹
def historyFromStockLine(windows, formWigdet, stockNo:str='', suoShuHangYe:str=''):
    windows.mainCapitalDialog.verticalLayout.removeWidget(windows.mainCapitalBrowser)
    windows.mainCapitalBrowser.deleteLater()  # 安全删除对象
    windows.mainCapitalBrowser = None  # 清除引用

    ymdhms = f"line_{windows.ChartSuoShuHangYe}_{DateTimeUtils.nowDateTime().strftime('%Y%m%d')}"
    chartFileName = f'{windows.third.charts_dir}/mainCapital_{ymdhms}.html'
    # chart数据编辑
    conditionData = windows.pandasSortData[windows.pandasSortData['所属行业'] == suoShuHangYe].DATA.to_frame()
    suoShuHangYeInfoPandas = pandas.DataFrame(conditionData.values.T[0][0],
                                              columns=conditionData.values.T[0][0].columns)
    logger.info(suoShuHangYeInfoPandas)
    sortStockNos = suoShuHangYeInfoPandas.groupby(by='股票No')

    if sortStockNos:
        xaxisData = []
        title_text_type = opts.TextStyleOpts(font_size=18, font_weight='bold', color='red')
        subtitle_text_type = opts.TextStyleOpts(font_size=13, font_weight='bold', color='#333')
        axislabel_opts = opts.LabelOpts(font_size=13, font_weight='bold', color='#333')
        for nomber, groupCols in sortStockNos:
             if nomber == stockNo:
                for index in range(0, len(groupCols.values)):
                    xaxisData.append((groupCols.values[index][5], groupCols.values[index][0]))
                break


        pieTitle = f'{windows.ChartSuoShuHangYe}折线图'

        # 降序
        pieData = sorted(xaxisData, key=lambda num: num[1], reverse=False)

        pie = Line(init_opts=opts.InitOpts(theme='light', width='958px', height='701px'))
        pie.add_xaxis(list(map(lambda n: n[1], pieData)))
        pie.add_yaxis(f'{windows.ChartSuoShuHangYe}', list(map(lambda n: n[0], pieData)),
                      linestyle_opts=opts.LineStyleOpts(width=3), symbol="diamond", symbol_size=12, color="#c23531")
        pie.set_global_opts(title_opts=opts.TitleOpts(title=pieTitle,
                                                      subtitle=f'{formWigdet.hangQingDate_From.text()} 至 {formWigdet.hangQingDate_To.text()}',
                                                      title_textstyle_opts=title_text_type,
                                                      subtitle_textstyle_opts=subtitle_text_type),
                            toolbox_opts=opts.ToolboxOpts(is_show=False),
                            yaxis_opts=opts.AxisOpts(
                                splitline_opts=opts.SplitLineOpts(
                                    is_show=False # True 显示网格
                                ),
                                axisline_opts=opts.AxisLineOpts(is_show=True),
                                axislabel_opts=axislabel_opts
                            ),
                            xaxis_opts=opts.AxisOpts(
                                splitline_opts=opts.SplitLineOpts(
                                    is_show=False
                                ),
                                axisline_opts=opts.AxisLineOpts(is_show=True),
                                axislabel_opts=axislabel_opts
                            ))
        # 条线图数值显示样式设定
        pie.set_series_opts(
            label_opts=opts.LabelOpts(position="right", font_size=12, font_weight='bold', color="#333"))
        pie.render(chartFileName)

    # 创建web引擎视图
    windows.mainCapitalBrowser = WebEngineView()
    windows.mainCapitalBrowser.load(QUrl(f"file:///{chartFileName}"))
    windows.mainCapitalDialog.verticalLayout.addWidget(windows.mainCapitalBrowser)
    windows.mainCapitalDialog.verticalLayoutWidget.show()
    windows.mainCapitalDialog.verticalStackedWidget.setCurrentIndex(1)

# 分类显示画面初期化
def initShowMainCapitalDialog(windows, formWigdet):
    icon = QIcon()
    icon.addPixmap(QPixmap("_internal/image/outFile.svg"), QIcon.Mode.Normal, QIcon.State.Off)
    windows.third.setWindowIcon(icon)

    pdfIcon = QIcon()
    pdfIcon.addPixmap(QPixmap("_internal/image/pdf.svg"), QIcon.Mode.Normal, QIcon.State.Off)
    windows.mainCapitalDialog.printDialog.setIcon(pdfIcon)
    windows.mainCapitalDialog.printPreview.setIcon(pdfIcon)

    # 确认存放charts文件的目录是否存在
    windows.third.charts_dir = f'{dir_path}/chart'
    if not os.path.exists(windows.third.charts_dir):
        os.makedirs(windows.third.charts_dir)
        # os.system(f'copy "./_internal/chart/echarts.min.js" "{windows.third.charts_dir}"')

    logger.info(f'存放charts文件的目录: [{windows.third.charts_dir}]存在！！！')

    # 确认存放charts文件快照的PNG目录是否存在
    windows.third.charts_png_dir = f'{dir_path}/PNG'
    if not os.path.exists(windows.third.charts_png_dir):
        os.makedirs(windows.third.charts_png_dir)
    logger.info(f'确认存放charts文件快照的PNG目录: [{windows.third.charts_png_dir}]存在！！！')

    # 窗体标题设置
    windows.third.setWindowTitle('资金流向')
    # 窗体固定大小， 最大化无效
    windows.third.setWindowFlags(
        Qt.WindowType.Window | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.MSWindowsFixedSizeDialogHint);
    # 关闭窗口右下角拖动按钮
    windows.third.setStatusBar(QStatusBar().setSizeGripEnabled(False))
    windows.ChartSuoShuHangYe = 'all'
    # TreeView设定
    initMCDTreeView(windows, formWigdet)
    # QFrame设定
    initFrame(windows, formWigdet)

# QFrame设定
def initFrame(windows, formWigdet, chartType:str='pie'):
    ymdhms = f"{chartType}_{windows.ChartSuoShuHangYe}_{DateTimeUtils.nowDateTime().strftime('%Y%m%d')}"
    chartFileName = f'{windows.third.charts_dir}/mainCapital_{ymdhms}.html'
    # chart数据编辑
    editMCDChartData(windows, formWigdet, chartFileName)
    # 创建web引擎视图
    windows.mainCapitalBrowser = WebEngineView()
    windows.mainCapitalBrowser.load(QUrl(f"file:///{chartFileName}"))
    windows.mainCapitalBrowser.loadFinished.connect(partial(on_load_finished, windows, formWigdet))
    windows.mainCapitalDialog.verticalLayout.addWidget(windows.mainCapitalBrowser)
    windows.mainCapitalDialog.verticalLayoutWidget.show()
    windows.mainCapitalDialog.verticalStackedWidget.setCurrentIndex(1)

# chart数据编辑
def editMCDChartData(windows, formWigdet, chartFileName):
    # 修改pyecharts库的js路径，变成本地文件夹
    CurrentConfig.ONLINE_HOST = ''
    pieData = []
    title_text_type = opts.TextStyleOpts(font_size=18, font_weight='bold', color='red')
    subtitle_text_type = opts.TextStyleOpts(font_size=13, font_weight='bold', color='#333')
    axislabel_opts = opts.LabelOpts(font_size=13, font_weight='bold', color='#333')
    if windows.ChartSuoShuHangYe == 'all':
        windows.pdfPngFile = f'{windows.third.charts_png_dir}/mainCapital_all.png'
        # 所有行业饼图地址
        windows.pieOfsshyPath = chartFileName
        if formWigdet.stock_stockType.currentText() != '全部':
            pieTitle = f'{formWigdet.stock_stockType.currentText()}主力资金饼图'
        else:
            pieTitle = '主力资金饼图'
        windows.mainCapitalDialog.nav_option.setText(f'行业名称：{windows.mainCapitalDialog.allSshyCharts.text()}')
        groupTotal = windows.pandasSortData.groupby(by='数量')
        for name, groupCols in groupTotal:
            # suoShuHangYes = '/'.join(groupCols['所属行业'])
            suoShuHangYes = '/'.join(groupCols['所属行业'][:3]) + '...' if len(groupCols['所属行业']) > 3 else '/'.join(
                groupCols['所属行业'])
            pieData.append((suoShuHangYes, name))

        # 设置图例不显示：is_show=False, 逆时针显示：is_clockwise=False
        pie = (Pie(init_opts=opts.InitOpts(theme='light', width='978px', height='688px'))
               .add('', pieData, is_clockwise=False)
               .set_series_opts(radius=['25%', '50%'], label_opts=opts.LabelOpts(position="right", formatter="{b}: {c}件", font_size=12, font_weight='bold',
                                          color="#333"))
               .set_global_opts(title_opts=opts.TitleOpts(title=pieTitle, subtitle=f'{formWigdet.hangQingDate_From.text()} 至 {formWigdet.hangQingDate_To.text()}',
                                                          title_textstyle_opts=title_text_type, subtitle_textstyle_opts=subtitle_text_type),
                                legend_opts=opts.LegendOpts(is_show=False, orient='vertical', pos_top='18%',
                                                            pos_left='3%'))
               )
    else:
        windows.pdfPngFile = f'{windows.third.charts_png_dir}/mainCapital_sshy.png'
        # pandas.DataFrame 条件检索
        # 组合条件：&(和) | (或)
        conditionData = windows.pandasSortData[windows.pandasSortData['所属行业'] == windows.ChartSuoShuHangYe].DATA.to_frame()
        suoShuHangYeInfoPandas = pandas.DataFrame(conditionData.values.T[0][0], columns=conditionData.values.T[0][0].columns)
        logger.info(suoShuHangYeInfoPandas)
        sortStockNames = suoShuHangYeInfoPandas.groupby(by='名称')
        stock_counts = [(name, len(group)) for name, group in sortStockNames]
        # 按统计数量从大到小排序
        sorted_stocks = sorted(stock_counts, key=lambda x: x[1], reverse=True)
        stockGroupDict = {name: count for name, count in sorted_stocks}
        pieStockNmData = []
        pieTitle = f'{windows.ChartSuoShuHangYe}条形图Top20'
        top20 = 20
        for name in stockGroupDict:
            pieStockNmData.append((name, stockGroupDict[name]))
            if top20 == 1:
                break
            top20 -= 1

        # 降序
        pieData = sorted(pieStockNmData, key=lambda num : num[1], reverse=False)

        pie = Bar(init_opts=opts.InitOpts(theme='light', width='958px', height='701px'))
        pie.add_xaxis(list(map(lambda n : n[0], pieData)))
        pie.add_yaxis(f'{windows.ChartSuoShuHangYe}', list(map(lambda n: n[1], pieData)))
        pie.set_global_opts(title_opts=opts.TitleOpts(title=pieTitle, subtitle=f'{formWigdet.hangQingDate_From.text()} 至 {formWigdet.hangQingDate_To.text()}',
                                                      title_textstyle_opts=title_text_type, subtitle_textstyle_opts=subtitle_text_type),
                            toolbox_opts=opts.ToolboxOpts(is_show=False),
                            yaxis_opts=opts.AxisOpts(
                                splitline_opts=opts.SplitLineOpts(
                                    is_show=False  # True 显示网格
                                ),
                                axisline_opts=opts.AxisLineOpts(is_show=True),
                                axislabel_opts=axislabel_opts
                            ),
                            xaxis_opts=opts.AxisOpts(
                                splitline_opts=opts.SplitLineOpts(
                                    is_show=False
                                ),
                                axisline_opts=opts.AxisLineOpts(is_show=True),
                                axislabel_opts=axislabel_opts
                            ))
        # 条线图数值显示样式设定
        pie.set_series_opts(
            label_opts=opts.LabelOpts(position="right", formatter="{c}件", font_size=12, font_weight='bold', color="#333"))
        pie.reversal_axis()

        # 缓存处理
        windows.barOfSingleSshyPaths[windows.ChartSuoShuHangYe] = chartFileName

    pie.render(chartFileName)

# TreeView设定
def initMCDTreeView(windows, formWigdet):
    treeModel = QStandardItemModel()
    treeModel.setHorizontalHeaderLabels(['所属行业/股票名称', '总数', '现价', '涨幅', 'hidden', 'hidden', 'hidden', 'hidden', 'hidden'])
    rootItem = treeModel.invisibleRootItem()
    windows.pandasSortData = MainCapitalModel.editSuoShuHangYeAndSort(windows.showMainCapitalData, formWigdet)
    for indexNo in windows.pandasSortData.index:
        sshy = windows.pandasSortData.loc[indexNo, '所属行业']
        suoShuHangYeQS = QStandardItem(sshy)
        suoShuHangYeQS_total = QStandardItem(str(windows.pandasSortData.loc[indexNo, '数量']))
        stockNames = windows.pandasSortData.loc[indexNo, '股票名称']
        stockXianJias = windows.pandasSortData.loc[indexNo, '现价']
        stockZhangFus = windows.pandasSortData.loc[indexNo, '涨幅']
        stockDepthDataUrls = windows.pandasSortData.loc[indexNo, '数据URL']
        stockF10Urls = windows.pandasSortData.loc[indexNo, 'F10URL']
        stockReportchartUrls = windows.pandasSortData.loc[indexNo, '可视化报告']
        stockInfoDatas = windows.pandasSortData.loc[indexNo, 'DATA']
        stockGroupDatas = stockInfoDatas.groupby(by='股票No')
        stock_counts = [(name, len(group)) for name, group in stockGroupDatas]
        # 按统计数量从大到小排序
        sorted_stocks = sorted(stock_counts, key=lambda x: x[1], reverse=True)
        stockGroupDict = { name: count for name, count in sorted_stocks}
        for stockNo in stockGroupDict.keys():
            suoShuHangYeQS.appendRow(
                [QStandardItem(stockNames[stockNo]),
                 QStandardItem(str(stockGroupDict[stockNo])),
                 QStandardItem(str(stockXianJias[stockNo])),
                 QStandardItem(str(stockZhangFus[stockNo])),
                 QStandardItem(stockDepthDataUrls[stockNo]),
                 QStandardItem(stockF10Urls[stockNo]),
                 QStandardItem(stockReportchartUrls[stockNo]),
                 QStandardItem(sshy),
                 QStandardItem(stockNo)])
        rootItem.appendRow([suoShuHangYeQS, suoShuHangYeQS_total])

    windows.mainCapitalDialog.mainCapitalTree.setModel(treeModel)
    windows.mainCapitalDialog.mainCapitalTree.setColumnWidth(0, 110)
    windows.mainCapitalDialog.mainCapitalTree.setColumnWidth(1, 40)
    windows.mainCapitalDialog.mainCapitalTree.setColumnWidth(2, 45)
    windows.mainCapitalDialog.mainCapitalTree.setColumnWidth(3, 45)
    windows.mainCapitalDialog.mainCapitalTree.setColumnWidth(4, 7)
    windows.mainCapitalDialog.mainCapitalTree.setColumnWidth(5, 7)
    windows.mainCapitalDialog.mainCapitalTree.setColumnWidth(6, 7)
    windows.mainCapitalDialog.mainCapitalTree.setColumnWidth(7, 7)
    windows.mainCapitalDialog.mainCapitalTree.setColumnWidth(8, 7)
    # 将第五至九列隐藏
    windows.mainCapitalDialog.mainCapitalTree.setColumnHidden(4, True)
    windows.mainCapitalDialog.mainCapitalTree.setColumnHidden(5, True)
    windows.mainCapitalDialog.mainCapitalTree.setColumnHidden(6, True)
    windows.mainCapitalDialog.mainCapitalTree.setColumnHidden(7, True)
    windows.mainCapitalDialog.mainCapitalTree.setColumnHidden(8, True)
    # 禁止拖动
    windows.mainCapitalDialog.mainCapitalTree.setDragEnabled(False)
    windows.mainCapitalDialog.mainCapitalTree.setAcceptDrops(False)
    # 设置单选模式
    windows.mainCapitalDialog.mainCapitalTree.setSelectionMode(QTreeView.SelectionMode.SingleSelection)
    windows.mainCapitalDialog.mainCapitalTree.setAnimated(True)
    # 禁止编辑
    windows.mainCapitalDialog.mainCapitalTree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    # 设置行选择颜色 (新增部分)
    selection_color = "#2a82da"  # 选择时的蓝色背景
    hover_color = "#ddeeff"  # 鼠标悬停时的浅蓝色
    text_color = "#ffffff"  # 选择时的白色文字

    windows.mainCapitalDialog.mainCapitalTree.setStyleSheet(f"""
                            QTreeView::item:selected {{
                                background-color: {selection_color};
                                color: {text_color};
                            }}
                            QTreeView::item:hover {{
                                background-color: {hover_color};
                            }}
                        """)

# 事件绑定 -- 检索
def AddClickedMasterStockSubmit(windows, formWigdet):
    # 主力资金--数据绑定
    editMainCapitalTable(windows, formWigdet)

# 主力资金--数据绑定
def editMainCapitalTable(windows, formWigdet):
    # 主力资金Tab--数据绑定
    getMainCapitalData(windows, formWigdet)
    # 主力资金Tab--数据显示设定
    setingMainCapitalTable(formWigdet.master_showStockTable)

# 主力资金Tab--数据绑定
def getMainCapitalData(windows, formWigdet):
    # 检索条件获取
    # 交易日期From
    hangQingDateFrom = DateTimeUtils.Format_changed(formWigdet.hangQingDate_From.text(), '%Y年%M月%d日', '%Y%M%d')
    # 交易日期To
    hangQingDateTo = DateTimeUtils.Format_changed(formWigdet.hangQingDate_To.text(), '%Y年%M月%d日', '%Y%M%d')
    # 股票No
    masterStockNo = formWigdet.master_stockNo_v.text()
    # 股票名称
    masterStockName = formWigdet.master_stockName_v.text()
    # 所属行业
    masterHangYe = formWigdet.master_hangYe_v.text()
    # 涨幅
    masterZhangFu = formWigdet.master_zhangFu_v.text()
    # 现价
    masterXianJia = formWigdet.master_xianJia_v.text()
    # 风险种类
    masterStockType = formWigdet.master_stockType.currentIndex()
    # 现价比较条件
    condition_xj = formWigdet.condition_xj.currentIndex()

    # 排序选项
    orderByOption = ' ORDER BY SIW.HANG_QING_DATE DESC'
    # 检索条件设定
    mainCapitalCondition = MainCapitalCondition(hangQingDateFrom, hangQingDateTo, masterStockNo, masterStockName, masterHangYe,
                                                masterZhangFu, masterXianJia, masterStockType, condition_xj, 'D', orderByOption)

    enableFlag = False
    # 数据检索
    windows.showMainCapitalData = MainCapitalModel.getMainCapitalWLWData(mainCapitalCondition)

    if windows.showMainCapitalData:
        enableFlag = True

    # 总件数format
    formWigdet.maste_count_number.setText(f'一共 {len(windows.showMainCapitalData)} 件数据')
    # 分类显示按钮是否可操作设定
    formWigdet.showMainCapitalDialog.setEnabled(enableFlag)

    # 页码初始化
    windows.current_MainPage = 1
    # 分页处理
    data = get_page(windows.showMainCapitalData, windows.current_MainPage, 20)
    # 数据显示处理
    showTableData(data, windows, formWigdet)

# 主力资金Tab--数据显示设定
def setingMainCapitalTable(tableView):
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

    # 设置列宽 1458
    tableView.setColumnWidth(0, 80)
    tableView.setColumnWidth(1, 80)
    tableView.setColumnWidth(2, 70)
    tableView.setColumnWidth(3, 80)
    tableView.setColumnWidth(4, 73)
    tableView.setColumnWidth(5, 69)
    tableView.setColumnWidth(6, 74)
    tableView.setColumnWidth(7, 88)
    tableView.setColumnWidth(8, 96)
    tableView.setColumnWidth(9, 104)
    tableView.setColumnWidth(10, 106)
    tableView.setColumnWidth(11, 90)
    tableView.setColumnWidth(12, 90)
    tableView.setColumnWidth(13, 94)
    tableView.setColumnWidth(14, 94)
    tableView.setColumnWidth(15, 90)
    # 统计行数
    rowCount = tableView.model().rowCount()
    # 行数 小于 10
    if rowCount < 10:
        tableView.setColumnWidth(16, 101)
    else:
        tableView.setColumnWidth(16, 94)

    # 启用数据排序和过滤
    tableView.setSortingEnabled(True)
    # 设置表格为整行选择 QAbstractItemView.SelectionBehavior(1) 单元格选中：QAbstractItemView.SelectionBehavior(0) 列选中：QAbstractItemView.SelectionBehavior(2)
    tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior(1))
    # 禁止列宽调整
    tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
    tableView.horizontalHeader().setSectionsMovable(False)

    # 获取列宽 用来手动调节每列列宽
    # tableView.horizontalHeader().sectionResized.connect(
    #     lambda index, old_size, new_size: print(f"列{index}宽度变为{new_size}"))

# 事件绑定 -- 清除
def AddClickedMasterClear(windows, formWigdet):
    mainCapitalInitContent(windows, formWigdet)