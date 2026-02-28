# _*_ coding: utf-8 _*_
# @Time : 2025/8/23 星期六 10:28
# @Author : 韦丽
# @Version: V 1.0
# @File : IncreaseFiveCondition.py
# @desc : 涨幅(5%)以上检索条件
class IncreaseFiveCondition:
    # 涨幅(5%)以上检索条件
    def __init__(self, p_hangQingDateFrom, p_hangQingDateTo, p_masterStockNo, p_masterStockName, p_masterHangYe, p_masterZhangFu, p_masterXianJia,
                 p_masterStockType, p_condition_xj, p_saleDateType, p_orderByOption):
        self.hangQingDateFrom = p_hangQingDateFrom
        self.hangQingDateTo = p_hangQingDateTo
        self.masterStockNo = p_masterStockNo
        self.masterStockName = p_masterStockName
        self.masterHangYe = p_masterHangYe
        self.masterZhangFu = p_masterZhangFu
        self.masterXianJia = p_masterXianJia
        self.masterStockType = p_masterStockType
        self.condition_xj = p_condition_xj
        self.saleDateType = p_saleDateType
        self.orderByOption = p_orderByOption

    # 持股机构总览数据检索条件
    def initInstitution(self, p_institutionType, p_reportDate, p_stockNo):
        self.institutionType = p_institutionType
        self.reportDate = p_reportDate
        self.stockNo = p_stockNo
