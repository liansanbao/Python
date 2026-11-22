# _*_ coding: utf-8 _*_
# @Time : 2025/8/25 星期一 0:27
# @Author : 韦丽
# @Version: V 1.0
# @File : PlateFundAction.py
# @desc : 板块资金显示
# @uptime: 2026/11/21 12:44

import datetime
import os
from functools import partial
from typing import Dict, Any

import pandas
from PyQt6 import QtCore
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *   # 从 PyQt6 中导入所需的类
from pyecharts.charts import Bar
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from pyecharts.globals import CurrentConfig
from pyecharts.options import DataZoomOpts

from WLW.StockBase import DateTimeUtils
from WLW.StockBase.DateTimeUtils import get_quarter_dates
from WLW.Tools.CommonUtils import str_to_float, setQStandardItemPlateFund
from WLW.Tools.LoggingEx import logger
from WLW.action.CustomVerticalHeader import CustomVerticalHeader
from WLW.action.MultiPlateFundSortProxyModel import CustomProxyModel
from WLW.action.RowMenuAction import create_menu
from WLW.action.WebEngineViewEx import WebEngineView
from WLW.model import PlateFundModel
from WLW.model.PlateFundCondition import PlateFundCondition

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)

# 获取所在文件夹路径
dir_path = str(os.path.dirname(script_path))

dir_path = dir_path.replace('\\', '/')

# 板块资金Tab(初期化)
def plateFundInitContent(windows, formWigdet):
    # 主力净流入(净额)条件设定
    formWigdet.plateFund_condition_zljlrje.clear()
    formWigdet.plateFund_condition_zljlrje.addItems(['=', '>', '<'])
    formWigdet.plateFund_condition_zljlrje.setCurrentIndex(0)
    formWigdet.plateFund_condition_zljlrje.setMinimumHeight(26)

    # 主力净流入(净额)单位
    formWigdet.plateFund_zljlrje_unit.clear()
    formWigdet.plateFund_zljlrje_unit.addItems(['亿', '万', '元'])
    formWigdet.plateFund_zljlrje_unit.setCurrentIndex(0)
    formWigdet.plateFund_zljlrje_unit.setMinimumHeight(26)

    # 板块代码
    formWigdet.plateFund_No.setText('')
    # 设置只能输入6位0-9的数字
    formWigdet.plateFund_No.setNumberWithRangeBK(4)

    # 板块名称
    formWigdet.plateFund_Name.setText('')

    # 主力净流入(净额)
    formWigdet.plateFund_zljlrje.setText('')

    # 当前周開始日取得
    weekFromDay = DateTimeUtils.Week_Day_Date(weekDay=1)

    # 交易日期From 显示格式
    formWigdet.plateFundDate_From.setDate(QDate(weekFromDay.year, weekFromDay.month, 1))
    # 交易日期From 可选最大日期
    formWigdet.plateFundDate_From.setMaximumDate(QDate.currentDate().addDays(0))
    # 交易日期From 可选最小日期
    # formWigdet.plateFundDate_From.setMinimumDate(QDate.currentDate().addDays(-30))
    # 交易日期From 日历控件弹出
    formWigdet.plateFundDate_From.setCalendarPopup(True)

    # 交易日期To 显示格式
    formWigdet.plateFundDate_To.setDate(QDate.currentDate())
    # 交易日期To 可选最大日期
    formWigdet.plateFundDate_To.setMaximumDate(QDate.currentDate().addDays(0))
    # 交易日期To 可选最小日期
    # formWigdet.plateFundDate_To.setMinimumDate(QDate.currentDate().addDays(-30))
    # 交易日期To 日历控件弹出
    formWigdet.plateFundDate_To.setCalendarPopup(True)

    # 上一页
    upIcon = QIcon()
    upIcon.addPixmap(QPixmap("_internal/image/upPage.svg"), QIcon.Mode.Normal, QIcon.State.Off)
    formWigdet.upPlateFundPage.setIcon(upIcon)
    # 下一页
    nextIcon = QIcon()
    nextIcon.addPixmap(QPixmap("_internal/image/nextPage.svg"), QIcon.Mode.Normal, QIcon.State.Off)
    formWigdet.nextPlateFundPage.setIcon(nextIcon)

    # 数据检索定时器
    # formWigdet.data_timer = QTimer()
    # formWigdet.data_timer.timeout.connect(partial(AutoCharts, windows, formWigdet))
    # # 检索时间起始值
    # formWigdet.searchStaHour = 9
    # formWigdet.searchStaMinu = 31
    # # 检索时间终止值
    # formWigdet.searchEndHour = 15
    # # 1分钟采集一次数据
    # formWigdet.searchFrequency = 1
    # formWigdet.plateFundActivate.setText('轨迹')
    # formWigdet.plateFundHour.setText('')
    # formWigdet.plateFundMin.setText('')

    # 设置行右键菜单功能
    if formWigdet.passKey == 'WLW':
        formWigdet.plateFund_showStockTable.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        formWigdet.plateFund_showStockTable.customContextMenuRequested.connect(
            lambda pos: show_menu(pos, windows, formWigdet))

    # 确认存放charts文件的目录是否存在
    windows.plateFundCharts_dir = f'{dir_path}/chart'
    if not os.path.exists(windows.plateFundCharts_dir):
        os.makedirs(windows.plateFundCharts_dir)

    # 确认存放charts文件快照的PNG目录是否存在
    windows.charts_png_dir = f'{dir_path}/PNG'
    if not os.path.exists(windows.charts_png_dir):
        os.makedirs(windows.charts_png_dir)
    logger.info(f'确认存放charts文件快照的PNG目录: [{windows.charts_png_dir}]存在！！！')

