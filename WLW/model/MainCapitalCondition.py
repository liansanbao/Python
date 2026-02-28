# 主流资金数据检索条件
class MainCapitalCondition:
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