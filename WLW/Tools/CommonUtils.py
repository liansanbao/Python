# _*_ coding: utf-8 _*_
# @Time : 2026/1/23 星期五 19:23
# @Author : 韦丽
# @Version: V 1.0
# @File : CommonUtils.py
# @desc : 系统工具类
from PyQt6.QtGui import QStandardItem

# 悬浮提示
def setQStandardItemPlateFund(text, index):
    # 主力B(净额)formate
    if index in [5]:
        if not (text.endswith('亿') or text.endswith('万') or text.endswith('元')):
            text = amountUnitEdit(text)
    item = QStandardItem(text)
    item.setToolTip(text)
    return item

# 净额数据单位编辑
def amountUnitEdit(strValue):
    # 例子：620811552.0 => 亿
    #      76256208.0 => 万
    #      66343.0 => 万
    try:
        strValue = str(int(strValue))
        # 长度为9的情况，可以转换成亿为单位
        if (len(strValue) >= 9):
            return f'{round(str_to_float(strValue) / 100000000, 2):.2f}亿'
        # 长度为5的情况，可以转换成万为单位
        elif (len(strValue) >= 5):
            return f'{round(str_to_float(strValue) / 10000, 2):.2f}万'
        else:
            return f'{str_to_float(strValue)}元'
    except Exception:
        return '0元'

# str转float
def str_to_float(str):
    result = float(0)
    try:
        result = float(str)
    except Exception as e:
        pass
    return result

# 悬浮提示
def setQStandardItem(showtext, toolTipText):
    item = QStandardItem(showtext)
    item.setToolTip(toolTipText)
    return item

def format_string(input_str, target_length):
    """
    格式化字符串：输出长度不足时用空格填充
    :param input_str: 输入字符串
    :param target_length: 目标长度
    :return: 格式化后的字符串
    """
    # 计算需要填充的空格数
    padding_length = target_length - len(input_str)

    # 使用空格填充
    if padding_length > 0:
        return input_str + '　' * padding_length
    else:
        return input_str[:target_length]