# 表格行右键菜单
def show_menu(pos, windows, formWigdet):
    try:
        index = formWigdet.plateFund_showStockTable.indexAt(pos)
        # 获取当前行所有列的值
        model = formWigdet.plateFund_showStockTable.model()
        # 持股机构数
        institutionCount = int(model.index(index.row(), 9).data())
        # 鼠标单击行焦点取得
        qPoint = formWigdet.plateFund_showStockTable.viewport().mapToGlobal(pos)

        if index.isValid() and institutionCount > 0:
            # 以交易日期转换成机构持股报告日期
            reportDate = get_quarter_dates("%Y-%m-%d %H:%M:%S", model.index(index.row(), 0).data(), "%Y-%m-%d")[
                "end_date"]
            # 获取股票代码
            stockNo = model.index(index.row(), 8).data()
            # 获取股票名称
            stockName = model.index(index.row(), 7).data()
            # 数据采集日期
            holdingDate = model.index(index.row(), 18).data()
            # 调用机构持股详细画面
            create_menu(reportDate, stockNo, stockName, holdingDate, '', '', index, qPoint, windows)
    except Exception as ex:
        logger.error(f'右击菜单处理出错了：{str(ex)}')

# 板块资金(事件绑定)
def plateFundActionSetting(windows, formWigdet):
    # 事件绑定 -- 检索
    formWigdet.plateFundSubmit.clicked.connect(partial(AddClickedPlateFundSubmit, windows, formWigdet, 'S'))
    # 事件绑定 -- 清除
    formWigdet.plateFundClear.clicked.connect(partial(AddClickedPlateFundClear, windows, formWigdet))
    # 事件绑定 -- 板块/概念切换
    formWigdet.plateFundActivate.clicked.connect(partial(AddClickedPlateFundActivate, windows, formWigdet))
    # 事件绑定 -- 上一页
    formWigdet.upPlateFundPage.clicked.connect(partial(AddClickedIncreasePage, 'up', windows, formWigdet))
    # 事件绑定 -- 下一页
    formWigdet.nextPlateFundPage.clicked.connect(partial(AddClickedIncreasePage, 'next', windows, formWigdet))

