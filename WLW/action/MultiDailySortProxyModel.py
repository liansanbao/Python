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
        left_val = self.get_safe_data(left)
        right_val = self.get_safe_data(right)
        # 日期列排序
        if left.column() == 0:
            return left_val < right_val
        # 数值列排序
        elif left.column() in [2, 4, 5, 7, 10, 11, 14, 18]:
            left_data = self.convertOtherStr(left_val)
            right_data = self.convertOtherStr(right_val)
            return left_data < right_data
        # 默认字符串排序
        return super().lessThan(left, right)
