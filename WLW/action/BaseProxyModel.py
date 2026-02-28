# _*_ coding: utf-8 _*_
# @Time : 2025/8/29 星期五 16:08
# @Author : 韦丽
# @Version: V 1.0
# @File : BaseProxyModel.py
# @desc : QTableView 列排序自定义处理(父类)
from PyQt6.QtCore import QSortFilterProxyModel

class BaseProxyModel(QSortFilterProxyModel):
    def convertOtherStr(self, keyStr: str = ''):
        if keyStr == '-' or keyStr == '':
            return float(0)
        """解析带单位的数值字符串为浮点数"""
        s = keyStr.strip().replace(',', '')
        if '亿' in s:
            return float(s.replace('亿', '')) * 1e8
        elif '万' in s:
            return float(s.replace('万', '')) * 1e4
        elif '元' in s:
            return float(s.replace('元', ''))
        elif '%' in s:
            return float(s.replace('%', ''))
        else:
            return float(s)
        # return keyStr.replace('%', '').replace('亿', '').replace('万', '').replace('元', '')