# 事件绑定 -- 翻页处理
def AddClickedIncreasePage(type, windows, formWigdet):
    try:
        if type == 'up':
            windows.current_PlateFundPage -= 1
        elif type == 'next':
            windows.current_PlateFundPage += 1
        # 分页处理
        data = get_page(windows.showPlateFundData, windows.current_PlateFundPage, 11)
        # 数据显示处理
        showTableData(data, windows, formWigdet)
        # 表格设定
        setingPlateFundTable(formWigdet.plateFund_showStockTable)
    except Exception as ex:
        logger.error(f'翻页处理出错了：{str(ex)}')

# 数据显示处理
def showTableData(data, windows, formWigdet):
    # ListView model 4Row 3 coloumn
    windows.plateFundShowModel = QStandardItemModel(0, 18)
    # 创建行标题
    windows.plateFundShowModel.setHorizontalHeaderLabels(
        ['交易日期', '板块代码', '板块名称', '最新价', '涨跌幅', '主力B(净额)', '主力B(净占比)', '优秀股名称',
         '优秀股代码',
         '持股机构数', '涨停主题', '概念', '涨停原因', '涨幅', '价格', '成交量(手)', '成交额', '换手率', 'hidden'])

    # 设定项目值显示
    showHeaderLables = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]
    if data['data']:
        for row, item in enumerate(data['data']):
            # windows.plateFundShowModel.appendRow([setQStandardItem(str(item[value]), value) for value in showHeaderLables])
            row_items = []
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
                elif col_idx in (10, ):
                    bold_font = QFont()
                    bold_font.setBold(True)
                    std_item.setFont(bold_font)

                row_items.append(std_item)
            windows.plateFundShowModel.appendRow(row_items)

    # 页码格式化
    formWigdet.plateFundPageNo.setText(f' 第 {data["current_page"]} 页 ')
    if data["current_page"] == 1:
        # 第一页时，上一页按钮不显示【setVisible(True)】
        formWigdet.upPlateFundPage.setVisible(False)
        nextFlag = True
        if len(windows.showPlateFundData) <= 11:
            nextFlag = False
        formWigdet.nextPlateFundPage.setVisible(nextFlag)

    elif data["current_page"] == data["total_pages"]:
        # 最后一页时，下一页按钮不显示【setVisible(True)】
        formWigdet.upPlateFundPage.setVisible(True)
        formWigdet.nextPlateFundPage.setVisible(False)

    else:
        formWigdet.upPlateFundPage.setVisible(True)
        formWigdet.nextPlateFundPage.setVisible(True)

    # 自定义排序Model
    customSortmodel = CustomProxyModel()
    customSortmodel.setSourceModel(windows.plateFundShowModel)
    formWigdet.plateFund_showStockTable.setModel(customSortmodel)
    # ===================== 新增：连续行号 =======================================================
    page_no = data["current_page"]
    page_size = data["page_size"]
    offset = (page_no - 1) * page_size
    v_header = formWigdet.plateFund_showStockTable.verticalHeader()
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

# 事件绑定 -- 板块/概念切换
def AddClickedPlateFundActivate(windows, formWigdet):
    try:
        current_name = ''
        plateFund_name = ''
        # 板块/概念 切换
        if formWigdet.plateFundActivate.text() == '概念':
            current_name = '概念资金'
            plateFund_name = '板块'
        elif formWigdet.plateFundActivate.text() == '板块':
            current_name = '板块资金'
            plateFund_name = '概念'

        # formWigdet.tabWidget.setTabText(current_name)
        _translate = QtCore.QCoreApplication.translate
        formWigdet.tabWidget.setTabText(formWigdet.tabWidget.indexOf(formWigdet.plateFund),
                                        _translate("WLW", current_name))
        formWigdet.plateFundActivate.setText(plateFund_name)
        AddClickedPlateFundSubmit(windows, formWigdet, 'S')
    except Exception as ex:
        logger.error(f'板块/概念切换处理出错了：{str(ex)}')

    # if formWigdet.plateFundActivate.text() == '轨迹':
    #     formWigdet.plateFundActivate.setText('暂停')
    #     enableFlag = False
    #     formWigdet.data_timer.start(6000)  # 每6秒检索一次数据
    #
    #     if formWigdet.plateFundHour.text() != '':
    #         formWigdet.searchStaHour = int(formWigdet.plateFundHour.text())
    #     if formWigdet.plateFundMin.text() != '':
    #         formWigdet.searchStaMinu = int(formWigdet.plateFundMin.text())
    #
    #     # 10点和13点开始，2分钟采集一次数据
    #     if formWigdet.searchStaHour == 10 or formWigdet.searchStaHour == 13:
    #         formWigdet.searchFrequency = 2
    #
    #     # 第一次检索
    #     AddClickedPlateFundSubmit(windows, formWigdet, 'A')
    #
    # elif formWigdet.plateFundActivate.text() == '暂停':
    #     formWigdet.plateFundActivate.setText('轨迹')
    #     enableFlag = True
    #     formWigdet.data_timer.stop()
    #
    # formWigdet.plateFundClear.setEnabled(enableFlag)
    # formWigdet.plateFundSubmit.setEnabled(enableFlag)

