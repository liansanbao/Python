# _*_ coding: utf-8 _*_
# @Time : 2025/9/23 星期二 16:23
# @Author : 韦丽
# @Version: V 1.0
# @File : RowMenuAction.py
# @desc : 表行右击菜单画面
import datetime

from PyQt6.QtCore import Qt
from PyQt6 import QtGui
from PyQt6.QtGui import QIcon, QPixmap, QStandardItemModel, QStandardItem, QAction
from PyQt6.QtWidgets import QMainWindow, QStatusBar, QMessageBox, QHeaderView, QAbstractItemView, QMenu

from WLW.Tools.LoggingEx import logger
from WLW.Ui_fund import Ui_FundWindow
from WLW.model import IncreaseFiveModel

# 创建机构持股详情菜单
def create_menu(reportDate, stockNo, stockName, holdingDate, hyname, zhangtingTitle, index, qPoint, windows):
    # 创建美化后的菜单
    menu = QMenu()
    # 设置菜单样式
    menu.setStyleSheet(
        """
            QMenu {background-color: #f5f5f5; border: 1px solid #d9d9d9; border-radius: 4px; font-family: 'Segoe UI'; }
            QMenu::item { padding: 6px 24px; }
            QMenu::item:selected { background-color: #3a7bd5; color: white; }
        """
    )

    # 添加带图标的动作
    edit_action = QAction("机构持股详情", menu)
    # edit_action.setToolTip("查看机构持股明细")
    edit_action.setData(index.row())
    menu.addAction(edit_action)

    # stock_action = None
    # # 个股名称
    # if stockName:
    #     # 添加分隔线
    #     menu.addSeparator()
    #
    #     # 添加其他菜单项
    #     stock_action = QAction(f"{stockName}详情", menu)
    #     menu.addAction(stock_action)
    #
    # # 行业名称
    # if hyname:
    #     # 添加分隔线
    #     menu.addSeparator()
    #
    #     # 添加其他菜单项
    #     export_action = QAction(f"{hyname}详情", menu)
    #     menu.addAction(export_action)
    #
    # # 涨停主题
    # if zhangtingTitle:
    #     # 添加分隔线
    #     menu.addSeparator()
    #
    #     # 添加其他菜单项
    #     export_action = QAction(f"{zhangtingTitle}详情", menu)
    #     menu.addAction(export_action)

    # 显示菜单
    action = menu.exec(qPoint)

    # 处理机构持股详情菜单动作
    if action == edit_action:
        show_fundPage(reportDate, stockNo, stockName, holdingDate, windows)
    # 个股详情菜单动作
    # elif action == stock_action:
    #     print('个股详情菜单动作')
    #     show_capital()

# 分类显示
def show_capital():
    try:
        pass
    except Exception as ex:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.NoIcon)
        msg.setWindowTitle('机构持股')
        msg.setWindowIcon(QtGui.QIcon("_internal/image/fund.svg"))
        msg.setText(f'详情发生错误了：{str(ex)}')
        # 设置消息框大小
        msg.setFixedSize(800, 800)  # 宽度800像素，高度800像素
        # 添加确定按钮
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
        logger.error('show_menu:' + str(ex))

