# _*_ coding: utf-8 _*_
# @Time : 2026/1/21 星期三 15:41
# @Author : 韦丽
# @Version: V 1.0
# @File : NoticesAction.py
# @desc : A股公告显示处理
import os
from functools import partial

from PyQt6 import QtGui
from PyQt6.QtCore import QDate, QUrl
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QTreeView, QAbstractItemView, QMessageBox

from WLW.StockBase import DateTimeUtils
from WLW.Tools.CommonUtils import format_string, setQStandardItem
from WLW.Tools.LoggingEx import logger
from WLW.action.WebEngineViewEx import WebEngineView
from WLW.model import NoticeInfoModel
from WLW.model.NoticeInfoCondition import NoticesInfoCondition

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)

# 获取所在文件夹路径
dir_path = str(os.path.dirname(script_path))

dir_path = dir_path.replace('\\', '/')

# 画面初期设定
def noticesInitContent(windows, formWidget):
    # 股票No、股票名称、连板数、换手率、涨停次数、所属行业、炸板次数、涨停主题、最新价输入框空白设定
    formWidget.notice_stockNo.setText('')
    # formWidget.notice_stockNo.setIntegerOnly()
    # 设置只能输入6位0-9的数字
    formWidget.notice_stockNo.setNumberWithRange(6)
    formWidget.notice_stockName.setText('')
    # 总件数format
    formWidget.notice_count_number.setText(f'一共 0 件数据')
    # browser窗口
    formWidget.stockInfoBrowser = None

    # 当前周開始日取得
    weekFromDay = DateTimeUtils.Week_Day_Date(weekDay=1)
    # 当前周终了日取得
    # weekToDay = DateTimeUtils.Week_Day_Date(weekDay=5)

    # 交易日期From 显示格式
    formWidget.notice_saleDateFrom.setDate(QDate(weekFromDay.year, weekFromDay.month, weekFromDay.day))
    # 交易日期From 可选最大日期
    formWidget.notice_saleDateFrom.setMaximumDate(QDate.currentDate().addDays(0))
    # 交易日期From 可选最小日期
    # formWidget.notice_saleDateFrom.setMinimumDate(QDate.currentDate().addDays(-30))
    # 交易日期From 日历控件弹出
    formWidget.notice_saleDateFrom.setCalendarPopup(True)

    # 交易日期To 显示格式
    formWidget.notice_saleDateTo.setDate(QDate.currentDate())
    # 交易日期To 可选最大日期
    formWidget.notice_saleDateTo.setMaximumDate(QDate.currentDate().addDays(0))
    # 交易日期To 可选最小日期
    # formWidget.notice_saleDateTo.setMinimumDate(QDate.currentDate().addDays(-30))
    # 交易日期To 日历控件弹出
    formWidget.notice_saleDateTo.setCalendarPopup(True)

# 事件绑定 注意参数传递:在这里functools.partial(方法名, 参数1, 参数2) 在主程序里就是方法名
def noticesActionSetting(windows, formWidget):
    # 事件绑定 -- 检索
    formWidget.notice_stockSubmit.clicked.connect(partial(AddClickedNoticSubmit, windows, formWidget))
    # 事件绑定 -- 清除
    formWidget.notice_stockClear.clicked.connect(partial(AddClickedNoticClear, windows, formWidget))
    # 事件绑定 -- 投资
    formWidget.notice_myself.clicked.connect(partial(AddClickedNoticeMyself, windows, formWidget))

# 事件绑定 -- 投资
def AddClickedNoticeMyself(windows, formWidget):
    try:
        if windows.myself == '':
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle('消息提示')
            msg.setWindowIcon(QtGui.QIcon("_internal/image/wlw.svg"))
            msg.setText(f'[{windows.parentPath}/config/config.ini]文件中， “投资”值没有设定！')
            # 设置消息框大小
            msg.setFixedSize(400, 200)  # 宽度400像素，高度200像素
            # 添加确定按钮
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            return

        # browser窗口初期化
        initBrowser(formWidget)
        # 数据绑定
        editNoticeTable(windows, formWidget, 'M')
        # 股票No、股票名称、连板数、换手率、涨停次数、所属行业、炸板次数、涨停主题、最新价输入框空白设定
        formWidget.notice_stockNo.setText('')
        # formWidget.notice_stockNo.setIntegerOnly()
        # 设置只能输入6位0-9的数字
        formWidget.notice_stockNo.setNumberWithRange(6)
        formWidget.notice_stockName.setText('')
    except Exception as ex:
        logger.error(f'事件绑定 -- 投资处理出错了：{str(ex)}')