# 事件绑定 -- 检索
def AddClickedPlateFundSubmit(windows, formWigdet, activateType):
    try:
        # 主力资金--数据绑定
        editPlateFundTable(windows, formWigdet, activateType)
    except Exception as ex:
        logger.error(f'检索处理出错了：{str(ex)}')

# 板块资金--数据绑定
def editPlateFundTable(windows, formWigdet, activateType: str = 'S'):
    # 主力资金Tab--数据绑定
    getPlateFundData(windows, formWigdet, activateType)
    # if windows.showPlateFundData:
    # 主力资金Tab--数据显示设定
    setingPlateFundTable(formWigdet.plateFund_showStockTable)
    # 板块资金--主力B金额条形图
    editPlateFundCharts(windows, formWigdet, activateType)

# 板块资金--主力B金额条形图
def editPlateFundCharts(windows, formWigdet, activateType):
    # 修改pyecharts库的js路径，变成本地文件夹js文件 非常重要
    CurrentConfig.ONLINE_HOST = ''

    # 浏览器初始化
    browser = getattr(windows, 'plateFundBrowser', None)
    if browser != None:
        formWigdet.detailInfo.removeWidget(windows.plateFundBrowser)
        windows.plateFundBrowser.deleteLater()  # 安全删除对象
        windows.plateFundBrowser = None  # 清除引用

    # pandas.DataFrame 条件检索
    if windows.showPlateFundData:
        # 条形图文件名
        hangQingDateFrom = DateTimeUtils.Format_changed(formWigdet.plateFundDate_From.text(), '%Y年%M月%d日', '%Y%M%d')
        chartFileName = f'{windows.plateFundCharts_dir}/PlateFund_{hangQingDateFrom}.html'
        windows.pdfPngFile = f'{windows.charts_png_dir}/PlateFund_{hangQingDateFrom}.png'

        # 将检索结果转成pandas
        searchPandas = pandas.DataFrame(data=windows.showPlateFundData,
                                        columns=['CREATE_DATE', 'F12', 'F14', 'F2', 'F3', 'F62', 'F184', 'F204', 'F205',
                                                 'INSTITUTION_COUNT', 'LIMIT_TITLE', 'CONCEPT', 'LIMIT_WHY', 'GSF3', 'GSF2', 'GSF5', 'GSF6', 'GSF8', 'hidden'])
        searchPandas['F62_clean'] = searchPandas['F62'].apply(clean_unit)
        sum_bk = (searchPandas
                  .groupby('F14', as_index=False)
                  .sum()[['F14', 'F62_clean']]
                  .rename(columns={'F62_clean': 'sum_value'}))
        stockGroupDict = dict(zip(sum_bk['F14'].astype(str), sum_bk['sum_value']))
        pieStockNmData = []
        for name in stockGroupDict:
            pieStockNmData.append((name, stockGroupDict[name]))

        # 降序
        pieData = sorted(pieStockNmData, key=lambda num: num[1], reverse=True)
        # 将数值转换成亿或者万的格式
        converted_data = [(rotate_text_90(name), convert_unit(value)) for name, value in pieData]
        logger.info(f'converted_data: {converted_data}')
        pie = Bar(init_opts=opts.InitOpts(theme='light',
                                          width='1420px',
                                          height='240px',
                                          animation_opts=opts.AnimationOpts(animation=False)  # 禁用动画提升性能
                                          ))
        pie.add_xaxis([item[0] for item in converted_data])
        pie.add_yaxis('', [item[1] for item in converted_data], itemstyle_opts=opts.ItemStyleOpts(
            JsCode("function(params) {var value = parseFloat(params.value); return value > 0 ? 'red' : 'green';}")))

        # 重写opts.DataZoomOpts对象，添加brushSelect属性 ST
        customerDataZoomOpts = DataZoomOpts(type_="slider",
                                    range_start=0,
                                    range_end=35, # 板块
                                    # range_end=6, # 概念
                                    pos_top="4%",orient="horizontal",is_zoom_lock=True)
        customerDataZoomOpts.opts['brushSelect'] = False
        # 重写DataZoomOpts对象，添加brushSelect属性 ND

        searchTime = ''
        # 检索时间
        if activateType == 'A':
            searchTime = f'{"{:02d}".format(formWigdet.searchStaHour)}:{"{:02d}".format(formWigdet.searchStaMinu)}:00'

        # 全局配置调整
        pie.set_global_opts(
            title_opts=opts.TitleOpts(title=searchTime, title_textstyle_opts=opts.TextStyleOpts(font_size=18, font_weight='bold', color='red')),
                            toolbox_opts=opts.ToolboxOpts(is_show=False),
                            # 独立添加数据缩放组件并设置在图形下方显示
                            datazoom_opts=[
                                # opts.DataZoomOpts(
                                #     type_="slider",
                                #     range_start=0,
                                #     range_end=35,
                                #     pos_top="4%",  # 靠近顶部
                                #     orient="horizontal",  # 关键配置
                                #     # brushSelect=False, # 该属性不存在
                                #     is_zoom_lock=True  # 禁用鼠标框选
                                # )
                                customerDataZoomOpts
                            ],
                            # x轴配置（现在是纵向显示，x轴在底部）
                            xaxis_opts=opts.AxisOpts(
                                axislabel_opts=opts.LabelOpts(
                                    font_size=12,
                                    font_weight='bold',
                                    color='#333',
                                    interval=0, # 显示所有标签
                                    # rotate=90, # 标签旋转90度纵向显示
                                    margin=10  # 增加标签间距
                                ),
                                splitline_opts=opts.SplitLineOpts(is_show=False  # True 显示网格
                                ),
                                axisline_opts=opts.AxisLineOpts(is_show=True),
                                boundary_gap=True  # 留出边界空间
                            ),
                            # y轴配置（现在是纵向显示，y轴在左侧）
                            yaxis_opts=opts.AxisOpts(
                                splitline_opts=opts.SplitLineOpts(is_show=False  # True 显示网格
                                ),
                                axisline_opts=opts.AxisLineOpts(is_show=True),
                                axislabel_opts=opts.LabelOpts(font_size=12, font_weight='bold', color='#333')
                            ))
        # 条线图数值显示样式设定
        pie.set_series_opts(
            # 条形柱子之间的间距参数
            barMinHeight = 5,
            barCategoryGap = "15%",
            barGap = "20%",
            label_opts=opts.LabelOpts(
                position='top', # 数值标签显示在柱子顶部
                distance=15,  # 强制设置标签与柱子的距离
                formatter=JsCode("""function(params) {var value = parseFloat(params.value); return value > 0 ? '{c|' + value + ' 亿}' : '{d|' + value + ' 亿}';}"""),
                rich= {"c": {"color": "red", "fontSize": 8}, "d": {"color": "green", "fontSize": 8}}
            )
        )

        # html文件生成
        pie.render(chartFileName)
    else:
        chartFileName = f'{windows.plateFundCharts_dir}/PlateFund_NoData.html'
        windows.pdfPngFile = f'{windows.charts_png_dir}/PlateFund_NoData.png'

    # html文件名称打印
    logger.info(f'chartFileName: {chartFileName}')

    # 创建web引擎视图
    windows.plateFundBrowser = WebEngineView()
    windows.plateFundBrowser.setMinimumSize(1420, 240)  # 固定显示区域
    windows.plateFundBrowser.load(QUrl(f"file:///{chartFileName}"))
    windows.plateFundBrowser.loadFinished.connect(partial(on_load_finished, windows, formWigdet))
    formWigdet.detailInfo.addWidget(windows.plateFundBrowser)
    formWigdet.verticalLayoutWidget.show()

