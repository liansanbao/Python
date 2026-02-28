# _*_ coding: utf-8 _*_
# @Time : 2026/2/4 星期三 21:38
# @Author : 韦丽
# @Version: V 1.0
# @File : CapitalAction.py
# @desc : 分类显示（个股详情数据）
import datetime
import os
from functools import partial

import pandas
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon, QPixmap
from PyQt6.QtWidgets import QMainWindow, QAbstractItemView, QStatusBar, QTreeView
from pyecharts.charts import Bar, Pie, Line
from pyecharts import options as opts
from pyecharts.globals import CurrentConfig

from WLW.StockBase import DateTimeUtils
from WLW.Tools.LoggingEx import logger
from WLW.WebView.QWebViewEx import FunctionMW
from WLW.action.WebEngineViewEx import WebEngineView
from WLW.ComplexLayoutPDF import ComplexLayoutPDF
from WLW.Ui_mainCapitalDialog import Ui_mainCapitalDialog
from WLW.model import StockInfoModel

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)

# 获取所在文件夹路径
dir_path = str(os.path.dirname(script_path))

dir_path = dir_path.replace('\\', '/')

def create_page(windows, formWidget):
    try:
        windows.second = QMainWindow()
        windows.stockDialog = Ui_mainCapitalDialog()
        windows.stockDialog.setupUi(windows.second)
        # 按钮名称切换
        windows.stockDialog.allSshyCharts.setText('所有主题')
        # 所有行业饼图地址
        windows.pieOfsshyPath = ''
        # 单一行业条形图地址
        windows.barOfSingleSshyPaths = {}
        # 图形显示格式设定不显示
        windows.stockDialog.showType.setEnabled(False)
        windows.stockDialog.printDialog.setEnabled(False)
        windows.stockDialog.showType.addItems(['表格', '折线图', '资金流向', '数据中心', 'F10资料', '可视化报告'])
        windows.stockDialog.showType.setCurrentIndex(0)
        windows.stockDialog.showType.currentTextChanged.connect(partial(calculate_values, windows, formWidget))
        # 分类显示画面初期化
        initStockDialog(windows, formWidget)
        # 分类显示画面事件绑定
        actionStockDialog(windows, formWidget)

        # 新增关闭事件处理
        def handle_close_event():
            windows.second.hide()  # 隐藏当前窗口
            windows._LWLW__mainWindow.show()  # 恢复主窗口显示

        # 绑定三种关闭方式
        windows.second.closeEvent = lambda e: handle_close_event()  # 点击关闭按钮

        windows.second.setWindowModality(Qt.WindowModality.ApplicationModal) # 阻塞所有窗口操作
        windows.second.show()
        windows._LWLW__mainWindow.hide() # 隐藏主窗口显示
    except Exception as ex:
        logger.error(f'create_page:{str(ex)}')

# 图形显示格式切换事件
def calculate_values(windows, formWidget):
    onSelectionChanged(windows, formWidget)

