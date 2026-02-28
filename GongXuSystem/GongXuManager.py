# _*_ coding: utf-8 _*_
# @Time : 2025/5/20 0020 20:59
# @Author : 韦丽
# @Version: V 1.0
# @File : GongXuManager.py
# @desc : 工序管理系统启动类

from PyQt5.QtWidgets import QApplication
import sys

from GongXuSystem import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

