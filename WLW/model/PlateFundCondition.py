# _*_ coding: utf-8 _*_
# @Time : 2025/8/26 星期二 8:29
# @Author : 韦丽
# @Version: V 1.0
# @File : PlateFundCondition.py
# @desc : 板块资金检索条件
class PlateFundCondition:
    def __init__(self, p_hangQingDateFrom, p_hangQingDateTo, p_plateFund_No, p_plateFund_Name, p_plateFund_zljlrje, p_condition_zljlrje, p_activateType, p_searchTime, p_hyType, p_orderByOption):
        self.hangQingDateFrom = p_hangQingDateFrom
        self.hangQingDateTo = p_hangQingDateTo
        self.plateFund_No = p_plateFund_No
        self.plateFund_Name = p_plateFund_Name
        self.plateFund_zljlrje = p_plateFund_zljlrje
        self.condition_zljlrje = p_condition_zljlrje
        self.activateType = p_activateType
        self.searchTime = p_searchTime
        self.hyType = p_hyType
        self.orderByOption = p_orderByOption