# TreeView行选择事件
def onSelectionChanged(windows, formWidget):
    try:
        windows.stockDialog.printDialog.setEnabled(False)
        indexes = windows.stockDialog.mainCapitalTree.selectionModel().selectedIndexes()  # 获取当前选中的索引列表

        if indexes:
            index = indexes[len(indexes) - 1]  # 只处理第一个索引，通常是顶层索引
            stockNo = windows.stockDialog.mainCapitalTree.model().itemFromIndex(index).text()
            windows.ChartSuoShuHangYe = windows.stockDialog.mainCapitalTree.model().itemFromIndex(
                indexes[0]).text()
            # 行业还是个股
            if stockNo == '':
                windows.stockDialog.nav_option.setText(f'涨停主题：{windows.ChartSuoShuHangYe}')
                isShowType = False
                windows.stockDialog.verticalLayout.removeWidget(windows.stockInfoBrowser)
                windows.stockInfoBrowser.deleteLater()  # 安全删除对象
                windows.stockInfoBrowser = None  # 清除引用
                barOfSingleSshyPaths = dict(windows.barOfSingleSshyPaths)
                if windows.ChartSuoShuHangYe in barOfSingleSshyPaths.keys():
                    pageTwo(windows, formWidget, windows.barOfSingleSshyPaths[windows.ChartSuoShuHangYe], 'Charts')
                else:
                    initFrame(windows, formWidget, 'bar')
            else:
                windows.stockDialog.nav_option.setText(f'股票名称：{windows.ChartSuoShuHangYe} No：{stockNo} ')
                isShowType = True
                # 由股票No或者所属行业查询股票历史轨迹
                index = indexes[len(indexes) - 2]
                suoShuHangYe = windows.stockDialog.mainCapitalTree.model().itemFromIndex(index).text()
                # 获取当前选择的显示类型
                display_type = windows.stockDialog.showType.currentText()

                if display_type == "表格":
                    historyFromStock(windows, formWidget, stockNo, suoShuHangYe)
                    setingDialogStockTable(windows.stockDialog.tableView)
                elif display_type == "折线图":
                    historyFromStockLine(windows, formWidget, stockNo, suoShuHangYe)
                elif display_type == "数据中心":
                    # 数据URL显示
                    index = indexes[len(indexes) - 5]
                    stockDepthDataUrls = windows.stockDialog.mainCapitalTree.model().itemFromIndex(index).text()
                    showWebDataUrl(windows, stockDepthDataUrls)
                elif display_type == "F10资料":
                    # F10数据URL显示
                    index = indexes[len(indexes) - 4]
                    stockF10Urls = windows.stockDialog.mainCapitalTree.model().itemFromIndex(index).text()
                    showWebDataUrl(windows, stockF10Urls)
                elif display_type == "可视化报告":
                    # 可视化报告数据URL显示
                    index = indexes[len(indexes) - 3]
                    stockReportchartUrls = windows.stockDialog.mainCapitalTree.model().itemFromIndex(index).text()
                    showWebDataUrl(windows, stockReportchartUrls)
                elif display_type == "资金流向":
                    # 资金流向数据URL显示
                    stockReportchartUrls = f'https://data.eastmoney.com/zjlx/{stockNo}.html'
                    showWebDataUrl(windows, stockReportchartUrls)

            # 图形显示格式设定: False不显示
            windows.stockDialog.showType.setEnabled(isShowType)
            windows.stockDialog.printPreview.setEnabled(not isShowType)
    except Exception as ex:
        logger.error(f'TreeView行选择处理出错了：{str(ex)}')

# PageTwo显示设定
def pageTwo(windows, formWidget, path, fileType):
    try:
        # 创建web引擎视图
        windows.stockInfoBrowser = WebEngineView()
        # PDF文件
        windows.stockInfoBrowser.load(QUrl(f"file:///{path}"))
        if fileType == 'Charts':
            windows.stockInfoBrowser.loadFinished.connect(partial(on_load_finished, windows, formWidget))

        windows.stockDialog.verticalLayout.addWidget(windows.stockInfoBrowser)
        windows.stockDialog.verticalLayoutWidget.show()
        windows.stockDialog.verticalStackedWidget.setCurrentIndex(1)
    except Exception as ex:
        logger.error(f'pageTwo出错了： {ex}')

def on_load_finished(windows, formWidget):
    # QTimer.singleShot(1000, lambda :
    #                   windows.stockInfoBrowser.grab().save(windows.pdfPngFile, "PNG"))
    QTimer.singleShot(1000, partial(save_high_res, windows))

def save_high_res(windows):
    windows.stockInfoBrowser.page().runJavaScript("document.body.scrollHeight;",
        lambda height: windows.stockInfoBrowser.grab().scaled(
            windows.stockInfoBrowser.size(),  # 2倍缩放
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ).save(windows.pdfPngFile, "PNG", 100)  # 100%质量
    )