# TreeView行选择事件
def onSelectionChanged(windows, formWidget):
    try:
        indexes = formWidget.noticeCapitalTree.selectionModel().selectedIndexes()  # 获取当前选中的索引列表
        if indexes:
            index = indexes[len(indexes) - 1]  # 只处理第一个索引，通常是顶层索引
            stockNo = formWidget.noticeCapitalTree.model().itemFromIndex(index).text()
            # 行业还是个股
            if stockNo == '':
                pass
            else:
                # 公告详情URL显示
                stockReportchartUrls = formWidget.noticeCapitalTree.model().itemFromIndex(indexes[2]).text()
                showWebDataUrl(formWidget, stockReportchartUrls)
    except Exception as ex:
        logger.error(f'TreeView行选择处理出错了：{str(ex)}')

# （数据、F10、可视化报告）URL
def showWebDataUrl(formWidget, dataUrl):
    # browser窗口初期化
    initBrowser(formWidget)
    # 创建web引擎视图
    formWidget.stockInfoBrowser = WebEngineView()
    formWidget.stockInfoBrowser.load(QUrl(dataUrl))
    formWidget.verticalLayout.addWidget(formWidget.stockInfoBrowser)
    formWidget.verticalLayoutWidget.show()
    formWidget.verticalStackedWidget.setCurrentIndex(1)

# browser窗口初期化
def initBrowser(formWidget):
    if formWidget.stockInfoBrowser:
        formWidget.verticalLayout.removeWidget(formWidget.stockInfoBrowser)
        formWidget.stockInfoBrowser.deleteLater()  # 安全删除对象
        formWidget.stockInfoBrowser = None  # 清除引用

# 事件绑定 -- 检索
def AddClickedNoticSubmit(windows, formWidget):
    # browser窗口初期化
    initBrowser(formWidget)
    # 数据绑定
    editNoticeTable(windows, formWidget)

# TreeView设定
def initMCDTreeView(windows, formWidget):
    treeModel = QStandardItemModel()
    treeModel.setHorizontalHeaderLabels(['公告类型(总数)/公告标题', 'hidden', 'hidden', 'hidden', 'hidden', 'hidden', 'hidden', 'hidden', 'hidden'])
    rootItem = treeModel.invisibleRootItem()
    windows.pandasSortData = NoticeInfoModel.editNoticeTypeAndSort(windows.showNoticeData, formWidget)
    for indexNo in windows.pandasSortData.index:
        sshy = windows.pandasSortData.loc[indexNo, '公告类型']
        sshy = '无类型' if sshy == '' else sshy
        sshy = format_string(sshy, 10)
        suoShuHangYeQS_total = str(windows.pandasSortData.loc[indexNo, '数量'])
        suoShuHangYeQS = setQStandardItem(f'{sshy}　　({suoShuHangYeQS_total})件', f'{sshy}　　({suoShuHangYeQS_total})件')
        stockNames = windows.pandasSortData.loc[indexNo, '股票名称']
        noticeTitles = windows.pandasSortData.loc[indexNo, '公告标题']
        stockNoticeUrl = windows.pandasSortData.loc[indexNo, '公告详情']
        stockInfoDatas = windows.pandasSortData.loc[indexNo, '股票code']
        for stockNo in stockInfoDatas:
            suoShuHangYeQS.appendRow(
                [setQStandardItem(stockNames[stockNo], noticeTitles[stockNo]),
                 QStandardItem(stockNames[stockNo]),
                 QStandardItem(stockNoticeUrl[stockNo]),
                 QStandardItem(''),
                 QStandardItem(''),
                 QStandardItem(''),
                 QStandardItem(''),
                 QStandardItem(''),
                 QStandardItem(stockNo)])
        rootItem.appendRow([suoShuHangYeQS])

    formWidget.noticeCapitalTree.setModel(treeModel)
    formWidget.noticeCapitalTree.setColumnWidth(0, 240)
    formWidget.noticeCapitalTree.setColumnWidth(1, 7)
    formWidget.noticeCapitalTree.setColumnWidth(2, 7)
    formWidget.noticeCapitalTree.setColumnWidth(3, 7)
    formWidget.noticeCapitalTree.setColumnWidth(4, 7)
    formWidget.noticeCapitalTree.setColumnWidth(5, 7)
    formWidget.noticeCapitalTree.setColumnWidth(6, 7)
    formWidget.noticeCapitalTree.setColumnWidth(7, 7)
    formWidget.noticeCapitalTree.setColumnWidth(8, 7)
    # 将第五至九列隐藏
    formWidget.noticeCapitalTree.setColumnHidden(1, True)
    formWidget.noticeCapitalTree.setColumnHidden(2, True)
    formWidget.noticeCapitalTree.setColumnHidden(3, True)
    formWidget.noticeCapitalTree.setColumnHidden(4, True)
    formWidget.noticeCapitalTree.setColumnHidden(5, True)
    formWidget.noticeCapitalTree.setColumnHidden(6, True)
    formWidget.noticeCapitalTree.setColumnHidden(7, True)
    formWidget.noticeCapitalTree.setColumnHidden(8, True)
    # 禁止拖动
    formWidget.noticeCapitalTree.setDragEnabled(False)
    formWidget.noticeCapitalTree.setAcceptDrops(False)
    # 设置单选模式
    formWidget.noticeCapitalTree.setSelectionMode(QTreeView.SelectionMode.SingleSelection)
    formWidget.noticeCapitalTree.setAnimated(True)
    # 禁止编辑
    formWidget.noticeCapitalTree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    # 获取根节点
    root = treeModel.invisibleRootItem()

    # 如果存在子节点，选中第一行
    if root.rowCount() > 0:
        first_child = root.child(0)
        # 选中第一行
        index = treeModel.indexFromItem(first_child)
        formWidget.noticeCapitalTree.setCurrentIndex(index)
        # 展开第一行
        formWidget.noticeCapitalTree.expand(index)

        # 展开后选中第一行的子项
        if first_child.rowCount() > 0:
            first_grandchild = first_child.child(0)
            grandchild_index = treeModel.indexFromItem(first_grandchild)
            formWidget.noticeCapitalTree.setCurrentIndex(grandchild_index)
            # 公告详情
            onSelectionChanged(windows, formWidget)

    # 设置行选择颜色 (新增部分)
    selection_color = "#2a82da"  # 选择时的蓝色背景
    hover_color = "#ddeeff"  # 鼠标悬停时的浅蓝色
    text_color = "#ffffff"  # 选择时的白色文字

    formWidget.noticeCapitalTree.setStyleSheet(f"""
                        QTreeView::item:selected {{
                            background-color: {selection_color};
                            color: {text_color};
                        }}
                        QTreeView::item:hover {{
                            background-color: {hover_color};
                        }}
                        QTreeView {{
                            border: 1px solid #000000; /* 设置边框宽度为1像素，样式为实线，颜色为黑色 */
                        }}
                        QTreeView::item {{
                            border: 1px solid #d9d9d9; /* 设置每个item的边框 */
                            padding: 2px; /* 可选：设置内边距 */
                        }}
                    """)

