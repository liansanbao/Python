# _*_ coding: utf-8 _*_
# @Time : 2025/4/26 10:17
# @Author : 韦丽
# @Version: V 1.0
# @File : holidays_playwright.py
# @desc : 中国公共假期数据取得：https://publicholidays.cn/zh/2025-dates/
import json
import os
import sys
from datetime import datetime, timedelta
import pymysql
from pymysql.cursors import DictCursor
from playwright.sync_api import sync_playwright

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)

# 获取所在文件夹路径
dir_path = str(os.path.dirname(script_path))

dir_path = dir_path.replace('\\', '/')

# 配置文件读取
with open(f'{dir_path}\db_config.json') as f:
    config = json.load(f)


def logger_now_date():
    return datetime.now().strftime("%Y.%m.%d %H:%M:%S.%f")

# 日期format return 09:25:00
def format_ymdhms(ymdhms: str = '2026-01-07 00:00:00', startF: str = '%Y-%m-%d %H:%M:%S', endF: str = '%Y-%m-%d'):
    # print(type(hms), hms)
    return datetime.strptime(ymdhms, startF).strftime(endF)

'''
    要求：
        1.数据内容应该包括：'放假时间','星期','假日名称'
        2.数据保存：txt一份
'''
class PublicHolidays(object):
    # 构造函数
    def __init__(self, year):
        # 初始化数据库连接参数
        self.mysql_host = config['database']['Host']
        self.mysql_port = int(config['database']['Port'])
        self.mysql_db = config['database']['Dbname']
        self.mysql_user = config['database']['User']
        self.mysql_pass = config['database']['Password']
        self.mysql_charset = config['database']['Charset']
        self.year = year
        # 连接对象和游标
        self.conn = None
        self.cursor = None
        self.result_data = []
        # 板块资金流向表数据插入
        self.insert_china_holidays = f"""
                INSERT INTO China_Holidays (
                   year,
                   month,
                   holidays,
                   holidays_content
                ) VALUES (%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                   year = VALUES(year),
                   month = VALUES(month),
                   holidays = VALUES(holidays),
                   holidays_content = VALUES(holidays_content)
                """

    def exec(self):
        self.detail_data = []
        """爬虫程序的入口函数"""
        with sync_playwright() as p:
            try:
                # 连接本地启动的浏览器
                browser = p.chromium.launch(headless=False,
                                  executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                                  args=['--start-maximized'])

                self.url = f'https://publicholidays.cn/zh/{self.year}-dates/'

                # 选择默认的浏览器上下文对象
                self.context = browser.new_context(no_viewport=True)
                # 选择默认打开的页面
                self.page = self.context.new_page()
                # 添加初始化js脚本代码，隐藏webdriver属性，防止检测出来
                js = "Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});"
                self.page.add_init_script(js)
                """爬虫执行的主要逻辑"""
                try:
                    self.page.goto(self.url, wait_until="domcontentloaded")
                except:
                    self.page.goto(self.url, wait_until="domcontentloaded")

                self.page.wait_for_timeout(5000)

                years={2026: 1, 2027: 3, 2028: 5}
                tableNo = years[self.year]

                # 数据不存在，跳过
                if self.page.locator(f'//table[{tableNo}]').count() > 0:
                    # 放假时间
                    holidays_list = [self.getInnerText(td) for td in self.page.locator(f'//table[{tableNo}]//tbody//td[1]').all()]
                    # 星期
                    holidaysWeek_list = [self.getInnerText(td) for td in self.page.locator(f'//table[{tableNo}]//tbody//td[2]').all()]
                    # 假日名称
                    holidaysName_list = [self.getInnerText(td) for td in self.page.locator(f'//table[{tableNo}]//tbody//td[3]').all()]

                    holidays = zip(holidays_list, holidaysWeek_list, holidaysName_list)
                    for day in holidays:
                        if '～' in day[0]:
                            new_days = self.get_full_date_range(day[0], self.year)
                            for newday in new_days:
                                # 20260101 # 周四 2026年元旦
                                self.detail_data.append([newday[0], f'# {newday[1]} {self.year}年{day[2]}'])
                                dbDay = format_ymdhms(newday[0], '%Y%m%d', '%Y-%m-%d')
                                self.result_data.append([self.year, newday[2], dbDay, f'{self.year}年{day[2]}'])
                        else:
                            holiday = self.convert_to_yyyymmdd(day[0], self.year)
                            # 20260101 # 周四 2026年元旦
                            self.detail_data.append([holiday, f'# {day[1]} {self.year}年{day[2]}'])
                            dbDay = format_ymdhms(holiday, '%Y%m%d', '%Y-%m-%d')
                            dbMonth = format_ymdhms(holiday, '%Y%m%d', '%m')
                            self.result_data.append([self.year, dbMonth, dbDay, f'{self.year}年{day[2]}'])
                # 关闭页面
                self.page.close()
            except Exception as e:
                print(f'连接失败： {e}')

        # 出力txt文件
        self.save_txt()
        # 数据入库
        self.writeMysql(self.result_data)

    # 打开mysql数据库链接
    def open_mysql(self):
        # 打开连接
        self.conn = pymysql.connect(
            host=self.mysql_host,
            port=self.mysql_port,
            user=self.mysql_user,
            password=self.mysql_pass,
            db=self.mysql_db,
            charset=self.mysql_charset,
            cursorclass=DictCursor
        )
        self.cursor = self.conn.cursor()
        print(f'{logger_now_date()} MYSQL已经打开了，可以写数据了！！！')

    # 关闭数据库连接
    def close_mysql(self):
        # 关闭数据库连接
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print(f'{logger_now_date()} MYSQL关闭了，数据记载完了！！！')

    # 数据入库
    def writeMysql(self, data):
        # 根据item中的操作类型执行不同SQL
        try:
            # 事务开启
            self.open_mysql()
            for item in data:
                mysql_dict = (item[0], item[1], item[2], item[3])
                self.cursor.execute(self.insert_china_holidays, mysql_dict)
            self.conn.commit()  # 提交事务
        except pymysql.Error as e:
            print(f'{logger_now_date()} 数据登录失败！！！{str(e)}')
            self.conn.rollback()  # 回滚事务
        finally:
            print(f'{logger_now_date()} 数据登录成功！！！')
            self.close_mysql()

    """
        将中文日期范围转换为 YYYYMMDD 格式的日期列表，包含起始到结束的所有日期。
    
        :param date_range_str: 输入字符串，如 "1月28日 ～ 2月4日"
        :param year: 起始年份（默认当前年）
        :return: YYYYMMDD 格式的日期列表，如 ["20240128", "20240129", ..., "20240204"]
    """
    def get_full_date_range(self, date_range_str: str, year: int = None) -> list[list]:
        # 分割起始和结束日期
        start_str, end_str = [s.strip().replace("日", "") for s in date_range_str.split("～")]
        weeksName = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']

        # 解析月份和日期
        def parse_part(part: str) -> tuple[int, int]:
            month, day = part.split("月")
            return int(month), int(day)

        start_month, start_day = parse_part(start_str)
        end_month, end_day = parse_part(end_str)

        # 确定起始年份（默认当前年）
        current_year = year if year is not None else datetime.now().year

        # 处理跨年逻辑（如12月到1月）
        if end_month < start_month:
            end_year = current_year + 1
        else:
            end_year = current_year

        # 生成日期对象
        try:
            start_date = datetime(current_year, start_month, start_day)
            end_date = datetime(end_year, end_month, end_day)
        except ValueError as e:
            raise ValueError(f"非法日期: {e}")

        # 计算日期范围
        if start_date > end_date:
            raise ValueError("结束日期早于起始日期")

        all_dates = []
        current_date = start_date
        while current_date <= end_date:
            all_dates.append([current_date.strftime("%Y%m%d"), weeksName[current_date.weekday()], current_date.strftime("%m")])
            current_date += timedelta(days=1)

        return all_dates

    # 字符串XX月XX日转YYYYMMDD
    def convert_to_yyyymmdd(self, date_str: str, year: int=None) -> str:
        # 获取当年年份
        year = year or datetime.now().year
        try:
            # 解析月日部分，自动补零
            date_obj = datetime.strptime(date_str, "%m月%d日")
            # 替换为指定年份， 并格式化为yyyymmdd
            return date_obj.replace(year=year).strftime("%Y%m%d")
        except ValueError as e:
            print(f'无效日期格式或非法日期: {date_str}')

    # text值取得
    def getInnerText(self, li):
        text_list = li
        try:
            if text_list.count() > 0:
                return text_list.inner_text().replace('\xa0', ' ')
        except:
            pass
        return ''

    # 出力txt文件
    def save_txt(self):
        with open(f'{self.year}_holidays.txt', 'w', encoding='utf-8') as w:
            for day in self.detail_data:
                str = ' '.join(day) + '\n'
                print(str)
                w.write(str)

if __name__ == '__main__':
    publicHolidays = PublicHolidays(2026)
    publicHolidays.exec()
    sys.exit()

