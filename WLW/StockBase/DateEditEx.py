# _*_ coding: utf-8 _*_
# @Time : 2025/8/1 星期五 22:48
# @Author : 韦丽
# @Version: V 1.0
# @File : DateEditEx.py
# @desc : 重写QDateEdit

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import QDateEdit

class AutoSetDateEdit(QDateEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        """重写点击事件，在弹出日历前设置可选最大日期"""
        self.setMaximumDate(QDate.currentDate().addDays(0))
        super().mousePressEvent(event)   # 再触发默认点击行为
