# _*_ coding: utf-8 _*_
# @Time : 2025/8/26 星期二 8:57
# @Author : 韦丽
# @Version: V 1.0
# @File : MultiPlateFundSortProxyModel.py
# @desc : QTableView 列排序自定义处理
from WLW.action.BaseProxyModel import BaseProxyModel

class CustomProxyModel(BaseProxyModel):
    def lessThan(self, left, right):
        # print(f'left.column(): {left.column()}, [{left.data()}, {right.data()}]')
        # 日期列排序
        if left.column() == 0:
            return left.data() < right.data()
        # 数值列排序
        elif left.column() in [3, 4, 5, 6, 8, 9, 13, 14, 15, 16, 17]:
            left_data = self.convertOtherStr(left.data())
            right_data = self.convertOtherStr(right.data())
            return left_data < right_data
        # 默认字符串排序
        return super().lessThan(left, right)
