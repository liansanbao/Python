# _*_ coding: utf-8 _*_
# @Time : 2026/1/23 星期五 19:23
# @Author : 韦丽
# @Version: V 1.0
# @File : CommonUtils.py
# @desc : 系统工具类
from PyQt6.QtGui import QStandardItem


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
