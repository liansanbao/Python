# _*_ coding: utf-8 _*_
# @Time : 2026/1/21 星期三 18:28
# @Author : 韦丽
# @Version: V 1.0
# @File : NoticeInfoCondition.py
# @desc :
# 公告数据检索条件
class NoticesInfoCondition:
    def __init__(self, p_saleDayFrom, p_saleDayTo, p_stockNo, p_stockName, p_saleDateType, p_orderByOption):
        self.saleDayFrom = p_saleDayFrom
        self.saleDayTo = p_saleDayTo
        self.stockNo = p_stockNo
        self.stockName = p_stockName
        self.saleDateType = p_saleDateType
        self.orderByOption = p_orderByOption