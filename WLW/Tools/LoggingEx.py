# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/2/25 15:20
# @Author : 连三保
# @Version: V 1.0
# @File : LoggingEx.py
# @desc : 关于日志输出的工具类
import configparser
import logging
import os
from logging.handlers import RotatingFileHandler

'''
Filename：指定路径的文件。这里使用了+—name—+是将log命名为当前py的文件名
Format：设置log的显示格式（即在文档中看到的格式）。分别是时间+当前文件名+log输出级别+输出的信息
Level：输出的log级别，优先级比设置的级别低的将不会被输出保存到log文档中
Filemode： log打开模式
    a：代表每次运行程序都继续写log。即不覆盖之前保存的log信息。
    w：代表每次运行程序都重新写log。即覆盖之前保存的log信息
'''

# 读取配置文件
config = configparser.ConfigParser()
config.read('./_internal/config/config.ini', 'utf-8')  # 确保config.ini文件存在

# 获取日志配置（带默认值）
log_dir = config.get('LOGGING', 'log_dir', fallback='_internal\\log')
max_size = config.getint('LOGGING', 'max_bytes', fallback=5*1024*1024)
backup_count = config.getint('LOGGING', 'backup_count', fallback=3)

# 确保日志目录存在
os.makedirs(log_dir, exist_ok=True)

# 创建RotatingFileHandler
handler = RotatingFileHandler(
    filename=os.path.join(log_dir, 'WLW.log'),
    encoding='utf-8',
    maxBytes=max_size,
    backupCount=backup_count,
    mode='a'
)

# 设置日志格式
formatter = logging.Formatter(
    "%(asctime)s %(name)s %(levelname)s %(message)s",
    datefmt='%Y-%m-%d %I:%M:%S %p'
)
handler.setFormatter(formatter)

# 配置根logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

class LoggingEx(logging.Handler):
    def __init__(self):
        super().__init__()
        # 给此handler定义日志的格式
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        self.setFormatter(formatter)

    def emit(self, record: logging.LogRecord) -> None:
        # 日志处理函数， 格式化日志数据后，写入大
        msg = self.format(record)

# 创建一个logger实例， 其它模块引用该实例
logger = logging.getLogger()