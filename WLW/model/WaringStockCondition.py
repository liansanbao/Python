# 主流资金数据检索条件
class WaringStockCondition:
    def __init__(self, p_cDateFrom, p_cDateTo, p_waringStockNo, p_waringStockName, p_waringHangYe, p_waringStockType, p_orderByOption):
        self.cDateFrom = p_cDateFrom
        self.cDateTo = p_cDateTo
        self.waringStockNo = p_waringStockNo
        self.waringStockName = p_waringStockName
        self.waringHangYe = p_waringHangYe
        self.waringStockType = p_waringStockType
        self.orderByOption = p_orderByOption