def on_load_finished(windows, formWidget):
    QTimer.singleShot(1000, partial(save_high_res, windows))

def save_high_res(windows):
    windows.plateFundBrowser.page().runJavaScript("document.body.scrollHeight;",
        lambda height: windows.plateFundBrowser.grab().scaled(
            windows.plateFundBrowser.size() * 2,  # 2倍缩放
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ).save(windows.pdfPngFile, "PNG", 100)  # 100%质量
    )

# 文字顺时针旋转90度
def rotate_text_90(text):
    """顺时针旋转90度打印"""
    max_len = max(len(line) for line in text.split('\n'))
    rotated = []
    for i in range(max_len):
        rotated_line = ''.join([
            line[i] if i < len(line) else ' '
            for line in reversed(text.split('\n'))
        ])
        rotated.append(rotated_line)
    return '\n'.join(rotated)

# 解析带单位的数值字符串为浮点数
def clean_unit(keyStr):
    try:
        if isinstance(keyStr, str):
            """解析带单位的数值字符串为浮点数"""
            s = keyStr.strip().replace(',', '')
            if '亿' in s:
                return float(s.replace('亿', '')) * 1e8
            elif '万' in s:
                return float(s.replace('万', '')) * 1e4

            return float(s)
    except Exception:
        return float(0)

