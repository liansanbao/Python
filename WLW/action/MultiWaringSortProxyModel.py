# _*_ coding: utf-8 _*_
# @Time : 2025/7/18 星期五 10:42
# @Author : 韦丽
# @Version: V 1.0
# @File : MultiDailySortProxyModel.py
# @desc : QTableView 列排序自定义处理
from WLW.action.BaseProxyModel import BaseProxyModel


class CustomProxyModel(BaseProxyModel):
    def lessThan(self, left, right):
        # print(f'left.column(): {left.column()}, [{left.data()}, {right.data()}]')
        if left.column() == 0:
            return left.data() > right.data()
        # 日期列排序
        elif left.column() in [2, 5]:
            return left.data() < right.data()
        # 数值列排序
        elif left.column() in [6]:
            left_data = self.convertOtherStr(left.data())
            right_data = self.convertOtherStr(right.data())
            return left_data < right_data
        # 默认字符串排序
        return super().lessThan(left, right)
