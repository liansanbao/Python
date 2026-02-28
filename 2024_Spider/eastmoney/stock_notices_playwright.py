# _*_ coding: utf-8 _*_
# @Time : 2026/1/6 星期二 20:46
# @Author : 韦丽
# @Version: V 1.0
# @File : stock_notices_playwright.py
# @desc : 个股公告数据采集

import json
import logging
import os
import sys
import time

from eastmoneyBase import EmBase

from eastmoneyTools import str_to_json, now_date, logger_now_date, format_ymdhms
from playwright.sync_api import sync_playwright

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)

# 获取所在文件夹路径
dir_path = str(os.path.dirname(script_path))

dir_path = dir_path.replace('\\', '/')

# 配置文件读取
with open(f'{dir_path}\db_config.json') as f:
    config = json.load(f)

# 获取日志配置（带默认值）
log_dir = config['logging']['log_dir']

# 确保日志目录存在
os.makedirs(log_dir, exist_ok=True)

'''
    要求：
        东方财富网数据采集
            A股公告数据
'''
class StockNoticesPlaywright(EmBase):
    # 构造函数
    def __init__(self, stockNo, maxPage):
        self.stockNo = stockNo
        self.url = f'https://data.eastmoney.com/notices/stock/{stockNo}.html'
        self.max_pages = maxPage
        self.result_data = []
        self._setup_logging()

    def _setup_logging(self):
        # 创建唯一logger，以股票代码区分
        logger_name = f"{self.__class__.__name__}_{self.stockNo}"
        self._logger = logging.getLogger(logger_name)
        self._logger.setLevel(logging.DEBUG)

        # 避免重复添加handler
        if not self._logger.handlers:
            # 1. 文件处理器 - 固定文件输出
            file_handler = logging.FileHandler(
                os.path.join(log_dir, f'{self.__class__.__name__}_{self.stockNo}.log'),
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self._logger.addHandler(file_handler)

            # 2. 控制台处理器 - 带颜色输出
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)

            # 彩色格式定义
            class ColorFormatter(logging.Formatter):
                COLORS = {
                    'DEBUG': '\033[94m',  # 蓝色
                    'INFO': '\033[92m',  # 绿色
                    'WARNING': '\033[93m',  # 黄色
                    'ERROR': '\033[91m',  # 红色
                    'CRITICAL': '\033[95m',  # 紫色
                }
                RESET = '\033[0m'

                def format(self, record):
                    log_message = super().format(record)
                    color = self.COLORS.get(record.levelname, self.RESET)
                    message = f"{color}{log_message}{self.RESET}"
                    # print(message)
                    return message

            console_formatter = ColorFormatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            self._logger.addHandler(console_handler)

    @property
    def logger(self):
        return self._logger

    def log(self, message, level=logging.DEBUG, **kw):
        # 简化的日志调用方法
        self._logger.log(level, message, **kw)

    def debug(self, message, **kw):
        """记录debug级别日志"""
        self._logger.debug(message, **kw)

    def info(self, message, **kw):
        """记录info级别日志"""
        self._logger.info(message, **kw)

    def warning(self, message, **kw):
        """记录warning级别日志"""
        self._logger.warning(message, **kw)

    def error(self, message, **kw):
        """记录error级别日志"""
        self._logger.error(message, **kw)

    # 数据采集
    def exec(self):
        try:
            """爬虫程序的入口函数"""
            with sync_playwright() as p:
                # 连接本地启动的浏览器
                self.browser = p.chromium.launch_persistent_context(
                    executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                    user_data_dir=r'D:\chrome_userData',  # 在D盘根目录下创建chrome_userData文件夹
                    headless=False)

                # 选择默认打开的页面
                self.search_page = self.browser.new_page()
                # 添加初始化js脚本代码，隐藏webdriver属性，防止检测出来
                js = "Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});"
                self.search_page.add_init_script(js)
                # 给playwright添加响应事件的侦听处理函数
                self.search_page.on('response', self.notices_response)
                """爬虫执行的主要逻辑"""
                try:
                    self.search_page.goto(self.url, wait_until="domcontentloaded")
                except:
                    self.search_page.goto(self.url, wait_until="domcontentloaded")

                self.search_page.wait_for_timeout(4000)
                try:
                    # 处理自动弹出开户对话框
                    if self.search_page.wait_for_selector('img[onclick="tk_tg_zoomin()"]', timeout=5000):
                        # 点击关闭按钮
                        self.search_page.locator('img[onclick="tk_tg_zoomin()"]').click()
                except:
                    self.logger.error('自动弹框出错了！')

                self.search_page.wait_for_timeout(5000)

                # 关闭页面
                self.search_page.close()

            # 有行业的股票数据保存
            if self.result_data:
                self.logger.info(f'{self.stockNo} 一共采集 {len(self.result_data)} 件')
        except Exception as ex:
            print(f"{logger_now_date()} 数据采集错误： {str(ex)}")

        return self.result_data

    # 服务器响应处理
    def notices_response(self, response):
        try:
            request_url = response.url
            # 个股公告数据：https://np-anotice-stock.eastmoney.com/api/security/ann?cb=jQuery112302258340068044008_1767700619151&sr=-1&page_size=50&page_index=3&ann_type=A&client_source=web&stock_list=002183&f_node=0&s_node=0
            if response.headers.get('content-type') == 'text/plain;charset=UTF-8' and request_url.find(
                    '/api/security/ann') != -1:
                # print(f'个股公告数据: {request_url}')
                # 个股公告数据
                self.parseNotices(response)

        except Exception as ex:
            print(f'{logger_now_date()} 服务器响应处理错误: {str(ex)}')

    # 个股公告数据
    def parseNotices(self, response):
        try:
            # 当日日期 yyyymmdd
            now_ymd = now_date('%Y-%m-%d')
            json_data = str_to_json(response.body())
            result = json_data["data"]
            if result:
                diff_value = result["list"]  # 安全访问 'list' 字段
                for item in diff_value:
                    notice_date = format_ymdhms(item['notice_date'], '%Y-%m-%d %H:%M:%S', '%Y-%m-%d')
                    # 公告时间必须大于等于当前系统时间
                    if now_ymd <= notice_date:
                        item['notice_date'] = notice_date
                        self.editFields(item)
        except Exception as ex:
            raise Exception(f'板块资金流数据抓取错误: {str(ex)}')

    # 采集数据编辑
    def editFields(self, item):
        try:
            notice_item = {}
            codes = item['codes'][0]
            # art_code
            notice_item["公告详情"] = f"https://data.eastmoney.com/notices/detail/{self.stockNo}/{item['art_code']}.html"
            # 公告日期
            notice_item["公告日期"] = item['notice_date']
            # 公告标题
            notice_item["公告标题"] = item['title']
            # 股票代码
            notice_item["股票代码"] = codes['stock_code']
            # 股票名称
            notice_item["股票名称"] = codes['short_name']
            # 公告类型
            if item['columns'] != None and len(item['columns']) > 0:
                notice_item["公告类型"] = item['columns'][0]['column_name']
            else:
                notice_item["公告类型"] = ''
            # print(f"{codes['stock_code']}_{codes['short_name']}: {notice_item}")

            self.result_data.append(notice_item)
        except Exception as ex:
            self.logger.error(f'数据处理对象: {item}')
            self.logger.error(f'{item["art_code"]}_数据编辑错误: {str(ex)}')

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

