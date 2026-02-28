# _*_ coding: utf-8 _*_
# @Time : 2025/11/13 星期四 21:22
# @Author : 韦丽
# @Version: V 1.0
# @File : gridist_playwright.py
# @desc :
import datetime
import json
import os
import sys
import time

import pymysql

from eastmoneyTools import str_to_json, str_to_int, amountUnitEdit, logger_now_date
from playwright.sync_api import sync_playwright
from eastmoneyBase import EmBase

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)

# 获取所在文件夹路径
dir_path = str(os.path.dirname(script_path))

dir_path = dir_path.replace('\\', '/')

# 配置文件读取
with open(f'{dir_path}\db_config.json') as f:
    config = json.load(f)

'''
    要求：
        东方财富网数据采集
            沪深京A股数据（ST除外）
'''
class GridistPlaywright(EmBase):
    # 构造函数
    def __init__(self, url, maxPage):
        # 初始化数据库连接参数
        self.mysql_host = config['database']['Host']
        self.mysql_port = int(config['database']['Port'])
        self.mysql_db = config['database']['Dbname']
        self.mysql_user = config['database']['User']
        self.mysql_pass = config['database']['Password']
        self.mysql_charset = config['database']['Charset']
        self.proxy_config = {
            "server": "http://proxy.ipipgo.io:24000",
            "username": "your_username",
            "password": "your_password"
        }
        self.url = url
        self.max_pages = maxPage
        self.isContinueExec = True
        # 连接对象和游标
        self.conn = None
        self.cursor = None
        # 大盘主力资金表数据插入
        self.insert_gridist_stock_sql = f"""
            INSERT INTO GRIDIST_STOCK (
               CREATE_DATE,
               F12,
               F14,
               F2,
               F3,
               F4,
               F5,
               F6,
               F7,
               F8,
               F9,
               F10,
               F15,
               F16,
               F17,
               F18,
               F23,
               hybk
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
               CREATE_DATE = VALUES(CREATE_DATE),
               F12 = VALUES(F12),
               F14 = VALUES(F14),
               F2 = VALUES(F2),
               F3 = VALUES(F3),
               F4 = VALUES(F4),
               F5 = VALUES(F5),
               F6 = VALUES(F6),
               F7 = VALUES(F7),
               F8 = VALUES(F8),
               F9 = VALUES(F9),
               F10 = VALUES(F10),
               F15 = VALUES(F15),
               F16 = VALUES(F16),
               F17 = VALUES(F17),
               F18 = VALUES(F18),
               F23 = VALUES(F23),
               hybk = VALUES(hybk)
            """
        # 中国A股表数据插入
        self.insert_aboard_sql = f"""
            INSERT INTO ABOARD (
               CREATE_DATE,
               F12,
               F14,
               F2,
               F3,
               F4,
               F5,
               F6,
               F7,
               F8,
               F9,
               F10,
               F15,
               F16,
               F17,
               F18,
               F23,
               hybk
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
               CREATE_DATE = VALUES(CREATE_DATE),
               F12 = VALUES(F12),
               F14 = VALUES(F14),
               F2 = VALUES(F2),
               F3 = VALUES(F3),
               F4 = VALUES(F4),
               F5 = VALUES(F5),
               F6 = VALUES(F6),
               F7 = VALUES(F7),
               F8 = VALUES(F8),
               F9 = VALUES(F9),
               F10 = VALUES(F10),
               F15 = VALUES(F15),
               F16 = VALUES(F16),
               F17 = VALUES(F17),
               F18 = VALUES(F18),
               F23 = VALUES(F23),
               hybk = VALUES(hybk)
            """
        self.result_data = []
        self.notBkResult_data = {}
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

    # 写入操作（行业板块）
    def write_existing_json(self, result: dict = {}):
        # 读取userinfo.json文件中所有信息
        try:
            # jsonPath = self.settings.get('OUTPUT_FILE_PATH')
            # self.gridistJsonFile = f'{jsonPath}hybk.json'
            with open(self.gridistJsonFile, 'w', encoding='utf-8') as w:
                json_data = json.dumps(result, ensure_ascii=False) + '\n'
                w.write(json_data)
        except (FileNotFoundError, json.JSONDecodeError) as ex:
            print(f'{logger_now_date()} hybk Json文件写入失败: {str(ex)}')

    # mysql数据库建立链接
    def open_mysql(self):
        # 爬虫启动时建立连接
        self.conn = pymysql.connect(
            host=self.mysql_host,
            port=self.mysql_port,
            user=self.mysql_user,
            password=self.mysql_pass,
            db=self.mysql_db,
            charset=self.mysql_charset,
            cursorclass=pymysql.cursors.DictCursor
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
            sale_data = datetime.date.today().strftime('%Y-%m-%d')
            for item in data:
                mysql_dict = (sale_data, item['f12'], item['f14'], item['f2'],
                              item['f3'], item['f4'], item['f5'], item['f6'],
                              item['f7'], item['f8'], item['f9'], item['f10'], item['f15'], item['f16'], item['f17'],
                              item['f18'], item['f23'], item['hybk'])
                if float(str(item['f3']).replace('%', '')) >= 4:
                    exec_sql = self.insert_gridist_stock_sql
                    self.cursor.execute(exec_sql, mysql_dict)

                if float(str(item['f2'])) > 0:
                    # 中国A股大盘数据采集
                    exec_sql = self.insert_aboard_sql
                    self.cursor.execute(exec_sql, mysql_dict)

            self.conn.commit()  # 提交事务
        except pymysql.Error as e:
            print(f'{logger_now_date()} 数据登录失败！！！{str(e)}')
            self.conn.rollback()  # 回滚事务
        finally:
            print(f'{logger_now_date()} 数据登录成功！！！')
            self.close_mysql()

    # 数据采集
    def exec(self):
        self.f10ResultData = []
        self.STResultData = []
        self.current_page = 1
        # self.proxy_config = playwrightProxy(1)
        """爬虫程序的入口函数"""
        with sync_playwright() as p:
            # 连接本地启动的浏览器
            self.browser = p.chromium.launch_persistent_context(
                executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                user_data_dir=r'D:\chrome_userData', # 在D盘根目录下创建chrome_userData文件夹
                # user_data_dir=r'C:\Users\Administrator\AppData\Local\Google\Chrome\User Data', # 系统默认chrome浏览器数据访问失败
                # proxy = self.proxy_config,
                headless=False)

            try:
                # 选择默认打开的页面
                self.search_page = self.browser.new_page()
                # 添加初始化js脚本代码，隐藏webdriver属性，防止检测出来
                js = "Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});"
                self.search_page.add_init_script(js)
                # 给playwright添加响应事件的侦听处理函数
                self.search_page.on('response', self.gridist_response)
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
                    print('自动弹框出错了！')

                print(f'{logger_now_date()} 第 {self.current_page} 页，已采集完了！！！！')
                self.search_page.wait_for_timeout(3000)

                # 分页处理
                for index in range(1, self.max_pages):
                    # 是否继续执行
                    if not self.isContinueExec:
                        break

                    self.current_page += 1
                    try:
                        # 单击下一页
                        nextPage = self.search_page.locator('//div[@class="qtpager"]//a[@title="下一页"]')
                        if nextPage.is_visible():
                            nextPage.click()
                        else:
                            # 没有下一页了，退出循环
                            break
                    except Exception as e:
                        # 异常了，退出循环
                        break
                    self.search_page.wait_for_timeout(5000)
                    print(f'{logger_now_date()} 第 {self.current_page} 页，已采集完了！！！！')

                # 板块名称采集
                for key, value in self.notBkResult_data.items():
                    # 新打开一个窗口
                    depthDataPage = self.browser.new_page()
                    # https://emweb.securities.eastmoney.com/pc_hsf10/pages/index.html?type=web&code=BJ920009&color=b#/cpbd
                    hz = ''
                    # 前缀生成
                    if str(key).startswith('0') or str(key).startswith('3'):
                        # SZ
                        hz = 'SZ'
                    elif str(key).startswith('6'):
                        # SZ
                        hz = 'SH'
                    elif str(key).startswith('9'):
                        # BJ
                        hz = 'BJ'
                    depthData_url = f'https://emweb.securities.eastmoney.com/pc_hsf10/pages/index.html?type=web&code={hz}{key}&color=b#/cpbd'
                    # 股票数据
                    self.depthDataItem = value
                    print(f'{logger_now_date()} {key}.F10数据_url: {depthData_url}')
                    # 添加初始化js脚本代码，隐藏webdriver属性，防止检测出来
                    js = "Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});"
                    depthDataPage.add_init_script(js)
                    # 给playwright添加响应事件的侦听处理函数
                    depthDataPage.on('response', self.f10_response)
                    """爬虫执行的主要逻辑"""
                    try:
                        depthDataPage.goto(depthData_url, wait_until="domcontentloaded")
                    except:
                        depthDataPage.goto(depthData_url, wait_until="domcontentloaded")
                    # 等待3秒
                    depthDataPage.wait_for_timeout(5000)
                    # 数据保存
                    self.f10ResultData.append(self.depthDataItem)
                    # 窗口关闭
                    depthDataPage.close()

                # 关闭页面
                self.search_page.close()
            except Exception as e:
                print(f"{logger_now_date()} 数据处理中。。。。。。连接失败： {e}")

        # 有行业的股票数据保存
        if self.result_data:
            print(f'{logger_now_date()} 有行业的股票数据保存: {len(self.result_data)}件')
            self.writeMysql(self.result_data)

        # 需要采集行业名称的股票数据保存
        if self.f10ResultData:
            print(f'{logger_now_date()} 需要采集行业名称的股票数据保存: {len(self.f10ResultData)}件')
            self.writeMysql(self.f10ResultData)

        # ST股票
        if self.STResultData:
            print(f'{logger_now_date()} ST股票件数：{len(self.STResultData)}件')
            # for item in self.STResultData:
            #     print(f"{item['f12']} {item['f14']} {item['f2']} {item['f3']}")

        # 结束之后写入操作
        self.write_existing_json(self.gridistHybkDict)

    # 服务器响应处理
    def gridist_response(self, response):
        try:
            request_url = response.url
            # 沪深京A股数据：https://push2.eastmoney.com/api/qt/clist/get?
            if response.headers.get('content-type') == 'application/javascript; charset=UTF-8' and request_url.find(
                    'api/qt/clist') != -1:
                # print(f'沪深京A股数据: {request_url}')
                # 沪深京A股数据抓取
                self.parseGridist(response)

        except Exception as ex:
            print(f'{logger_now_date()} 服务器响应处理错误: {str(ex)}')

    # 服务器响应处理
    def f10_response(self, response):
        try:
            request_url = response.url
            # F10数据：https://datacenter.eastmoney.com/securities/api/data/get?type=RPT_F10_CORETHEME_BOARDTYPE&sty=ALL&filter=(SECUCODE%3D%22920009.BJ%22)&p=1&ps=&sr=1&st=BOARD_RANK&source=HSF10&client=PC&v=03599433189126675
            if response.headers.get(
                    'content-type') == 'text/plain;charset=UTF-8' and request_url.find(
                    'type=RPT_F10_CORETHEME_BOARDTYPE') != -1:
                # print(f'F10数据: {request_url}')
                # F10数据采集
                self.parseF10Data(response)

        except Exception as ex:
            print(f'{logger_now_date()} 服务器响应处理错误: {str(ex)}')

    # 沪深京A股数据抓取
    def parseGridist(self, response):
        try:
            json_data = str_to_json(response.body())
            row = 0
            # 数据采集
            result = json_data['data']
            if result:
                diff_value = result['diff']  # 安全访问 'diff' 字段
                for item in diff_value:
                    row += 1
                    # ST 不要
                    stockName = str(item['f14'])
                    if stockName.find('st') != -1 or stockName.find('ST') != -1:
                        # print(f"第 {self.current_page} 页 {row}行 退市股票: {item['f12']}, {item['f14']}, {item['f2']}")
                        self.STResultData.append(item)
                        continue

                    # 项目值编辑
                    resultItem = self.editFields(item)
                    # 涨跌幅小于4% 不要
                    if int(item['f3']) < 400:
                        print(f"第 {self.current_page} 页 {row}行 涨跌幅小于4%的股票: {item['f12']}, {item['f14']}, {item['f3']}")
                        self.isContinueExec = False
                        continue

                    # 是否已经采集过 条件1：股票代码不存在需要采集
                    if item['f12'] not in self.gridistHybkDict.keys():
                        print(
                            f"{logger_now_date()} 第 {self.current_page} 页 {row}行 {item['f12']} 行业板块名称没有，数据采集中...")
                        # self.requestDepthData(item)
                        self.notBkResult_data[item['f12']] = resultItem
                    else:
                        hybkName = self.gridistHybkDict[item['f12']]
                        if hybkName == 'None':
                            print(
                                f"{logger_now_date()} 第 {self.current_page} 页 {row}行 {item['f12']} 行业板块名称不正，数据采集中...")
                            # self.requestDepthData(item)
                            self.notBkResult_data[item['f12']] = resultItem
                        else:
                            resultItem["hybk"] = hybkName  # 所属板块
                            self.result_data.append(resultItem)
            else:
                print("路径未匹配到数据")

            print(f'{logger_now_date()} 第 {self.current_page} 页 {row}行 采集的数据：{len(self.result_data)}')
        except Exception as ex:
            raise Exception(f'{logger_now_date()} 沪深京A股数据抓取错误: {str(ex)}')

    # F10数据采集
    def parseF10Data(self, response):
        try:
            json_data = json.loads(response.body())
            depthData_list = json_data['result']['data']
            for item in depthData_list[0]:
                print(f'F10数据采集 item: {item}')
                # 关键字
                keyword = str(item['BOARD_TYPE'])
                # 行业
                if keyword == '行业':
                    self.depthDataItem["hybk"] = item["BOARD_NAME"]
                    # 所属板块保存
                    self.gridistHybkDict[self.depthDataItem['f12']] = item["BOARD_NAME"]
                    break

        except Exception as e:
            raise Exception(f"深度数据采集出错: {str(e)}")

    # 采集数据编辑
    def editFields(self, raw_data):
        # 数据处理
        item = {}
        item["f12"] = raw_data["f12"]  # 股票代码
        item["f14"] = str(raw_data["f14"]).strip()  # 股票名称
        item["f2"] = f'{round(str_to_int(raw_data["f2"]) / 100, 2)}'  # 最新价
        item["f3"] = f'{round(str_to_int(raw_data["f3"]) / 100, 2)}%'  # 涨跌幅
        item["f4"] = f'{round(str_to_int(raw_data["f4"]) / 100, 2)}'  # 涨跌额
        item["f5"] = amountUnitEdit(raw_data["f5"], '')  # 成交量(手)
        item["f6"] = amountUnitEdit(raw_data["f6"])  # 成交额
        item["f7"] = f'{round(str_to_int(raw_data["f7"]) / 100, 2)}%'  # 振幅
        item["f8"] = f'{round(str_to_int(raw_data["f8"]) / 100, 2)}%'  # 换手率
        item["f9"] = f'{round(str_to_int(raw_data["f9"]) / 100, 2)}%'  # 市盈率（动态）
        item[
            "f10"] = f'{round(str_to_int(raw_data["f10"]) / 100, 2)}' if f'{round(str_to_int(raw_data["f10"]) / 100, 2)}' != '0.0' else '-'  # 量比
        item["f15"] = f'{round(str_to_int(raw_data["f15"]) / 100, 2)}'  # 最高
        item["f16"] = f'{round(str_to_int(raw_data["f16"]) / 100, 2)}'  # 最低
        item["f17"] = f'{round(str_to_int(raw_data["f17"]) / 100, 2)}'  # 今开
        item["f18"] = f'{round(str_to_int(raw_data["f18"]) / 100, 2)}'  # 昨收
        item["f23"] = f'{round(str_to_int(raw_data["f23"]) / 100, 2)}'  # 市净率
        item["hybk"] = '' # 默认值
        return item

if __name__ == '__main__':
    es = GridistPlaywright('https://quote.eastmoney.com/center/gridlist.html#hs_a_board', 80)
    if not es.isExec():
        es.exec()
        time.sleep(5)
    sys.exit()