# QFrame设定
def initFrame(windows, formWidget, chartType:str='pie'):
    # 确认存放charts文件的目录是否存在
    ymdhms = f"{chartType}_{windows.ChartSuoShuHangYe}_{DateTimeUtils.nowDateTime().strftime('%Y%m%d')}"
    chartFileName = f'{windows.second.charts_dir}/DL_{ymdhms}.html'

    # chart数据编辑
    editMCDChartData(windows, formWidget, chartFileName)
    # 创建web引擎视图
    windows.stockInfoBrowser = WebEngineView()
    windows.stockInfoBrowser.load(QUrl(f"file:///{chartFileName}"))
    windows.stockInfoBrowser.loadFinished.connect(partial(on_load_finished, windows, formWidget))
    windows.stockDialog.verticalLayout.addWidget(windows.stockInfoBrowser)
    windows.stockDialog.verticalLayoutWidget.show()
    windows.stockDialog.verticalStackedWidget.setCurrentIndex(1)

# chart数据编辑
def editMCDChartData(windows, formWidget, chartFileName):
    # 修改pyecharts库的js路径，变成本地文件夹
    CurrentConfig.ONLINE_HOST = ''
    pieData = []
    title_text_type = opts.TextStyleOpts(font_size=18, font_weight='bold', color='red')
    subtitle_text_type = opts.TextStyleOpts(font_size=13, font_weight='bold', color='#333')
    axislabel_opts = opts.LabelOpts(font_size=13, font_weight='bold', color='#333')
    if windows.ChartSuoShuHangYe == 'all':
        windows.pdfPngFile = f'{windows.second.charts_png_dir}/dl_all.png'
        # 所有行业饼图地址
        windows.pieOfsshyPath = chartFileName
        if formWidget.stock_stockType.currentText() != '全部':
            pieTitle = f'{formWidget.stock_stockType.currentText()}主力资金饼图'
        else:
            pieTitle = '主力资金饼图'
        windows.stockDialog.nav_option.setText(f'行业名称：{windows.stockDialog.allSshyCharts.text()}')
        groupTotal = windows.pandasSortData.groupby(by='数量')
        for name, groupCols in groupTotal:
            # suoShuHangYes = '/'.join(groupCols['涨停主题'])
            suoShuHangYes = '/'.join(groupCols['涨停主题'][:3]) + '...' if len(groupCols['涨停主题']) > 3 else '/'.join(
                groupCols['涨停主题'])
            pieData.append((suoShuHangYes, name))

        # 设置图例不显示：is_show=False, 逆时针显示：is_clockwise=False
        pie = (Pie(init_opts=opts.InitOpts(theme='light', width='978px', height='688px'))
                    .add('', pieData, is_clockwise=False)
                    .set_series_opts(radius=['25%', '50%'], label_opts=opts.LabelOpts(position="right", formatter="{b}: {c}件", font_size=12, font_weight='bold',
                                          color="#333"))
                    .set_global_opts(title_opts=opts.TitleOpts(
                                    title=pieTitle,
                                    subtitle=f'{formWidget.saleDateFrom.text()} 至 {formWidget.saleDateTo.text()}',
                                    title_textstyle_opts=title_text_type,
                                    subtitle_textstyle_opts=subtitle_text_type),
                                    legend_opts=opts.LegendOpts(is_show=False, orient='vertical', pos_top='18%', pos_left='3%')
                    )
               )
    else:
        windows.pdfPngFile = f'{windows.second.charts_png_dir}/dl_sshy.png'
        # pandas.DataFrame 条件检索
        # 组合条件：&(和) | (或)
        conditionData = windows.pandasSortData[windows.pandasSortData['涨停主题'] == windows.ChartSuoShuHangYe].DATA.to_frame()
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
        pie.set_global_opts(title_opts=opts.TitleOpts(title=pieTitle, subtitle=f'{formWidget.saleDateFrom.text()} 至 {formWidget.saleDateTo.text()}',
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
        pie.set_series_opts(label_opts=opts.LabelOpts(position="right", formatter="{c}件", font_size=12, font_weight='bold',color="#333"))
        pie.reversal_axis()

        # 缓存处理
        windows.barOfSingleSshyPaths[windows.ChartSuoShuHangYe] = chartFileName

    pie.render(chartFileName)

# 由股票No或者所属行业查询股票历史轨迹
def historyFromStock(windows, formWidget, stockNo:str='', suoShuHangYe:str=''):
    # ListView model 4Row 3 coloumn
    windows.historyMainCapitalModel = QStandardItemModel(0, 12)
    # 创建行标题
    windows.historyMainCapitalModel.setHorizontalHeaderLabels(
        ['所属行业', '交易日期', '涨跌幅(%)', '最新价(元)', '连板数', '炸板次数', '成交额(亿)', '换手率(%)', 'F封板时间', 'L封板时间', '封板资金', '涨停统计'])

    # 设定项目值显示
    showHeaderLables = [1, 0, 4, 5, 6, 7, 10, 11, 12, 13, 14, 15]

    # 添加数据;
    # pandas.DataFrame 条件检索
    # 组合条件：&(和) | (或)
    conditionData = windows.pandasSortData[windows.pandasSortData['涨停主题'] == suoShuHangYe].DATA.to_frame()
    suoShuHangYeInfoPandas = pandas.DataFrame(conditionData.values.T[0][0],
                                              columns=conditionData.values.T[0][0].columns)
    logger.info(f'historyFromStock: {suoShuHangYeInfoPandas}')
    sortStockNos = suoShuHangYeInfoPandas.groupby(by='股票No')

    if sortStockNos:
        for nomber, groupCols in sortStockNos:
             if nomber == stockNo:
                for index in range(0, len(groupCols.values)):
                    windows.historyMainCapitalModel.appendRow([QStandardItem(str(groupCols.values[index][value])) for value in showHeaderLables])
                break

    windows.stockDialog.tableView.setModel(windows.historyMainCapitalModel)
    # 将TableView控件设置为显示
    windows.stockDialog.verticalStackedWidget.setCurrentIndex(0)

# 涨停板分类显示--数据显示设定
def setingDialogStockTable(tableView):
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
    tableView.setColumnWidth(0, 90)
    tableView.setColumnWidth(1, 105)
    tableView.setColumnWidth(2, 80)
    tableView.setColumnWidth(3, 80)
    tableView.setColumnWidth(4, 80)
    tableView.setColumnWidth(5, 80)
    tableView.setColumnWidth(6, 90)
    tableView.setColumnWidth(7, 90)
    tableView.setColumnWidth(8, 90)
    tableView.setColumnWidth(9, 90)
    tableView.setColumnWidth(10, 90)
    tableView.setColumnWidth(11, 90)

    # 启用数据排序和过滤
    tableView.setSortingEnabled(True)
    # 设置表格为整行选择 QAbstractItemView.SelectionBehavior(1) 单元格选中：QAbstractItemView.SelectionBehavior(0) 列选中：QAbstractItemView.SelectionBehavior(2)
    tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

# 由股票No或者所属行业查询股票历史轨迹
def historyFromStockLine(windows, formWidget, stockNo:str='', suoShuHangYe:str=''):
    windows.stockDialog.verticalLayout.removeWidget(windows.stockInfoBrowser)
    windows.stockInfoBrowser.deleteLater()  # 安全删除对象
    windows.stockInfoBrowser = None  # 清除引用

    ymdhms = f"line_{windows.ChartSuoShuHangYe}_{DateTimeUtils.nowDateTime().strftime('%Y%m%d')}"
    chartFileName = f'{windows.second.charts_dir}/DL_{ymdhms}.html'
    # chart数据编辑
    conditionData = windows.pandasSortData[windows.pandasSortData['涨停主题'] == suoShuHangYe].DATA.to_frame()
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

        pie = Line(init_opts=opts.InitOpts(theme='light', width='998px', height='701px'))
        pie.add_xaxis(list(map(lambda n: n[1], pieData)))
        pie.add_yaxis(f'{windows.ChartSuoShuHangYe}', list(map(lambda n: n[0], pieData)),
                      linestyle_opts=opts.LineStyleOpts(width=3), symbol="diamond", symbol_size=12, color="#c23531")
        pie.set_global_opts(title_opts=opts.TitleOpts(title=pieTitle,
                                                      subtitle=f'{formWidget.saleDateFrom.text()} 至 {formWidget.saleDateTo.text()}',
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
    windows.stockInfoBrowser = WebEngineView()
    windows.stockInfoBrowser.load(QUrl(f"file:///{chartFileName}"))
    windows.stockDialog.verticalLayout.addWidget(windows.stockInfoBrowser)
    windows.stockDialog.verticalLayoutWidget.show()
    windows.stockDialog.verticalStackedWidget.setCurrentIndex(1)

# （数据、F10、可视化报告）URL
def showWebDataUrl(windows, dataUrl):
    windows.stockDialog.verticalLayout.removeWidget(windows.stockInfoBrowser)
    windows.stockInfoBrowser.deleteLater()  # 安全删除对象
    windows.stockInfoBrowser = None  # 清除引用
    # 创建web引擎视图
    windows.stockInfoBrowser = WebEngineView()
    windows.stockInfoBrowser.load(QUrl(dataUrl))
    windows.stockDialog.verticalLayout.addWidget(windows.stockInfoBrowser)
    windows.stockDialog.verticalLayoutWidget.show()
    windows.stockDialog.verticalStackedWidget.setCurrentIndex(1)

# 分类显示画面初期化
def initStockDialog(windows, formWidget):
    icon = QIcon()
    icon.addPixmap(QPixmap("_internal/image/outFile.svg"), QIcon.Mode.Normal, QIcon.State.Off)
    windows.second.setWindowIcon(icon)

    pdfIcon = QIcon()
    pdfIcon.addPixmap(QPixmap("_internal/image/pdf.svg"), QIcon.Mode.Normal, QIcon.State.Off)
    windows.stockDialog.printDialog.setIcon(pdfIcon)
    windows.stockDialog.printPreview.setIcon(pdfIcon)

    # 确认存放charts文件的目录是否存在
    windows.second.charts_dir = f'{dir_path}/chart'
    if not os.path.exists(windows.second.charts_dir):
        os.makedirs(windows.second.charts_dir)
    logger.info(f'存放charts文件的目录: [{windows.second.charts_dir}]存在！！！')

    # 确认存放charts文件快照的PNG目录是否存在
    windows.second.charts_png_dir = f'{dir_path}/PNG'
    if not os.path.exists(windows.second.charts_png_dir):
        os.makedirs(windows.second.charts_png_dir)
    logger.info(f'确认存放charts文件快照的PNG目录: [{windows.second.charts_png_dir}]存在！！！')

    # 窗体标题设置
    windows.second.setWindowTitle('涨停板')
    # 窗体固定大小， 最大化无效
    windows.second.setWindowFlags(
        Qt.WindowType.Window | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.MSWindowsFixedSizeDialogHint);
    # 关闭窗口右下角拖动按钮
    windows.second.setStatusBar(QStatusBar().setSizeGripEnabled(False))
    windows.ChartSuoShuHangYe = 'all'
    # TreeView设定
    initMCDTreeView(windows, formWidget)
    # QFrame设定
    initFrame(windows, formWidget)

# TreeView设定
def initMCDTreeView(windows, formWidget):
    treeModel = QStandardItemModel()
    treeModel.setHorizontalHeaderLabels(['涨停主题/股票名称', '总数', '现价', '涨幅', 'hidden', 'hidden', 'hidden', 'hidden', 'hidden'])
    rootItem = treeModel.invisibleRootItem()
    windows.pandasSortData = StockInfoModel.editSuoShuHangYeAndSort(windows.showStockData, formWidget)
    for indexNo in windows.pandasSortData.index:
        sshy = windows.pandasSortData.loc[indexNo, '涨停主题']
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
        stockGroupDict = {name: count for name, count in sorted_stocks}
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

    windows.stockDialog.mainCapitalTree.setModel(treeModel)
    windows.stockDialog.mainCapitalTree.setColumnWidth(0, 110)
    windows.stockDialog.mainCapitalTree.setColumnWidth(1, 40)
    windows.stockDialog.mainCapitalTree.setColumnWidth(2, 45)
    windows.stockDialog.mainCapitalTree.setColumnWidth(3, 45)
    windows.stockDialog.mainCapitalTree.setColumnWidth(4, 7)
    windows.stockDialog.mainCapitalTree.setColumnWidth(5, 7)
    windows.stockDialog.mainCapitalTree.setColumnWidth(6, 7)
    windows.stockDialog.mainCapitalTree.setColumnWidth(7, 7)
    windows.stockDialog.mainCapitalTree.setColumnWidth(8, 7)
    # 将第五至九列隐藏
    windows.stockDialog.mainCapitalTree.setColumnHidden(4, True)
    windows.stockDialog.mainCapitalTree.setColumnHidden(5, True)
    windows.stockDialog.mainCapitalTree.setColumnHidden(6, True)
    windows.stockDialog.mainCapitalTree.setColumnHidden(7, True)
    windows.stockDialog.mainCapitalTree.setColumnHidden(8, True)
    # 禁止拖动
    windows.stockDialog.mainCapitalTree.setDragEnabled(False)
    windows.stockDialog.mainCapitalTree.setAcceptDrops(False)
    # 设置单选模式
    windows.stockDialog.mainCapitalTree.setSelectionMode(QTreeView.SelectionMode.SingleSelection)
    windows.stockDialog.mainCapitalTree.setAnimated(True)
    # 禁止编辑
    windows.stockDialog.mainCapitalTree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    # 设置行选择颜色 (新增部分)
    selection_color = "#2a82da"  # 选择时的蓝色背景
    hover_color = "#ddeeff"  # 鼠标悬停时的浅蓝色
    text_color = "#ffffff"  # 选择时的白色文字

    windows.stockDialog.mainCapitalTree.setStyleSheet(f"""
                        QTreeView::item:selected {{
                            background-color: {selection_color};
                            color: {text_color};
                        }}
                        QTreeView::item:hover {{
                            background-color: {hover_color};
                        }}
                    """)

# 分类显示画面事件绑定
def actionStockDialog(windows, formWidget):
    # TreeView行选择事件
    windows.stockDialog.mainCapitalTree.selectionModel().selectionChanged.connect(partial(onSelectionChanged, windows, formWidget))
    # 所属行业数据
    windows.stockDialog.allSshyCharts.clicked.connect(partial(clickedStockPreview, windows, formWidget))
    # 预览
    windows.stockDialog.printPreview.clicked.connect(partial(clickedPrintPreview, windows, formWidget))
    # 打印
    windows.stockDialog.printDialog.clicked.connect(partial(handlerPrint, windows, formWidget))
    # PDF出力
    # windows.stockDialog.printOut.clicked.connect(partial(clickedStockPDF, windows, formWidget, 'Preview'))

# 所属行业数据
def clickedStockPreview(windows, formWidget):
    windows.stockDialog.printDialog.setEnabled(False)
    windows.stockDialog.printPreview.setEnabled(True)
    # 图形显示格式设定: False不显示
    windows.stockDialog.showType.setEnabled(False)
    windows.ChartSuoShuHangYe = 'all'
    windows.stockDialog.verticalLayout.removeWidget(windows.stockInfoBrowser)
    windows.stockInfoBrowser.deleteLater()  # 安全删除对象
    windows.stockInfoBrowser = None  # 清除引用
    if windows.pieOfsshyPath == '':
        # QFrame设定
        initFrame(windows, formWidget)
    else:
        windows.stockDialog.nav_option.setText(f'行业名称：{windows.stockDialog.allSshyCharts.text()}')
        pageTwo(windows, formWidget, windows.pieOfsshyPath, 'Charts')

# 预览
def clickedPrintPreview(windows, formWidget):
    try:
        windows.browserPrinterDialogUrl = ''
        clickedStockPDF(windows, formWidget, 'Preview')
        if windows.browserPrinterDialogUrl != '':
            windows.stockDialog.printDialog.setEnabled(True)
            windows.webBrowser = FunctionMW(windows.browserPrinterDialogUrl, windows.second)
            windows.webBrowser.closed.connect(lambda: windows.second.show())  # 连接关闭信号到显示原窗口
            windows.webBrowser.show()
            windows.second.hide()
    except Exception as ex:
        logger.error(f'预览处理出错了：{str(ex)}')

# PDF出力
def clickedStockPDF(windows, formWidget, opreationType):
    try:
        # PDF数据
        pdfData = {}

        # 确认存放PDF文件的目录是否存在
        windows.second.pdf_dir = f'{dir_path}/PDF'
        if not os.path.exists(windows.second.pdf_dir):
            os.makedirs(windows.second.pdf_dir)
        logger.info(f'存放PDF文件的目录: [{windows.second.pdf_dir}]存在！！！')

        # 全行业数据取得
        if windows.ChartSuoShuHangYe == 'all':
            pdfPageTitle = "涨停主题数据"
            pdfFileName = f"{windows.second.pdf_dir}/DL_{pdfPageTitle}_{DateTimeUtils.nowDateTime().strftime('%Y%m%d')}.pdf"
            for indexNo in windows.pandasSortData.index:
                # 所属行业名称取得
                sshy = windows.pandasSortData.loc[indexNo, '涨停主题']
                # PDF数据编辑
                pdfData.update(editPdfData(windows, formWidget, sshy))
        else:
            pdfFileName = f"{windows.second.pdf_dir}/DL_{windows.ChartSuoShuHangYe}_{DateTimeUtils.nowDateTime().strftime('%Y%m%d')}.pdf"
            pdfPageTitle = f"{windows.ChartSuoShuHangYe}行业数据"
            # PDF数据编辑
            pdfData.update(editPdfData(windows, formWidget, windows.ChartSuoShuHangYe))

        logger.info(f'表格数据: {pdfData}')
        pdf_builder = ComplexLayoutPDF(windows.pdfPngFile, '涨停板情报', pdfPageTitle, pdfFileName, formWidget.passKey, pdfData)
        pdf_builder.build_document()
        # 预览
        if opreationType == 'Preview':
            windows.browserPrinterDialogUrl = pdfFileName
            # pageTwo(windows, formWidget, pdfFileName, 'Pdf')
    except Exception as Ex:
        logger.error(f'涨停板 PDF出力错误: {Ex}')

# PDF数据编辑
def editPdfData(windows, formWidget, sshy):
    # 表格header
    tableHeader = ['交易日期', '股票No', '股票名称', '最新价(元)', '连板/炸板数', '风险种类', '换手率(%)', 'L封板时间']

    # 设定项目值显示
    showHeaderLables = [0, 2, 3, 5, 6, 7, 8, 11, 13]
    # PDF数据
    pdfData = {}

    # 表格数据
    table_data = [tableHeader]
    conditionData = windows.pandasSortData[windows.pandasSortData['涨停主题'] == sshy].DATA.to_frame()
    suoShuHangYeInfoPandas = pandas.DataFrame(conditionData.values.T[0][0],
                                              columns=conditionData.values.T[0][0].columns)

    # 最新价(元) 降序 SQL中已经降序了，这里无需排列
    # sortStockNos = suoShuHangYeInfoPandas.sort_values(by=['最新价(元)'], ascending=True)

    # 行
    for nomber in suoShuHangYeInfoPandas.index:
        # 列
        table_row = [str(suoShuHangYeInfoPandas.iloc[nomber, value]) for value in showHeaderLables]
        # 2025-06-16 转 2025/06/16
        table_row[0] = datetime.datetime.strptime(table_row[0], '%Y-%m-%d').strftime('%Y/%m/%d')
        table_row_new = []
        for index, value in enumerate(table_row):
            # 风险种类编辑
            if index == 4:
                # '连板数' + '炸板次数' = '连板/炸板数'
                lbzbcount = f'{table_row[4]}/{table_row[5]}'
                table_row_new.append(lbzbcount)
            elif index == 5:
                continue
            else:
                table_row_new.append(table_row[index])

        table_data.append(table_row_new)

    pdfData[f'{sshy}一共有 {len(table_data) - 1}件'] = table_data

    return pdfData

# 打印
def handlerPrint(windows, formWidget):
    try:
        windows.webBrowser = FunctionMW(windows.browserPrinterDialogUrl, windows.second)
        windows.webBrowser.handlePrintRequest()  # 直接调用打印方法
    except Exception as ex:
        logger.error(f'打印处理出错了：{str(ex)}')