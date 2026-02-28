# _*_ coding: utf-8 _*_
# @Time : 2025/12/31 星期三 20:23
# @Author : 韦丽
# @Version: V 1.0
# @File : eastmoneyBase.py
# @desc :
import json
import os
import time

import pymysql
from pymysql.cursors import DictCursor
from eastmoneyTools import now_date, logger_now_date

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)

# 获取所在文件夹路径
dir_path = str(os.path.dirname(script_path))

dir_path = dir_path.replace('\\', '/')

holidays=[]
contentHolidays = {}

# 配置文件读取
with open(f'{dir_path}\db_config.json') as f:
    config = json.load(f)

# 配置文件读取
with open(f'{dir_path}/2026_holidays.txt', 'r', encoding='utf-8') as reader:
    for content in reader:
        day = content.replace('\n', '').split(' # ')
        holidays.append(day[0])
        contentHolidays[day[0]]=day[1].split(' ')[1]

class EmBase:
    def __init__(self):
        # 初始化数据库连接参数
        self.mysql_host = config['database']['Host']
        self.mysql_port = int(config['database']['Port'])
        self.mysql_db = config['database']['Dbname']
        self.mysql_user = config['database']['User']
        self.mysql_pass = config['database']['Password']
        self.mysql_charset = config['database']['Charset']
        # 连接对象和游标
        self.conn = None
        self.cursor = None
        # 行业板块存储, 减少访问服务器的负担
        self.gridistHybkDict = self.read_existing_json()  # 加载已有的行业板块

    # 读取操作（行业板块）
    def read_existing_json(self):
        # 读取hybk.json文件中所有信息
        result = {}
        try:
            jsonPath = config['hybk']['output_file_path']
            self.gridistJsonFile = f'{jsonPath}hybk.json'
            with open(self.gridistJsonFile, 'r', encoding='utf-8') as r:
                for line in r:
                    line = line.strip()
                    if line:  # 跳过空行
                        result = dict(json.loads(line))
                        # result[data['f12']] = data['hybk']
        except (FileNotFoundError, json.JSONDecodeError):
            return dict()
        # print(f'result: {result}')
        return result

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

    # 判断当前日期是否是法定节假日
    def isExec(self):
        day = now_date()
        if day in holidays:
            print(f'{day}是节假日 {contentHolidays[day]}, 不进行数据采集。')
            time.sleep(8)
            return True
        return False

if __name__ == '__main__':
    em = EmBase()
    em.isExec()