# 涨停板数据检索条件
class StockInfoCondition:
    def __init__(self, p_saleDayFrom, p_saleDayTo, p_stockNo, p_stockName, p_lianBanShu, p_huanShouLv, p_zhangTingCiShu, p_youZiYouWu, p_suoShuHangYe, p_zhaBanCiShu, p_stockType,
                 p_le_ztzt, p_le_zxj, p_condition_zxj, p_condition_lbs, p_condition_hsl, p_condition_ztcs, p_condtion_zbcs, p_saleDateType, p_orderByOption):
        self.saleDayFrom = p_saleDayFrom
        self.saleDayTo = p_saleDayTo
        self.stockNo = p_stockNo
        self.stockName = p_stockName
        self.lianBanShu = p_lianBanShu
        self.huanShouLv = p_huanShouLv
        self.zhangTingCiShu = p_zhangTingCiShu
        self.youZiYouWu = p_youZiYouWu
        self.suoShuHangYe = p_suoShuHangYe
        self.zhaBanCiShu = p_zhaBanCiShu
        self.stockType = p_stockType
        self.le_ztzt = p_le_ztzt
        self.le_zxj = p_le_zxj
        self.condition_zxj = p_condition_zxj
        self.condition_lbs = p_condition_lbs
        self.condition_hsl = p_condition_hsl
        self.condition_ztcs = p_condition_ztcs
        self.condtion_zbcs = p_condtion_zbcs
        self.saleDateType = p_saleDateType
        self.orderByOption = p_orderByOption