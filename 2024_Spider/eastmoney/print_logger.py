# _*_ coding: utf-8 _*_
# @Time : 2025/10/29 星期三 21:24
# @Author : 韦丽
# @Version: V 1.0
# @File : print_logger.py
# @desc :
import os
import sys
import datetime
from typing import Optional


class PrintLogger:
    """使用print函数实现的日志记录器"""

    def __init__(self, name: str, instance=None):
        self.name = name
        self.instance = instance
        self.colors = {
            'INFO': '\033[94m',  # 蓝色
            'DEBUG': '\033[92m',  # 绿色
            'WARNING': '\033[93m',  # 黄色
            'ERROR': '\033[91m',  # 红色
            'RESET': '\033[0m'  # 重置
        }

    def _format_message(self, level: str, msg: str) -> str:
        """格式化日志消息"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        instance_info = f"[{self.instance.__class__.__name__}]" if self.instance else ""
        res_message = f"{self.colors[level]}[{timestamp}] {level}: {instance_info} {msg}{self.colors['RESET']}"
        print(res_message)
        return res_message

    def info(self, msg: str, *args, **kwargs):
        """信息级别日志"""
        formatted_msg = self._format_message('INFO', msg)

    def debug(self, msg: str, *args, **kwargs):
        """调试级别日志"""
        formatted_msg = self._format_message('DEBUG', msg)

    def warning(self, msg: str, *args, **kwargs):
        """警告级别日志"""
        formatted_msg = self._format_message('WARNING', msg)

    def error(self, msg: str, *args, **kwargs):
        """错误级别日志"""
        formatted_msg = self._format_message('ERROR', msg)

    def critical(self, msg: str, *args, **kwargs):
        """严重错误级别日志"""
        formatted_msg = self._format_message('ERROR', msg)  # 使用红色显示

    def exception(self, msg: str, *args, **kwargs):
        """异常级别日志"""
        formatted_msg = self._format_message('ERROR', msg)
        print(formatted_msg)
        import traceback
        traceback.print_exc()

class PrintLoggerAdapter:
    """PrintLogger的适配器，提供与logging.LoggerAdapter类似的接口"""

    def __init__(self, logger, extra):
        self.logger = logger
        self.extra = extra

    def info(self, msg: str, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def debug(self, msg: str, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        self.logger.critical(msg, *args, **kwargs)

class EastMoneyPlaywright:
    def __init__(self):
        self.execType = "gridist_crawl"

    @property
    def logger(self):
        # 创建PrintLogger实例
        print_logger = PrintLogger(self.execType, self)
        # 返回适配器以保持接口兼容
        return PrintLoggerAdapter(print_logger, {"EastMoneyPlaywright": self})

    def collect_sector_funds(self):
        """采集板块资金流数据"""
        self.logger.info("开始采集板块资金流数据")
        # 模拟数据采集过程
        import time
        time.sleep(1)
        self.logger.info("板块资金流数据采集完成")
        return {"sector": "金融", "funds": "1.2亿"}

    def collect_concept_data(self):
        """采集概念数据"""
        self.logger.debug("开始采集概念数据")
        # 模拟数据采集过程
        return {"concept": "人工智能", "stocks": 50}

    def collect_gainers_data(self):
        """采集涨幅4%以上数据"""
        self.logger.warning("注意：涨幅数据可能包含延迟")
        return {"stock": "AAPL", "gain": "4.5%"}

    def run_all_tasks(self):
        """运行所有采集任务"""
        self.logger.info("=== 开始东方财富网数据采集 ===")

        try:
            # 采集板块资金流数据
            sector_data = self.collect_sector_funds()
            self.logger.info(f"板块资金流数据: {sector_data}")

            # 采集概念数据
            concept_data = self.collect_concept_data()
            self.logger.debug(f"概念数据: {concept_data}")

            # 采集涨幅数据
            gainers_data = self.collect_gainers_data()
            self.logger.info(f"涨幅数据: {gainers_data}")

            self.logger.info("=== 数据采集任务完成 ===")

        except Exception as e:
            self.logger.error(f"数据采集失败: {e}")

def main():
    """主函数 - 演示PrintLogger的使用"""
    emp = EastMoneyPlaywright()

    # 测试不同级别的日志输出
    emp.logger.info("这是一条信息级别的日志")
    emp.logger.debug("这是一条调试级别的日志")
    emp.logger.warning("这是一条警告级别的日志")
    emp.logger.error("这是一条错误级别的日志")

    # 运行采集任务
    emp.run_all_tasks()


if __name__ == "__main__":
    main()