# 数据绑定
def editNoticeTable(windows, formWidget, optionType: str = 'S'):
    # 公告Tab--数据绑定
    getNoticeData(windows, formWidget, optionType)
    # TreeView设定
    initMCDTreeView(windows, formWidget)
    # TreeView行选择事件
    formWidget.noticeCapitalTree.selectionModel().selectionChanged.connect(
        partial(onSelectionChanged, windows, formWidget))

# 公告Tab--数据绑定
def getNoticeData(windows, formWidget, optionType):
    # 检索条件获取
    # 交易日期From
    saleDayFrom = DateTimeUtils.Format_changed(formWidget.notice_saleDateFrom.text(), '%Y年%M月%d日', '%Y%M%d')
    # 交易日期To
    saleDayTo = DateTimeUtils.Format_changed(formWidget.notice_saleDateTo.text(), '%Y年%M月%d日', '%Y%M%d')
    # 股票No
    stockNo = formWidget.notice_stockNo.text()
    # 股票名称
    stockName = formWidget.notice_stockName.text()

    # 排序选项
    orderByOption = 'ORDER BY SIW.NOTICE_DATE DESC'
    # 检索条件设定
    if optionType == 'M':
        stockNo = windows.myself

    noticsInfoCondition = NoticesInfoCondition(saleDayFrom, saleDayTo, stockNo, stockName, optionType, orderByOption)
    # 数据检索;
    windows.showNoticeData = NoticeInfoModel.getNoticeInfoData(noticsInfoCondition)

    # 总件数format
    formWidget.notice_count_number.setText(f'一共 {len(windows.showNoticeData)} 件数据')

# 事件绑定 -- 清除按钮事件
def AddClickedNoticClear(windows, formWidget):
    try:
        # browser窗口初期化
        initBrowser(formWidget)
        clear_tree_view(formWidget.noticeCapitalTree)
        noticesInitContent(windows, formWidget)
    except Exception as ex:
        logger.error(f'清除处理出错了：{str(ex)}')

def clear_tree_view(tree_view):
    """
    清空QTreeView中的所有节点
    """
    model = tree_view.model()
    if model is not None:
        model.removeRows(0, model.rowCount())