# 机构持股详情菜单动作
def show_fundPage(reportDate, stockNo, stockName, holdingDate, windows):
    try:
        windows.fundWindow = QMainWindow()
        windows.fundDialog = Ui_FundWindow()
        windows.fundDialog.setupUi(windows.fundWindow)

        # windows.fundDialog.page_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        windows.fundWindow.setWindowTitle(f"{stockName}({stockNo})机构持股明细")

        # 持股机构设定
        windows.fundDialog.fund_cb.clear()
        windows.fundDialog.fund_cb.addItems(
            ['全部', '基金', '保险', 'QFII', '社保', '券商', '私募', '信托', '财务公司', '年金', '银行', '一般法人', '特殊法人', '北上资金'])
        windows.fundDialog.fund_cb.setCurrentIndex(0)
        windows.fundDialog.fund_cb.setMinimumHeight(26)
        windows.fundDialog.fund_cb.currentIndexChanged.connect(
            lambda index: on_fund_selection_change(windows.fundDialog.fund_cb.itemText(index), reportDate, stockNo, windows))

        # 报告日期设定
        year = datetime.datetime.now().year
        report_cb = [f'{(year - 1)}-12-31', f'{year}-03-31', f'{year}-06-30', f'{year}-09-30', f'{year}-12-31']
        windows.fundDialog.report_cb.clear()
        windows.fundDialog.report_cb.addItems(report_cb)
        windows.fundDialog.report_cb.setCurrentIndex(report_cb.index(reportDate))
        windows.fundDialog.report_cb.setMinimumHeight(26)
        windows.fundDialog.report_cb.currentIndexChanged.connect(
            lambda index: on_report_selection_change(windows.fundDialog.report_cb.itemText(index), stockNo, windows))

        icon = QIcon()
        icon.addPixmap(QPixmap("_internal/image/fund.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        windows.fundWindow.setWindowIcon(icon)

        # 窗体固定大小， 最大化无效
        windows.fundWindow.setWindowFlags(
            Qt.WindowType.Window | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.MSWindowsFixedSizeDialogHint);
        # 关闭窗口右下角拖动按钮
        windows.fundWindow.setStatusBar(QStatusBar().setSizeGripEnabled(False))

        # 机构数据采集日期
        windows.fundDialog.create_date = f'采集时间：{holdingDate}'

        # 持股机构总览
        institution_holding_detail(reportDate, stockNo, windows)

        # 持仓机构明细
        position_holding_detail(reportDate, stockNo, windows)

        # 新增关闭事件处理
        def handle_close_event():
            windows.fundWindow.hide()  # 隐藏当前窗口
            windows._LWLW__mainWindow.show()  # 恢复主窗口显示

        # 绑定三种关闭方式
        windows.fundWindow.closeEvent = lambda e: handle_close_event()  # 点击关闭按钮

        windows.fundWindow.setWindowModality(Qt.WindowModality.ApplicationModal)  # 阻塞所有窗口操作
        windows.fundWindow.show()
        windows._LWLW__mainWindow.hide()  # 隐藏主窗口显示
    except Exception as ex:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.NoIcon)
        msg.setWindowTitle(f"{stockName}({stockNo})机构持股")
        msg.setWindowIcon(QtGui.QIcon("_internal/image/fund.svg"))
        msg.setText(f"{stockName}({stockNo})机构持股详情发生错误了：{str(ex)}")
        # 设置消息框大小
        msg.setFixedSize(800, 800)  # 宽度800像素，高度800像素
        # 添加确定按钮
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
        logger.error('show_menu:' + str(ex))

def on_report_selection_change(selected_text, stockNo, windows):
    # 获取持仓机构数据
    getPosition_holding_detail(selected_text, stockNo, '全部', windows)
    # 持股机构总览
    institution_holding_detail(selected_text, stockNo, windows)

def on_fund_selection_change(selected_text, reportDate, stockNo, windows):
    # 获取持仓机构数据
    getPosition_holding_detail(reportDate, stockNo, selected_text, windows)

# 持仓机构明细
def position_holding_detail(reportDate, stockNo, windows):
    # 获取持仓机构数据
    getPosition_holding_detail(reportDate, stockNo, '', windows)
    # 持仓机构数据显示设定
    setingTable(windows.fundDialog.phdetail, 'Phdetail')

# 持股机构总览
def institution_holding_detail(reportDate, stockNo, windows):
    # 获取持股机构总览数据
    getInstitution_holding_detail(reportDate, stockNo, windows)
    # 持股机构总览数据显示设定
    setingTable(windows.fundDialog.ihdetail, 'Ihdetail')

# 获取持仓机构数据
def getPosition_holding_detail(reportDate, stockNo, institutionType, windows):
    try:
        # ListView model 4Row 3 coloumn
        windows.ihdetailModel = QStandardItemModel(0, 5)
        # 创建行标题
        windows.ihdetailModel.setHorizontalHeaderLabels(
            ['机构属性', '机构数量', '持仓数量(万股)', '持仓市值(万元)', '占总股本比%', '占已流通A股比%'])

        # 设定项目值显示
        showHeaderLables = [3, 4, 5, 6, 7, 8]

        result = IncreaseFiveModel.getPositionHoldingDetail(reportDate, stockNo, institutionType)

        for item in result:
            windows.ihdetailModel.appendRow(
                [QStandardItem(str(item[value])) for value in showHeaderLables])

        windows.fundDialog.phdetail.setModel(windows.ihdetailModel)
    except Exception as ex:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.NoIcon)
        msg.setWindowTitle('机构持股')
        msg.setWindowIcon(QtGui.QIcon("_internal/image/fund.svg"))
        msg.setText(f'发送错误了：{str(ex)}')
        # 设置消息框大小
        msg.setFixedSize(800, 800)  # 宽度800像素，高度800像素
        # 添加确定按钮
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
        logger.error('getPosition_holding_detail:' + str(ex))

