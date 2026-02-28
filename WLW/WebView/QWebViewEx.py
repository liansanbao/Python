# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/3/8 15:43
# @Author : 连三保
# @Version: V 1.0
# @File : mainFunction.py
# @desc :PDF打印、预览、保存
from datetime import datetime

import sys
from PyQt6.QtCore import QUrl, Qt, pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QApplication, QMessageBox, QProgressDialog, QStatusBar

from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest

from WLW.WebView.PrintHandlerEx import PrintHandler
from WLW.WebView.Ui_main import Ui_MainWindow
from WLW.WebView.downLoadDialog import DownLoadDialog
from WLW.WebView.webview import WebView
from WLW.Tools.LoggingEx import logger


class FunctionMW(QMainWindow, Ui_MainWindow):
    closed = pyqtSignal()  # 定义关闭信号

    def __init__(self, file, parent=None):
        super().__init__(parent)
        self.filePath = file
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.newWebView = WebView()
        self.page = self.newWebView.page()  # 网页浏览的页面
        self.page.profile().downloadRequested.connect(self.downloadRequested)  # 下载文件信号触发
        # self.page.printRequested.connect(self.handlePrintRequest)
        self.setCentralWidget(self.newWebView)
        self.newWebView.load(QUrl(f'file:///{self.filePath}#toolbar=0'))
        # 加载PDF时添加#toolbar=0参数 去掉工具栏
        # self.newWebView.load(
        #     QUrl('file:///D:/learing/Python/Stock202409/window/action/PDF/DL_多行业数据_20250707.pdf#toolbar=0'))
        self.action_printer.triggered.connect(self.handlePrintRequest)
        self.action_save.triggered.connect(self.downloadTriggered)
        # 窗体固定大小， 最大化无效
        self.setWindowFlags(
            Qt.WindowType.Window | Qt.WindowType.WindowMinimizeButtonHint | Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.MSWindowsFixedSizeDialogHint);
        # 关闭窗口右下角拖动按钮
        self.setStatusBar(QStatusBar().setSizeGripEnabled(False))
        self.setWindowModality(Qt.WindowModality.ApplicationModal)  # 阻塞所有窗口操作

    # 页面打印
    def handlePrintRequest(self):
        handler = PrintHandler(self.newWebView)
        handler.load_pdf(self.filePath)
        # handler.show_print_preview()
        handler.print_directly()

    # 页面保存
    def downloadTriggered(self):
        # 获取当前页面URL或指定下载资源
        download_item = self.page.download(self.page.url())
        self.downloadRequested(download_item)

    def downloadRequested(self, item):
        try:
            """
                    获取下载请求的 URL，并启动下载对话框
                    item：下载对象
                    """
            downLoadItem = item
            if downLoadItem and downLoadItem.state() == QWebEngineDownloadRequest.DownloadState.DownloadRequested:
                # 进入下载状态就会打开下载对话框
                downloadDialog = DownLoadDialog(downLoadItem, self)
                downloadDialog.downloadStart.connect(self.downloading)
                downloadDialog.exec()
        except Exception as ex:
            logger.error(f'错误了： {ex}')

    def downloading(self, item, path, downLoadName):
        """
        预备下载了
        """
        self.now1 = datetime.now()  # 开始计时
        self.downLoadItem = item
        self.downLoadItem.setDownloadDirectory(path) # 设置下载目录
        self.downLoadItem.setDownloadFileName(downLoadName) # 设置下载文件名
        self.downLoadItem.accept() # 开始下载
        self.downLoadItem.totalBytesChanged.connect(self.updateProgress) # 下载文件总大小
        self.downLoadItem.receivedBytesChanged.connect(self.updateProgress) # 下载文件接收大小
        self.downLoadItem.stateChanged.connect(self.updateProgress) # 下载文件的状态变化
        self.execProgressDialog()

    def execProgressDialog(self):
        """
        启动下载进程对话框
        """
        self.progress = QProgressDialog(self)
        self.progress.setWindowTitle("正在下载文件")
        self.progress.setCancelButtonText("取消")
        self.progress.setMinimumDuration(100) # 预估最少时间大于0.1秒才显示对话框
        self.progress.setWindowModality(Qt.WindowModality.WindowModal) # 对话框模态
        self.progress.setRange(0, 100)
        self.progress.canceled.connect(self.canceledDownLoad) # 单击“取消”按钮触发

    def canceledDownLoad(self):
        """
        取消下载
        """
        self.downLoadItem.cancel()

    def UnitConversion(self, size):
        """
        单位转换
        size：文件大小
        """
        if size < 1024:
            return f"{size} bytes"
        elif size < 1024*1024:
            return f"{size/1024:.2f} KB"
        elif size < 1024*1024*1024:
            return f"{size/pow(1024, 2):.2f} MB"
        else:
            return f"{size/pow(1024, 3):.2f} GB"

    def updateProgress(self):
        """
        更新进度对话框
        """
        duration = (datetime.now() - self.now1).seconds # 持续时间（秒）
        if duration == 0:
            duration = 1
        totalBytes = self.downLoadItem.totalBytes() # 总的大小
        receivedBytes = self.downLoadItem.receivedBytes() # 已经下载的大小
        bytesPerSecond = receivedBytes / duration # 平均下载速度
        downLoadState = self.downLoadItem.state() # 下载状态
        if downLoadState == QWebEngineDownloadRequest.DownloadState.DownloadInProgress:
            # 下载
            if totalBytes >= 0:
                self.progress.setValue(int(100 * receivedBytes / totalBytes))
                downloadInfo = f"接收：{self.UnitConversion(receivedBytes)}，总大小：{self.UnitConversion(totalBytes)}，平均下载速度：{self.UnitConversion(bytesPerSecond)}/S"
                self.progress.setLabelText(downloadInfo)
            else:
                self.progress.setValue(0)
                downloadInfo = f"接收：{self.UnitConversion(receivedBytes)}，总大小未知，平均下载速度：{self.UnitConversion(bytesPerSecond)}/S"
                self.progress.setLabelText(downloadInfo)
        elif downLoadState == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
            # 下载完毕
            QMessageBox.information(self, "提示", "下载完毕！")
        elif downLoadState == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted:
            # 下载被终止，如：网络问题
            self.progress.setValue(0)
            downloadInfo = f"下载失败！\n接收：{self.UnitConversion(receivedBytes)}，总大小：{self.UnitConversion(totalBytes)}，平均下载速度：{self.UnitConversion(bytesPerSecond)}/S\n{self.downLoadItem.interruptReasonString()}"
            self.progress.setLabelText(downloadInfo)

    # 打印预览窗体关闭
    def closeEvent(self, event):
        self.closed.emit()  # 发射关闭信号
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    webBrowser = FunctionMW('D:/learing/Python/Stock202409/WebEngineView/20250629.pdf')
    webBrowser.show()
    sys.exit(app.exec())