if __name__ == '__main__':
    result_data = {}
    # 资产数据读取
    stockNos = str(config['stockNos']).split(',')
    print(f'需要采集的股票: {stockNos}')
    if stockNos:
        for stock in stockNos:
            es = StockNoticesPlaywright(stock, 0)
            data = es.exec()
            if data:
                stockName = format_string(data[0]['股票名称'], 4)
                result_data[f"({data[0]['股票代码']}_{stockName}) -> {data[0]['公告日期']}"] = data
                es.logger.info(f"{data[0]['股票代码']}_{stockName}: {data}")

        # 有行业的股票数据保存
        if result_data:
            now_ymd = now_date('%Y-%m-%d')
            jsonFile = f'{dir_path}/StockNotices/notices_{now_ymd}.json'
            with open(jsonFile, 'w', encoding='utf-8') as w:
                for key, val in result_data.items():
                    json_data = json.dumps(f'<>{key}<>', ensure_ascii=False, indent=2) + ', \n'
                    w.write(json_data)
                    for item in val:
                        # 不显示的内容
                        item = {"公告详情": item["公告详情"], "公告类型": item["公告类型"], "公告标题": item["公告标题"]}
                        json_data = json.dumps(f'　　　　{item}', ensure_ascii=False, indent=2) + ', \n'
                        w.write(json_data)

            print(f'所有资产公告数据采集完毕！ {jsonFile}')
            time.sleep(10)

    sys.exit()
