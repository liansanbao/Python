# _*_ coding: utf-8 _*_
# @Time : 2025/10/21 星期二 20:20
# @Author : 韦丽
# @Version: V 1.0
# @File : AutoSetNumberLineEdit.py
# @desc : 数值输入

from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression


class AutoSetNumberLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

    def setIntegerOnly(self):
        """设置只能输入整数"""
        # 使用正则表达式严格限制只能输入数字
        pattern = f"^\\d*$"
        regex = QRegularExpression(pattern)
        validator = QRegularExpressionValidator(regex, self)
        self.setValidator(validator)

    def setNumberWithRange(self, max_val=6):
        """设置只能输入指定范围的数字"""
        pattern = "[0-9]{" + str(max_val)+ "}"
        regex = QRegularExpression(pattern)
        validator = QRegularExpressionValidator(regex, self)
        self.setValidator(validator)

    def setNumberWithRangeBK(self, max_val=6):
        """设置只能输入指定范围的数字"""
        pattern = "^BK[0-9]{" + str(max_val)+ "}$"
        regex = QRegularExpression(pattern)
        validator = QRegularExpressionValidator(regex, self)
        self.setValidator(validator)

    def setDecimalOnly(self, allow_negative=False):
        """设置只能输入数字（包括小数）"""
        if allow_negative:
            pattern = "^-?\\d*\\.?\\d*$"
        else:
            pattern = "^\\d*\\.?\\d*$"

        regex = QRegularExpression(pattern)
        validator = QRegularExpressionValidator(regex, self)
        self.setValidator(validator)


# 使用示例
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel


    class DemoWidget(QWidget):
        def __init__(self):
            super().__init__()
            self.initUI()

        def initUI(self):
            layout = QVBoxLayout()

            # 只能输入整数
            self.intEdit = AutoSetNumberLineEdit()
            self.intEdit.setIntegerOnly()
            self.intEdit.setPlaceholderText("只能输入数字0-9")

            # 只能输入0-6范围内的数字
            self.rangeEdit = AutoSetNumberLineEdit()
            self.rangeEdit.setNumberWithRange(6)
            self.rangeEdit.setPlaceholderText("只能输入0-6范围内的数字")

            layout.addWidget(QLabel("整数输入框:"))
            layout.addWidget(self.intEdit)
            layout.addWidget(QLabel("范围输入框:"))
            layout.addWidget(self.rangeEdit)

            self.setLayout(layout)
            self.setWindowTitle("数字输入框示例")
            self.resize(300, 150)


    app = QApplication(sys.argv)
    window = DemoWidget()
    window.show()
    sys.exit(app.exec())


