# _*_ coding: utf-8 _*_
# @Time : 2026/11/21 星期六 19:14
# @Author : 韦丽
# @Version: V 1.0
# @File : StockColorDelegate.py
# @desc : 单元格字体样式设定
from PyQt6.QtWidgets import QStyledItemDelegate, QStyle
from PyQt6.QtGui import QPainter, QColor, QPalette, QFont
from PyQt6.QtCore import Qt, QRect

class StockColorDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_color = QColor("#e5e7eb")
        self.line_width = 1
        # ========= 核对你的列索引！！ =========
        self.col_zhangfu = 4  # 涨跌幅
        self.col_price = 5  # 最新价
        self.col_ftime = 12           # 首次涨停时间
        self.col_ltime = 13             # 最后涨停时间
        self.col_zhangting_stat = 15  # 涨停统计列 x/y

    def paint(self, painter, option, index):
        opt = option
        col = index.column()
        text = index.data(Qt.ItemDataRole.DisplayRole)
        text = str(text).strip() if text is not None else ""

        # 跳过光标
        is_selected = bool(opt.state & QStyle.StateFlag.State_Selected)
        is_hover = bool(opt.state & QStyle.StateFlag.State_MouseOver)
        if is_hover or is_selected:
            print(f'dddd')
            super().paint(painter, opt, index)
            return

        # ========= 单独处理【涨停统计列】（拆分颜色：前面红，/后面黑） =========
        if col == self.col_zhangting_stat and "/" in text:
            # 先画背景（选中底色、hover底色保留）
            style = opt.widget.style()
            style.drawPrimitive(QStyle.PrimitiveElement.PE_PanelItemViewItem, opt, painter, opt.widget)

            rect = opt.rect
            rect.adjust(3, 0, -3, 0)
            font = QFont(opt.font)
            painter.setFont(font)

            left_part, right_part = text.split("/", 1)
            # 斜杠前红色
            painter.setPen(QColor("red"))
            w1 = painter.fontMetrics().horizontalAdvance(left_part)
            painter.drawText(rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, left_part)
            # 斜杠+后面数字黑色
            new_rect = QRect(rect)
            new_rect.setLeft(rect.left() + w1)
            if opt.state & QStyle.StateFlag.State_Selected:
                painter.setPen(QColor("white"))
            else:
                painter.setPen(QColor("#111111"))
            painter.drawText(new_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, "/" + right_part)

            # 底部横线（和其它行保持一致）
            painter.save()
            total_rows = index.model().rowCount()
            if index.row() < total_rows - 1:
                pen = painter.pen()
                pen.setColor(self.line_color)
                pen.setWidth(self.line_width)
                pen.setStyle(Qt.PenStyle.SolidLine)
                painter.setPen(pen)
                painter.drawLine(opt.rect.bottomLeft(), opt.rect.bottomRight())
            painter.restore()
            print(f'15: {col}')
            return
        print(f'else: {col}')
        # ========= 下面是你原来的逻辑，只增加【涨跌幅、最新价加粗】 =========
        if opt.state & QStyle.StateFlag.State_Selected:
            opt.palette.setColor(QPalette.ColorRole.Text, QColor("white"))
        else:
            color = QColor("#111111")
            if col in (2, 3):
                color = QColor("blue")
            elif col == self.col_zhangfu:
                try:
                    val = float(text.replace("%", "").replace(",", ""))
                    if val < 0:
                        color = QColor("#009455")
                    else:
                        color = QColor("red")
                except ValueError:
                    color = QColor("#111111")
            elif col == self.col_price:
                color = QColor("red")
            opt.palette.setColor(QPalette.ColorRole.Text, color)

        # ✅ 加粗：涨跌幅、最新价
        if col in (self.col_ftime, self.col_ltime):
            bold_font = QFont(opt.font)
            bold_font.setBold(True)
            opt.font = bold_font

        # 原生绘制其他单元格
        super().paint(painter, opt, index)

        # 绘制横向分隔线（只画底部横线，你原来的逻辑不动）
        painter.save()
        total_rows = index.model().rowCount()
        if index.row() < total_rows - 1:
            pen = painter.pen()
            pen.setColor(self.line_color)
            pen.setWidth(self.line_width)
            pen.setStyle(Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.drawLine(opt.rect.bottomLeft(), opt.rect.bottomRight())
        painter.restore()