# 板块资金Tab--数据绑定
def getPlateFundData(windows, formWigdet, activateType):
    # 检索条件获取
    # 交易日期From
    hangQingDateFrom = DateTimeUtils.Format_changed(formWigdet.plateFundDate_From.text(), '%Y年%M月%d日', '%Y%M%d')
    # 交易日期To
    hangQingDateTo = DateTimeUtils.Format_changed(formWigdet.plateFundDate_To.text(), '%Y年%M月%d日', '%Y%M%d')
    # 主力净流入(净额)条件设定
    condition_zljlrje = formWigdet.plateFund_condition_zljlrje.currentIndex()
    # 主力净流入(净额)单位
    condition_unit = ['亿', '万', '元']
    condition_zljlrje_unit = condition_unit[formWigdet.plateFund_zljlrje_unit.currentIndex()]
    # 板块代码
    plateFund_No = formWigdet.plateFund_No.text()
    # 板块名称
    plateFund_Name = formWigdet.plateFund_Name.text()
    # 主力净流入(净额)
    plateFund_zljlrje = formWigdet.plateFund_zljlrje.text()
    if plateFund_zljlrje:
        plateFund_zljlrje = clean_unit(f'{plateFund_zljlrje}{condition_zljlrje_unit}')

    # 排序选项
    orderByOption = ' ORDER BY CAST(HC.F62 AS INTEGER) DESC'
    searchTime = ''
    # 检索时间
    if activateType == 'A':
        searchTime = f'{hangQingDateFrom} {"{:02d}".format(formWigdet.searchStaHour)}{"{:02d}".format(formWigdet.searchStaMinu)}00'

    # 板块/概念 切换
    hyType = '1'
    current_name = formWigdet.tabWidget.tabText(formWigdet.tabWidget.currentIndex())
    if current_name == '概念资金':
        hyType = '2'

    plateFundCondition = PlateFundCondition(hangQingDateFrom, hangQingDateTo, plateFund_No, plateFund_Name, plateFund_zljlrje, condition_zljlrje, activateType, searchTime, hyType, orderByOption)
    # 添加数据;
    windows.showPlateFundData = PlateFundModel.getPlateFundWLWData(plateFundCondition)
    count = 0
    enableFlag = False
    # 主力净流入
    plateFundInput = float(0)
    # 主力净流出
    plateFundOutput = float(0)
    # 设定项目值显示
    if windows.showPlateFundData:
        for row, item in enumerate(windows.showPlateFundData):
            f62 = str_to_float(item[5])
            if f62 > 0:
                plateFundInput += f62
            else:
                plateFundOutput += f62
        # 总件数format
        count = len(windows.showPlateFundData)
        # 页码初始化
        windows.current_PlateFundPage = 1
        # 分页处理
        data = get_page(windows.showPlateFundData, windows.current_PlateFundPage, 11)
        # 数据显示处理
        showTableData(data, windows, formWigdet)
        enableFlag = True
    else:
        # windows.plateFundShowModel.clear()  # 清除所有数据及表头
        # 分页按钮不显示
        formWigdet.upPlateFundPage.setVisible(False)
        formWigdet.nextPlateFundPage.setVisible(False)
        # 页码格式化
        formWigdet.plateFundPageNo.setText('')

    formWigdet.plateFundInput.setText('净流入: ' + convert_unit(plateFundInput) + '亿')
    formWigdet.plateFundOutput.setText('净流出: ' + convert_unit(plateFundOutput) + '亿')
    # 总件数format
    formWigdet.plateFund_count_number.setText(f'共 {count} 条')
    # data 不显示
    formWigdet.plateFund_showStockTable.setVisible(enableFlag)

