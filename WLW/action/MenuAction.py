# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/3/8 19:16
# @Author : 连三保
# @Version: V 1.0
# @File : MenuAction.py
# @desc : 菜单按钮(事件绑定)

import datetime
from functools import partial

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QStatusBar, QMessageBox
from PyQt6 import QtGui

from WLW.StockBase import DateTimeUtils
from WLW.Database_loader import ProgressWindow
from WLW.Tools.LoggingEx import logger
from WLW.model import DataOpreationModel

def menuActionSetting(windows, formWigdet):
    # 事件绑定 -- 采集所有
    formWigdet.actionCrawlAll.triggered.connect(partial(ShowProgressWindow, windows, 'ALL'))
    # 事件绑定 -- 日涨停
    formWigdet.actionDailyLimit.triggered.connect(partial(ShowProgressWindow, windows, 'D'))
    # 事件绑定 -- 主力资金
    # formWigdet.actionMainCapital.triggered.connect(partial(ShowProgressWindow, windows, 'M'))
    # 事件绑定 -- 涨幅(5%)以上
    formWigdet.activeIncreaseFive.triggered.connect(partial(ShowProgressWindow, windows, 'I'))
    # 事件绑定 -- 板块资金
    formWigdet.activePlateFund.triggered.connect(partial(ShowProgressWindow, windows, 'P'))
    # 事件绑定 -- 机构持股
    formWigdet.actionStockHolding.triggered.connect(partial(ShowProgressWindow, windows, 'S'))
    # 事件绑定 -- 公告
    formWigdet.actionNotices.triggered.connect(partial(ShowProgressWindow, windows, 'N'))
    # 事件绑定 -- 风险个股
    formWigdet.actionServerData.triggered.connect(partial(addaAtionServerData, windows, 'Q'))
    # 事件绑定 -- 使用说明
    formWigdet.actionHelp.triggered.connect(partial(addaAtionHelp, windows))

# 使用说明
def addaAtionHelp(windows):
    content = """
说明如下：
  感谢您选择使用此软件，希望给您带来便利！
    数据采集（ST个股除外）
      1、交易日18点30分之后，可以操作。
      2、风险个股每月只能执行一次，软件启动的时候会去执行采集。

    功能
      1、涨停板
        统计当日大盘涨停的个股，涨停主题及原因等信息，分类显示功能以涨停主题进行归类统计和可视化显示所占比例；
为了方便投资者详细了解个股情况，单击个股时，以[表格、折线图、资金流向、数据中心、F10资料、可视化报告]进行相关信息显示。也可以打印和预览统计的数据。

      2、板块资金/概念资金
        统计净流入和净流出情况，以条形图和表格形式显示。
        
      3、涨幅(4%)以上
        统计最近5/10/20/60/120/250个交易日大盘个股涨幅在4%以上的数据，然后在此基础上分析出交易日、涨幅、股价和上榜统计的数据，并以此为检索条件进行精确检索。
        
      4、风险个股
        统计最近出现的风险个股，提醒投资者注意避险。
        
      5、公告
        A股市场个股公告。

  有任何问题可以联系我。邮箱：981037985@qq.com 

Version:3.0
    """
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.NoIcon)
    msg.setWindowTitle('数据采集')
    msg.setWindowIcon(QtGui.QIcon("_internal/image/wlw.svg"))
    msg.setText(content)
    # 设置消息框大小
    msg.setFixedSize(800, 800)  # 宽度800像素，高度800像素
    # 添加确定按钮
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec()

# 风险个股
def addaAtionServerData(windows, opreationType):
    try:
        yearMonth = datetime.datetime.today().strftime('%Y%m')
        # 交易日期
        yearMonthDom = str(DataOpreationModel.getDataInterval('STOCK_INFO_QUESTION'))
        if yearMonthDom == yearMonth:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle('数据采集')
            msg.setWindowIcon(QtGui.QIcon("_internal/image/wlw.svg"))
            msg.setText(f'风险个股数据已经是最新的，无需采集！')
            # 设置消息框大小
            msg.setFixedSize(400, 200)  # 宽度400像素，高度200像素
            # 添加确定按钮
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            return

        # 中国节假日数据采集
        windows.four = ProgressWindow(opreationType)
        # 窗体固定大小， 最大化无效
        windows.four.setWindowFlags(
            Qt.WindowType.Window | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.MSWindowsFixedSizeDialogHint);
        # 关闭窗口右下角拖动按钮
        windows.four.setStatusBar(QStatusBar().setSizeGripEnabled(False))
        # 阻塞所有窗口操作
        windows.four.setWindowModality(Qt.WindowModality.ApplicationModal)
        windows.four.show()
    except Exception as ex:
        logger.error(f'风险个股处理时，发生错误: {str(ex)}')

# 日涨停/主力资金进度条画面
def ShowProgressWindow(windows, opreationType):
    try:
        # 检查是否可执行
        if show_messagebox(opreationType):
            windows.four = ProgressWindow(opreationType)
            # 窗体固定大小， 最大化无效
            windows.four.setWindowFlags(
                Qt.WindowType.Window | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.MSWindowsFixedSizeDialogHint);
            # 关闭窗口右下角拖动按钮
            windows.four.setStatusBar(QStatusBar().setSizeGripEnabled(False))
            # 阻塞所有窗口操作
            windows.four.setWindowModality(Qt.WindowModality.ApplicationModal)
            windows.four.show()
    except Exception as ex:
        logger.error(f'ShowProgressWindow 处理{opreationType}时，发生错误: {str(ex)}')

def show_messagebox(opreationType):
    # 板块资金、公告
    if opreationType in ['P', 'N']:
        return True
    conditionHour = '183000'
    hour = DateTimeUtils.nowDateTime().strftime('%H%M%S')
    hourOut = DateTimeUtils.nowDateTime().strftime('%H点%M分%S秒')
    saleDate = DateTimeUtils.saleDate()
    nowDate = DateTimeUtils.nowDateTime().strftime('%Y%m%d')
    if saleDate == nowDate and hour < conditionHour:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle('数据采集')
        msg.setWindowIcon(QtGui.QIcon("_internal/image/wlw.svg"))
        msg.setText(f'现在时间：{hourOut}，18点30分之后可以执行！')
        # 设置消息框大小
        msg.setFixedSize(400, 200)  # 宽度400像素，高度200像素
        # 添加确定按钮
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
        return False

    return True
