# _*_ coding: utf-8 _*_
# @Time : 2025/7/25 星期五 21:05
# @Author : 韦丽
# @Version: V 1.0
# @File : UpdateWlw.py
# @desc : WLW软件下载自动更新
#         要求：每次启动软件时，访问服务器确认当前运行软件版本是否是与服务器当前提供的版本一致。
#              不一致时，弹出下载更新的页面
import json
import sys
import os
import subprocess
from PyQt6.QtGui import QIcon, QPixmap
import requests
from PyQt6.QtWidgets import (QMainWindow, QProgressBar,
                             QPushButton, QVBoxLayout, QWidget, QMessageBox)
from PyQt6.QtCore import QThread, pyqtSignal, QSize

from WLW.Tools.LoggingEx import logger

# 软件版本
CURRENT_VERSION=3.3

# 下载
class DownloadThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, url, save_path):
        super().__init__()
        self.url = url
        self.save_path = save_path

    def run(self):
        try:
            with requests.get(self.url, stream=True, timeout=30) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                downloaded = 0

                with open(self.save_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        progress = int(100 * downloaded / total_size)
                        self.progress.emit(progress)

                self.finished.emit(self.save_path)
        except Exception as e:
            self.error.emit(str(e))

# 软件自动更新
class InstallerWindow(QMainWindow):
    def __init__(self, dir_path, installPath):
        super().__init__()
        self.singe_exe = dir_path
        self.install_path = installPath  # 默认路径^^^1^^^
        self.setup_ui()
        self.download_thread = None

    def isUpdae(self):
        try:
            self.download_url = "https://w7wp557v37c1.xiaomiqiu.com/downloadWlw?pType=Online"
            self.wlw_dict = {}

            with requests.get(self.download_url, stream=True, timeout=30) as r:
                json_data = json.loads(r.text)
                for name in json_data:
                    self.wlw_dict = dict(name)
                    break

            if self.wlw_dict:
                if float(self.wlw_dict['version']) > CURRENT_VERSION:
                    return True

            return False
        except Exception as e:
            QMessageBox.critical(self, "错误", f"检查更新失败: {str(e)}")
            return False

    def setup_ui(self):
        # 窗体标题
        icon = QIcon()
        icon.addPixmap(QPixmap("_internal/image/wlw.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.setWindowIcon(icon)
        self.setWindowTitle("WLW更新")
        self.setFixedSize(400, 200)

        self.progress_bar = QProgressBar()
        self.progress_bar.setGeometry(30, 40, 340, 30)
        self.progress_bar.setFixedHeight(30)
        self.progress_bar.setRange(0, 100)
        # 进度条样式：单色纯绿
        self.progress_bar.setStyleSheet("""
                    QProgressBar {
                        border: 2px solid #00C853;
                        border-radius: 5px;
                        background: #ECF0F1;
                        text-align: center;  /* 水平居中 */
                    }
                    QProgressBar::chunk {
                        background: qlineargradient(
                            spread:pad, x1:0, y1:0.5, x2:1, y2:0.5,
                            stop:0 #00C853, stop:1 #00C853);
                        border-radius: 3px;
                    }
                """)

        self.btn_update = QPushButton(" 更新", self)
        dicon = QIcon()
        dicon.addPixmap(QPixmap("_internal/image/DAI.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_update.setIcon(dicon)
        self.btn_update.setIconSize(QSize(16, 16))  # 图标大小
        self.btn_update.setFixedHeight(36)  # 按钮高度
        self.btn_update.setStyleSheet("""
                QPushButton {
                    background-color: #00C853;  /* 绿色背景 */
                    color: #333333;             /* 白色文字 */
                    border-radius: 5px;         /* 圆角边框 */
                    border: none;               /* 无边框 */
                    padding: 8px 16px;          /* 内边距 */
                    font-size: 14px;
                    font-weight: 500;
                }
                QPushButton:hover { background-color: #00A040; }  /* 悬停加深 */
                QPushButton:pressed { background-color: #008030; } /* 按下效果 */
            """)
        self.btn_update.clicked.connect(self.start_download)

        # 跳过
        self.btn_pass = QPushButton(" 跳过", self)
        dicon = QIcon()
        dicon.addPixmap(QPixmap("_internal/image/pass.svg"), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_pass.setIcon(dicon)
        self.btn_pass.setIconSize(QSize(16, 16))
        self.btn_pass.setFixedHeight(36)
        self.btn_pass.setStyleSheet("""
                QPushButton {
                    background-color: #ECF0F1;  /* 浅灰背景 */
                    color: #333333;             /* 深灰文字 */
                    border-radius: 5px;         /* 圆角边框 */
                    border: 1px solid #BDC3C7;  /* 浅灰边框 */
                    padding: 8px 16px;
                    font-size: 14px;
                }
                QPushButton:hover { background-color: #D5DBDB; }  /* 悬停效果 */
                QPushButton:pressed { background-color: #BFC9CA; } /* 按下效果 */
            """)
        self.btn_pass.clicked.connect(self.start_main)

        # 布局调整（增加间距）
        layout = QVBoxLayout()
        layout.addWidget(self.progress_bar)
        layout.addSpacing(20)  # 进度条与按钮间距
        layout.addWidget(self.btn_update)
        layout.addSpacing(10)  # 按钮间间距
        layout.addWidget(self.btn_pass)
        layout.setContentsMargins(30, 40, 30, 40)  # 窗口内边距

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_main(self):
        try:
            from WLW.LoginSystem import LoginWindow
            self.window = LoginWindow()
            self.window.show()
            self.close()
        except Exception as ex:
            QMessageBox.critical(self, "错误", f"启动失败: {str(ex)}")

    def start_download(self):
        self.btn_update.setEnabled(False)
        # download_url = "https://w7wp557v37c1.xiaomiqiu.com/downloads/2"
        temp_path = os.path.join(os.getenv("TEMP"), f"{self.wlw_dict['name']}.{self.wlw_dict['version']}.exe")
        logger.info(f'download_path: {temp_path}')

        self.download_thread = DownloadThread(self.wlw_dict['download_url'], temp_path)
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.error.connect(self.on_download_error)
        self.download_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_download_finished(self, exe_path):
        try:
            # 调用已经下载的安装软件，并设置安装路径为之前安装的路径
            subprocess.Popen([exe_path, f'/D={self.install_path}'])
            # 退出自动更新画面
            sys.exit(0)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"安装失败: {str(e)}")
        finally:
            self.btn_update.setEnabled(True)

    def on_download_error(self, message):
        QMessageBox.critical(self, "错误", f"下载失败: {message}")
        self.btn_update.setEnabled(True)