# 获取持股机构总览数据
def getInstitution_holding_detail(reportDate, stockNo, windows):
    # ListView model 4Row 3 coloumn
    windows.ihdetailModel = QStandardItemModel(0, 5)
    # 创建行标题
    windows.ihdetailModel.setHorizontalHeaderLabels(
        ['机构属性', '机构数量', '持仓数量(万股)', '持仓市值(万元)', '占总股本比%', '占已流通A股比%'])

    # 设定项目值显示
    showHeaderLables = [3, 4, 5, 6, 7, 8]

    result = IncreaseFiveModel.getInstitutionHoldingDetail(reportDate, stockNo)

    for item in result:
        windows.ihdetailModel.appendRow(
            [QStandardItem(str(item[value])) for value in showHeaderLables])

    windows.fundDialog.ihdetail.setModel(windows.ihdetailModel)

def setingTable(tableView, funcType):
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
    tableView.horizontalHeader().setSectionsClickable(True)  # 设置列头可点击（可选）
    tableView.verticalHeader().setSectionsClickable(True)  # 设置行头可点击（可选）
    tableView.horizontalHeader().setSectionsMovable(True)  # 设置列头可移动（可选）
    tableView.verticalHeader().setSectionsMovable(True)  # 设置行头可移动（可选）
    tableView.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置列头文本居中显示（可选）
    tableView.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置行头文本居中显示（可选）
    # 列设置保持可调整（默认状态）
    tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    # 设置行交替
    tableView.setAlternatingRowColors(True)

    # 禁止编辑
    tableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    # 设置列宽 1458
    if funcType == 'Phdetail':
        tableView.setColumnWidth(0, 548)
        tableView.setColumnWidth(1, 100)
        tableView.setColumnWidth(2, 120)
        tableView.setColumnWidth(3, 120)
        tableView.setColumnWidth(4, 160)
        tableView.setColumnWidth(5, 200)
    elif funcType == 'Ihdetail':
        tableView.setColumnWidth(0, 198)
        tableView.setColumnWidth(1, 200)
        tableView.setColumnWidth(2, 180)
        tableView.setColumnWidth(3, 180)
        tableView.setColumnWidth(4, 210)
        tableView.setColumnWidth(5, 300)

    # 启用数据排序和过滤
    tableView.setSortingEnabled(True)
    # 设置表格为整行选择 QAbstractItemView.SelectionBehavior(1) 单元格选中：QAbstractItemView.SelectionBehavior(0) 列选中：QAbstractItemView.SelectionBehavior(2)
    tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior(1))

    # 获取列宽 用来手动调节每列列宽
    # tableView.horizontalHeader().sectionResized.connect(
    #     lambda index, old_size, new_size: print(f"列{index}宽度变为{new_size}"))
