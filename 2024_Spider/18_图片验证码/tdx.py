# _*_ coding: utf-8 _*_
# @Time : 2025/12/10 星期三 10:51
# @Author : 韦丽
# @Version: V 1.0
# @File : tdx.py
# @desc :

import os
from pytdx.hq import TdxHq_API


def modify_ma_color(stock_code, period='季线'):
    api = TdxHq_API()
    with api.connect('119.147.212.81', 7709):
        # 获取股票数据
        data = api.get_security_quotes([stock_code])
        if not data:
            print("未找到股票数据")
            return

        # 修改60日均线公式
        formula = f"MA(CLOSE,60),COLORFF0000,LINETHICK2;"  # 红色粗线
        api.modify_formula(stock_code, period, formula)
        print(f"已将{stock_code} {period} 60日均线颜色修改为红色")


if __name__ == "__main__":
    modify_ma_color('000001', '季线')  # 修改指定股票季线颜色