# 条形图数值转换
def convert_unit(value):
    return f'{round(str_to_float(value) / 100000000, 2):.2f}'

# 主力资金Tab--数据显示设定
def setingPlateFundTable(tableView):
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
    tableView.setStyleSheet(style_sheet)

    # ========= 【重点修改这里】只初次替换一次垂直表头，不要重复新建 =====================================
    vh = tableView.verticalHeader()
    if not isinstance(vh, CustomVerticalHeader):
        # 只有原生表头的时候，才替换一次
        new_vh = CustomVerticalHeader(tableView)
        tableView.setVerticalHeader(new_vh)
        # 绑定点击事件，只绑定一次
        from PyQt6.QtCore import QItemSelectionModel
        new_vh.sectionClicked.connect(lambda row: tableView.selectionModel().select(
            tableView.model().index(row, 0),
            QItemSelectionModel.SelectionFlag.Rows | QItemSelectionModel.SelectionFlag.ClearAndSelect
        ))
    # ==========================================================================================

    # 去掉网格线
    tableView.setShowGrid(False)
    # 设置行交替
    tableView.setAlternatingRowColors(True)

    # 设置样式表添加边框
    tableView.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)  # 禁止调整行高
    tableView.verticalHeader().setDefaultSectionSize(29)  # 设置默认行高为30像素（可选）
    tableView.horizontalHeader().setMinimumHeight(29)
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
    tableView.setColumnWidth(0, 130)
    tableView.setColumnWidth(1, 70)
    tableView.setColumnWidth(2, 80)
    tableView.setColumnWidth(3, 80)
    tableView.setColumnWidth(4, 60)
    tableView.setColumnWidth(5, 80)
    tableView.setColumnWidth(6, 95)
    tableView.setColumnWidth(7, 75)
    tableView.setColumnWidth(8, 70)
    tableView.setColumnWidth(9, 70)
    tableView.setColumnWidth(10, 90)
    tableView.setColumnWidth(11, 96)
    tableView.setColumnWidth(12, 90)
    tableView.setColumnWidth(13, 64)
    tableView.setColumnWidth(14, 85)
    tableView.setColumnWidth(15, 80)
    tableView.setColumnWidth(16, 76)
    tableView.setColumnWidth(17, 65)

    # 第19列隐藏 机构数据采集日期
    tableView.setColumnHidden(18, True)

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
def AddClickedPlateFundClear(windows, formWigdet):
    try:
        plateFundInitContent(windows, formWigdet)
    except Exception as ex:
        logger.error(f'清除处理出错了：{str(ex)}')
