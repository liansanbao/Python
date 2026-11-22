# _*_ coding: utf-8 _*_
# @Time : 2026/11/22 星期日 12:05
# @Author : 韦丽
# @Version: V 1.0
# @File : CustomVerticalHeader.py
# @desc : 行号处理
from PyQt6.QtWidgets import QHeaderView
from PyQt6.QtGui import QPainter, QBrush, QColor
from PyQt6.QtCore import Qt, pyqtSignal

class CustomVerticalHeader(QHeaderView):
    sectionClicked = pyqtSignal(int)
    def __init__(self, parent=None):
        super().__init__(Qt.Orientation.Vertical, parent)
        self.selected_row = -1
        self.setHighlightSections(False)
        self.start_offset = 0   # ✅ 新增：行号起始偏移，默认0，第一页
        self.font = self.font()


    # ✅ 对外接口：翻页的时候调用这个，设置偏移
    def setStartOffset(self, offset:int):
        self.start_offset = offset
        self.update()  # 立刻重绘表头

    def clearSelectedRow(self):
        self.selected_row = -1
        self.update()

    def paintSection(self, painter, rect, logicalIndex):
        painter.save()
        # 背景绘制
        if logicalIndex == self.selected_row:
            painter.fillRect(rect, QColor("#b8d0ee"))
        else:
            painter.fillRect(rect, QColor("transparent"))

        # ✅ 核心：连续行号计算公式
        show_num = self.start_offset + logicalIndex + 1
        painter.setFont(self.font)
        painter.setPen(QColor("#222222"))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(show_num))
        painter.restore()
