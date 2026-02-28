# _*_ coding: utf-8 _*_
# @Time : 2025/10/1 星期三 19:02
# @Author : 韦丽
# @Version: V 1.0
# @File : LoadingOverlay.py
# @desc :
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QMovie

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        if parent and not isinstance(parent, QWidget):
            parent = None  # 非QWidget父对象时强制设为None
        super().__init__(parent)
        self.task_completed = False  # 新增任务状态标志

    def setup_ui(self):
        # 确保覆盖层在最上层
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 半透明背景
        # self.setStyleSheet("background-color: rgba(0, 0, 0, 300);")

        # 居中布局
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 动画标签
        self.loading_label = QLabel()
        self.movie = QMovie("loading.gif")
        self.movie.setScaledSize(QSize(190, 190))
        self.loading_label.setMovie(self.movie)
        layout.addWidget(self.loading_label)

        # 初始隐藏
        self.hide()

    def set_task_complete(self):
        self.task_completed = True

    def show_overlay(self):
        """显示覆盖层并开始动画"""
        if self.parent():
            self.setGeometry(0, 0,
                             self.parent().width(),
                             self.parent().height())
        self.raise_()  # 提升到最上层
        self.show()
        self.movie.start()
