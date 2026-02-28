# _*_ coding: utf-8 _*_
# @Time : 2025/8/23 星期六 10:17
# @Author : 韦丽
# @Version: V 1.0
# @File : IncreaseFiveAction.py
# @desc : 涨幅(5%)以上Tab数据处理
# 禁用metrics收集
import copy
from functools import partial
from typing import Dict, Any

import pandas
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *   # 从 PyQt6 中导入所需的类

from WLW.StockBase.DateTimeUtils import get_quarter_dates, lastTradingDaysFromIncreaseFive
from WLW.Tools.CommonUtils import setQStandardItem
from WLW.Tools.LoggingEx import logger
from WLW.action.MultiIncreaseSortProxyModel import CustomProxyModel
from WLW.action.RowMenuAction import create_menu
from WLW.model import IncreaseFiveModel
from WLW.model.IncreaseFiveCondition import IncreaseFiveCondition

# 涨幅(5%)以上Tab(初期化)
def increaseFiveInitContent(windows, formWigdet):
    try:
        # 股票No、股票名称、涨幅、现价、所属行业输入框空白设定
        formWigdet.lncrease_stockNo.setText('')
        # 设置只能输入6位0-9的数字
        formWigdet.lncrease_stockNo.setNumberWithRange(6)
        formWigdet.lncrease_stockName.setText('')
        formWigdet.lncrease_hangYe.setText('')
        formWigdet.lncrease_xianJia.setText('')

        # 现价检索条件设定
        formWigdet.lncrease_condition_xj.clear()
        formWigdet.lncrease_condition_xj.addItems(['=', '>', '<'])
        formWigdet.lncrease_condition_xj.setCurrentIndex(0)
        formWigdet.lncrease_condition_xj.setMinimumHeight(26)

        # 风险种类 '全部'设定
        formWigdet.lncrease_stockType.clear()
        formWigdet.lncrease_stockType.addItems(
            ['全部', '频发风险', '触发风险', '商誉风险', '近期解禁', '退市风险', '立案调查', '无风险'])
        formWigdet.lncrease_stockType.setCurrentIndex(7)
        formWigdet.lncrease_stockType.setMinimumHeight(26)

        # 最近N个交易日
        formWigdet.lncrease_condition_zj.clear()
        formWigdet.lncrease_condition_zj.addItems(
            ['5个交易日', '10个交易日', '20个交易日', '60个交易日', '120个交易日', '250个交易日'])
        formWigdet.lncrease_condition_zj.setCurrentIndex(0)
        formWigdet.lncrease_condition_zj.setMinimumHeight(26)

        # 最近5,10,20个交易日日期取得：{'0': {'from': 19/9, 'to': 25/9}, '1':{'from': 12/9, 'to': 25/9}, '2':{'from': 29/8, 'to': 25/9} }
        windows.lastTradingDays = lastTradingDaysFromIncreaseFive()

        # 上一页
        upIcon = QIcon()
        upIcon.addPixmap(QPixmap("_internal/image/upPage.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        formWigdet.uplncreasePage.setIcon(upIcon)
        # 下一页
        nextIcon = QIcon()
        nextIcon.addPixmap(QPixmap("_internal/image/nextPage.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        formWigdet.nextlncreasePage.setIcon(nextIcon)

        # 设置行右键菜单功能
        if formWigdet.passKey == 'WLW':
            formWigdet.lncrease_showStockTable.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            formWigdet.lncrease_showStockTable.customContextMenuRequested.connect(
                lambda pos: show_menu(pos, windows, formWigdet))
    except Exception as ex:
        logger.error(f'初期处理出错了：{str(ex)}')

# 表格行右键菜单
def show_menu(pos, windows, formWigdet):
    try:
        index = formWigdet.lncrease_showStockTable.indexAt(pos)
        # 获取当前行所有列的值
        model = formWigdet.lncrease_showStockTable.model()
        # print(f'model: {model.rowCount()}')
        # 持股机构数
        institutionCount = int(model.index(index.row(), 17).data())
        # 鼠标单击行焦点取得
        qPoint = formWigdet.lncrease_showStockTable.viewport().mapToGlobal(pos)

        if index.isValid() and institutionCount > 0:
            # 以交易日期转换成机构持股报告日期
            reportDate = get_quarter_dates("%Y-%m-%d", model.index(index.row(), 2).data(), "%Y-%m-%d")["end_date"]
            # 获取股票代码
            stockNo = model.index(index.row(), 0).data()
            # 获取股票名称
            stockName = model.index(index.row(), 1).data()
            # 数据采集日期
            holdingDate = model.index(index.row(), 20).data()
            # 调用机构持股详细画面
            create_menu(reportDate, stockNo, stockName, holdingDate, '', '', index, qPoint, windows)
    except Exception as ex:
        logger.error(f'右击菜单处理出错了：{str(ex)}')

# 涨幅(5%)以上(事件绑定)
def increaseFiveActionSetting(windows, formWigdet):
    # 事件绑定 -- 检索
    formWigdet.lncrease_stockSubmit.clicked.connect(partial(AddClickedIncreaseStockSubmit, windows, formWigdet))
    # 事件绑定 -- 清除
    formWigdet.lncrease_stockClear.clicked.connect(partial(AddClickedIncreaseClear, windows, formWigdet))
    # 事件绑定 -- 上一页
    formWigdet.uplncreasePage.clicked.connect(partial(AddClickedIncreasePage, 'up', windows, formWigdet))
    # 事件绑定 -- 下一页
    formWigdet.nextlncreasePage.clicked.connect(partial(AddClickedIncreasePage, 'next', windows, formWigdet))

# 事件绑定 -- 翻页处理
def AddClickedIncreasePage(type, windows, formWigdet):
    try:
        if type == 'up':
            windows.current_IncreaseFivePage -= 1
        elif type == 'next':
            windows.current_IncreaseFivePage += 1
        # 分页处理
        data = get_page(windows.reportData, windows.current_IncreaseFivePage, 20)
        # 数据显示处理
        showTableData(data, windows, formWigdet)
        # 表格设定
        setingTable(formWigdet.lncrease_showStockTable)
    except Exception as ex:
        logger.error(f'翻页处理出错了：{str(ex)}')

# 事件绑定 -- 检索
def AddClickedIncreaseStockSubmit(windows, formWigdet):
    try:
        editIncreaseFiveTable(windows, formWigdet)
    except Exception as ex:
        logger.error(f'检索处理出错了：{str(ex)}')

# 涨幅(5%)以上--数据绑定
def editIncreaseFiveTable(windows, formWigdet):
    # 涨幅(5%)以上Tab--数据绑定
    getIncreaseFiveData(windows, formWigdet)
    # 涨幅(5%)以上Tab--数据显示设定
    setingTable(formWigdet.lncrease_showStockTable)

# 数据处理
def editIncreaseFiveData(showIncreaseFiveData, windows, formWigdet):
    resultData = []
    formWigdet.combox_sale_lncrease.clear()
    formWigdet.combox_zf_lncrease.clear()
    formWigdet.combox_sp_lncrease.clear()
    formWigdet.combox_plate_lncrease.clear()

    # 检索数据再次处理
    if showIncreaseFiveData:
        pandasData = pandas.DataFrame(data=showIncreaseFiveData, columns=['交易日期', '所属行业', '股票No', '名称', '涨幅', '现价(元)', '风险种类', '涨跌额', '成交量(手)', '成交额', '振幅', '换手率', '市盈率（动态）',
             '量比', '涨停主题', '概念', '涨停原因', '机构持股数量', 'DEPTH', 'F10URL', 'REPORT', 'hidden'])
        groupStockNo = (pandasData.sort_values('交易日期', ascending=False).groupby(by='所属行业'))
        groupSale = (pandasData.sort_values('交易日期', ascending=False).groupby(by='交易日期'))
        groupSale = ["全部"] + sorted([key for key, value in groupSale], reverse=True)
        # 数据栏检索条件处理 STR
        windows.zhangfuIncreaseConditionAdd = [0]
        windows.zhangfuCombox = [' 全部', ' 4% 至  9%', ' 9% 至 11%', '11% 至 19%', '19% 至 20%', '20% 以上']

        windows.gujiaIncreaseConditionAdd = [0]
        windows.gujiaCombox = ['全部', '10元 以下', '10 至 20元', '20 至 30元', '30 至 50元', '50 至 100元', '100 至 500元', '500 至 1000元', '1000元以上']

        windows.plateIncreaseCondition = []
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
            if len(windows.zhangfuIncreaseConditionAdd) != 6:
                # 检索条件涨幅生成
                createZhangFuContion(max_data, windows)
            if len(windows.gujiaIncreaseConditionAdd) != 8:
                # 检索条件股价生成
                createGuJiaContion(max_data, windows)

            # 上榜统计
            if qushi not in windows.plateIncreaseCondition:
                windows.plateIncreaseCondition.append(qushi)

            resultData.append(max_data)

        # 整数列表排序
        windows.zhangfuIncreaseConditionAdd = sorted(set(windows.zhangfuIncreaseConditionAdd))
        windows.gujiaIncreaseConditionAdd = sorted(set(windows.gujiaIncreaseConditionAdd))
        windows.plateIncreaseCondition = ["全部"] + [str(value) for value in sorted(set(windows.plateIncreaseCondition))]

        # 交易日期
        formWigdet.combox_sale_lncrease.addItems(groupSale)
        formWigdet.combox_sale_lncrease.setCurrentIndex(0)
        formWigdet.combox_sale_lncrease.setMinimumHeight(26)
        formWigdet.combox_sale_lncrease.currentIndexChanged.connect(
            lambda index: on_combox_sale_selection_change(formWigdet.combox_sale_lncrease.itemText(index), formWigdet, windows))

        # 涨幅
        formWigdet.combox_zf_lncrease.addItems([windows.zhangfuCombox[index] for index in windows.zhangfuIncreaseConditionAdd])
        formWigdet.combox_zf_lncrease.setCurrentIndex(0)
        formWigdet.combox_zf_lncrease.setMinimumHeight(26)
        formWigdet.combox_zf_lncrease.currentIndexChanged.connect(
            lambda index: on_combox_zf_selection_change(formWigdet.combox_zf_lncrease.currentIndex(), formWigdet, windows))

        # 股价
        formWigdet.combox_sp_lncrease.addItems(
            [windows.gujiaCombox[index] for index in windows.gujiaIncreaseConditionAdd])
        formWigdet.combox_sp_lncrease.setCurrentIndex(0)
        formWigdet.combox_sp_lncrease.setMinimumHeight(26)
        formWigdet.combox_sp_lncrease.currentIndexChanged.connect(
            lambda index: on_combox_sp_selection_change(formWigdet.combox_sp_lncrease.currentIndex(), formWigdet, windows))

        # 上榜统计
        formWigdet.combox_plate_lncrease.addItems(windows.plateIncreaseCondition)
        formWigdet.combox_plate_lncrease.setCurrentIndex(0)
        formWigdet.combox_plate_lncrease.setMinimumHeight(26)
        formWigdet.combox_plate_lncrease.currentIndexChanged.connect(
            lambda index: on_combox_plate_selection_change(formWigdet.combox_plate_lncrease.itemText(index), formWigdet, windows))
    return resultData

# 交易日期下拉框事件
def on_combox_sale_selection_change(itemText, formWigdet, windows):
    try:
        windows.saleText = itemText
        windows.zfCurrentIndex = formWigdet.combox_zf_lncrease.currentIndex()
        windows.spCurrentIndex = formWigdet.combox_sp_lncrease.currentIndex()
        plateIndex = formWigdet.combox_plate_lncrease.currentIndex()
        windows.plateCurrentIndex = formWigdet.combox_plate_lncrease.itemText(plateIndex)
        reportDataAgin(windows, formWigdet)
    except Exception as ex:
        logger.error(f'交易日期下拉框处理出错了：{str(ex)}')

# 涨幅下拉框事件
def on_combox_zf_selection_change(currentIndex, formWigdet, windows):
    try:
        windows.zfCurrentIndex = currentIndex
        windows.spCurrentIndex = formWigdet.combox_sp_lncrease.currentIndex()
        plateIndex = formWigdet.combox_plate_lncrease.currentIndex()
        windows.plateCurrentIndex = formWigdet.combox_plate_lncrease.itemText(plateIndex)
        index = formWigdet.combox_sale_lncrease.currentIndex()
        windows.saleText = formWigdet.combox_sale_lncrease.itemText(index)
        reportDataAgin(windows, formWigdet)
    except Exception as ex:
        logger.error(f'涨幅下拉框处理出错了：{str(ex)}')

# 股价下拉框事件
def on_combox_sp_selection_change(currentIndex, formWigdet, windows):
    try:
        windows.spCurrentIndex = currentIndex
        windows.zfCurrentIndex = formWigdet.combox_zf_lncrease.currentIndex()
        plateIndex = formWigdet.combox_plate_lncrease.currentIndex()
        windows.plateCurrentIndex = formWigdet.combox_plate_lncrease.itemText(plateIndex)
        index = formWigdet.combox_sale_lncrease.currentIndex()
        windows.saleText = formWigdet.combox_sale_lncrease.itemText(index)
        reportDataAgin(windows, formWigdet)
    except Exception as ex:
        logger.error(f'股价下拉框处理出错了：{str(ex)}')

# 上榜统计下拉框事件
def on_combox_plate_selection_change(itemText, formWigdet, windows):
    try:
        windows.plateCurrentIndex = itemText
        windows.spCurrentIndex = formWigdet.combox_sp_lncrease.currentIndex()
        windows.zfCurrentIndex = formWigdet.combox_zf_lncrease.currentIndex()
        index = formWigdet.combox_sale_lncrease.currentIndex()
        windows.saleText = formWigdet.combox_sale_lncrease.itemText(index)
        reportDataAgin(windows, formWigdet)
    except Exception as ex:
        logger.error(f'上榜统计下拉框处理出错了：{str(ex)}')

# 数据二次编辑
def reportDataAgin(windows, formWigdet):
    windows.reportData = editIncreaseFiveDataAgin(windows)

    # 总件数format
    formWigdet.lncrease_count_number.setText(f'一共 {len(windows.reportData)} 件数据')
    # 页码初始化
    windows.current_IncreaseFivePage = 1
    # 分页处理
    data = get_page(windows.reportData, windows.current_IncreaseFivePage, 20)
    # 数据显示处理
    showTableData(data, windows, formWigdet)

# 数据二次检索处理
def editIncreaseFiveDataAgin(windows):
    resultData = []

    # 检索数据再次处理
    if windows.reportDataBody:
        # 数据栏检索条件处理 END
        for max_data in windows.reportDataBody:
            # 交易日期 涨幅 股价
            if (condtionSale(max_data, windows) and condtionIncrease(max_data, windows)
                    and condtionPrice(max_data, windows)) and condtionFlate(max_data, windows):
                resultData.append(max_data)

    return resultData

# 检索条件判断 STR
def condtionSale(max_data, windows):
    if windows.saleText == '全部' or max_data[0] == windows.saleText:
        return True
    return False

def condtionIncrease(max_data, windows):
    if windows.zfCurrentIndex == 0 or windows.zfCurrentIndex == createZhangFuContion(max_data, windows):
        return True
    return False

def condtionPrice(max_data, windows):
    if windows.spCurrentIndex == 0 or windows.spCurrentIndex == createGuJiaContion(max_data, windows):
        return True
    return False

def condtionFlate(max_data, windows):
    if windows.plateCurrentIndex == '全部' or windows.plateCurrentIndex == str(max_data[21]):
        return True
    return False

# 检索条件判断 END

# 检索条件涨幅生成
def createZhangFuContion(max_data, windows):
    # 涨幅5档
    zhangfu = float(str(max_data[4]).replace('%', ''))
    if 4 <= zhangfu and zhangfu < 9:
        if 1 not in windows.zhangfuIncreaseConditionAdd:
            windows.zhangfuIncreaseConditionAdd.append(1)
        index = 1
    elif 9 <= zhangfu and zhangfu < 11:
        if 2 not in windows.zhangfuIncreaseConditionAdd:
            windows.zhangfuIncreaseConditionAdd.append(2)
        index = 2
    elif 11 <= zhangfu and zhangfu < 19:
        if 3 not in windows.zhangfuIncreaseConditionAdd:
            windows.zhangfuIncreaseConditionAdd.append(3)
        index = 3
    elif 19 <= zhangfu and zhangfu < 20:
        if 4 not in windows.zhangfuIncreaseConditionAdd:
            windows.zhangfuIncreaseConditionAdd.append(4)
        index = 4
    elif 20 <= zhangfu and zhangfu < 999:
        if 5 not in windows.zhangfuIncreaseConditionAdd:
            windows.zhangfuIncreaseConditionAdd.append(5)
        index = 5
    return index

# 检索条件股价生成
def createGuJiaContion(max_data, windows):
    # 股价8档
    gujia = float(max_data[5])
    index = 0
    if gujia <= 10:
        if 1 not in windows.gujiaIncreaseConditionAdd:
            windows.gujiaIncreaseConditionAdd.append(1)
        index = 1
    elif 10 < gujia and gujia <= 20:
        if 2 not in windows.gujiaIncreaseConditionAdd:
            windows.gujiaIncreaseConditionAdd.append(2)
        index = 2
    elif 20 < gujia and gujia < 30:
        if 3 not in windows.gujiaIncreaseConditionAdd:
            windows.gujiaIncreaseConditionAdd.append(3)
        index = 3
    elif 30 < gujia and gujia <= 50:
        if 4 not in windows.gujiaIncreaseConditionAdd:
            windows.gujiaIncreaseConditionAdd.append(4)
        index = 4
    elif 50 < gujia and gujia <= 100:
        if 5 not in windows.gujiaIncreaseConditionAdd:
            windows.gujiaIncreaseConditionAdd.append(5)
        index = 5
    elif 100 < gujia and gujia <= 500:
        if 6 not in windows.gujiaIncreaseConditionAdd:
            windows.gujiaIncreaseConditionAdd.append(6)
        index = 6
    elif 500 < gujia and gujia <= 1000:
        if 7 not in windows.gujiaIncreaseConditionAdd:
            windows.gujiaIncreaseConditionAdd.append(7)
        index = 7
    elif 1000 < gujia:
        if 8 not in windows.gujiaIncreaseConditionAdd:
            windows.gujiaIncreaseConditionAdd.append(8)
        index = 8
    return index

# 涨幅(5%)以上Tab--数据绑定
def getIncreaseFiveData(windows, formWigdet):
    # 检索条件获取
    # 最近N个交易日
    zj = formWigdet.lncrease_condition_zj.currentIndex()
    # 当前周開始日取得
    dayFromTo = windows.lastTradingDays[zj]
    # 交易日期From
    hangQingDateFrom = dayFromTo['from']
    # 交易日期To
    hangQingDateTo = dayFromTo['to']
    # 股票No
    masterStockNo = formWigdet.lncrease_stockNo.text()
    # 股票名称
    masterStockName = formWigdet.lncrease_stockName.text()
    # 所属行业
    masterHangYe = formWigdet.lncrease_hangYe.text()
    # 涨幅
    masterZhangFu = ''
    # 现价
    masterXianJia = formWigdet.lncrease_xianJia.text()
    # 风险种类
    masterStockType = formWigdet.lncrease_stockType.currentIndex()
    # 现价比较条件
    condition_xj = formWigdet.lncrease_condition_xj.currentIndex()
    # 排序选项
    orderByOption = ' ORDER BY GS.CREATE_DATE DESC'
    # 数据检索
    increaseFiveCondition = IncreaseFiveCondition(hangQingDateFrom, hangQingDateTo, masterStockNo, masterStockName, masterHangYe,
                                                masterZhangFu, masterXianJia, masterStockType, condition_xj, 'D', orderByOption)
    # 添加数据;
    windows.showIncreaseFiveData = IncreaseFiveModel.getIncreaseFiveWLWData(increaseFiveCondition)
    # 数据处理
    windows.reportData = editIncreaseFiveData(windows.showIncreaseFiveData, windows, formWigdet)
    windows.reportDataBody = copy.deepcopy(windows.reportData)
    # 总件数format
    formWigdet.lncrease_count_number.setText(f'一共 {len(windows.reportData)} 件数据')
    # 页码初始化
    windows.current_IncreaseFivePage = 1
    # 分页处理
    data = get_page(windows.reportData, windows.current_IncreaseFivePage, 20)
    # 数据显示处理
    showTableData(data, windows, formWigdet)

# 数据显示处理
def showTableData(data, windows, formWigdet):
    # ListView model 4Row 3 coloumn
    windows.increaseFive = QStandardItemModel(0, 21)
    # 创建行标题
    windows.increaseFive.setHorizontalHeaderLabels(
        ['股票No', '名称', '交易日期', '所属行业', '涨幅', '现价(元)', '风险种类', '涨跌额', '成交量(手)', '成交额',
         '振幅', '换手率', '市盈率',
         '量比', '涨停主题', '概念', '涨停原因', '机构数', '上榜次数', '首次交易日', 'hidden'])
    # 设定项目值显示
    showHeaderLables = [2, 3, 0, 1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 21, 22, 23]
    if data['data']:
        for row, item in enumerate(data['data']):
            windows.increaseFive.appendRow([setQStandardItem(str(item[value]), str(item[value])) for value in showHeaderLables])
    # 页码格式化
    formWigdet.lncrease_pageNo.setText(f' 第 {data["current_page"]} 页 ')
    if data["current_page"] == 1:
        # 第一页时，上一页按钮不显示【setVisible(True)】
        formWigdet.uplncreasePage.setVisible(False)
        nextFlag = True
        if len(windows.reportData) <= 20:
            nextFlag = False
        formWigdet.nextlncreasePage.setVisible(nextFlag)

    elif data["current_page"] == data["total_pages"]:
        # 最后一页时，下一页按钮不显示【setVisible(True)】
        formWigdet.uplncreasePage.setVisible(True)
        formWigdet.nextlncreasePage.setVisible(False)

    else:
        formWigdet.uplncreasePage.setVisible(True)
        formWigdet.nextlncreasePage.setVisible(True)

    # 自定义排序Model
    customSortmodel = CustomProxyModel()
    customSortmodel.setSourceModel(windows.increaseFive)
    formWigdet.lncrease_showStockTable.setModel(customSortmodel)

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

# 涨幅(5%)以上Tab--数据显示设定
def setingTable(tableView):
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
    tableView.verticalHeader().setSectionsClickable(True)  # 设置行头可点击（可选）
    # tableView.horizontalHeader().setSectionsMovable(True)  # 设置列头可移动（可选）
    # tableView.verticalHeader().setSectionsMovable(True)  # 设置行头可移动（可选）
    # tableView.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置列头文本居中显示（可选）
    tableView.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置行头文本居中显示（可选）
    # 列设置保持可调整（默认状态）
    # tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    # 设置行交替
    # tableView.setAlternatingRowColors(True)

    # 禁止编辑
    tableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    # 设置列宽
    tableView.setColumnWidth(0, 66)
    tableView.setColumnWidth(1, 79)
    tableView.setColumnWidth(2, 85)
    tableView.setColumnWidth(3, 80)
    tableView.setColumnWidth(4, 60)
    tableView.setColumnWidth(5, 66)
    tableView.setColumnWidth(6, 70)
    tableView.setColumnWidth(7, 60)
    tableView.setColumnWidth(8, 80)
    tableView.setColumnWidth(9, 66)
    tableView.setColumnWidth(10, 66)
    tableView.setColumnWidth(11, 70)
    tableView.setColumnWidth(12, 88)
    tableView.setColumnWidth(13, 66)
    tableView.setColumnWidth(14, 70)
    tableView.setColumnWidth(15, 70)
    tableView.setColumnWidth(16, 88)
    tableView.setColumnWidth(17, 72)
    tableView.setColumnWidth(18, 85)
    # 统计行数
    rowCount = tableView.model().rowCount()
    # 行数 小于 10
    if rowCount < 10:
        tableView.setColumnWidth(19, 92)
    else:
        tableView.setColumnWidth(19, 85)

    # 第21列隐藏 机构数据采集日期
    tableView.setColumnHidden(20, True)

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
def AddClickedIncreaseClear(windows, formWigdet):
    try:
        increaseFiveInitContent(windows, formWigdet)
    except Exception as ex:
        logger.error(f'清除处理出错了：{str(ex)}')

