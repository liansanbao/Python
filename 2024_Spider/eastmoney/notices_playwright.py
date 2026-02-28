# _*_ coding: utf-8 _*_
# @Time : 2026/1/6 星期二 15:40
# @Author : 韦丽
# @Version: V 1.0
# @File : notices_playwright.py
# @desc : 东方财富网A股公告
import json
import os
import sys
import time

import pymysql

from eastmoneyBase import EmBase

from eastmoneyTools import str_to_json, amountUnitEdit, now_date, logger_now_date, format_ymdhms
from playwright.sync_api import sync_playwright

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
            A股公告数据
'''
class NoticesPlaywright(EmBase):
    # 构造函数
    def __init__(self, url, maxPage):
        super().__init__()
        # 当日日期 yyyymmdd
        self.now_date = now_date('%Y-%m-%d')
        self.url = url
        self.max_pages = maxPage
        self.result_data = {}
        # 当日文章code读取
        self.now_arts = self.read_artcode_json()
        # A股公告数据插入
        self.insert_anotices_sql = f"""
                    INSERT INTO A_NOTICES (
                       ART_CODE,
                       STOCK_CODE,
                       STOCK_NAME,
                       NOTICE_DATE,
                       NOTICE_TYPE,
                       NOTICE_TITLE,
                       NOTICE_INFO_URL,
                       INDUSTRY
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE
                       ART_CODE = VALUES(ART_CODE),
                       STOCK_CODE = VALUES(STOCK_CODE),
                       STOCK_NAME = VALUES(STOCK_NAME),
                       NOTICE_DATE = VALUES(NOTICE_DATE),
                       NOTICE_TYPE = VALUES(NOTICE_TYPE),
                       NOTICE_TITLE = VALUES(NOTICE_TITLE),
                       NOTICE_INFO_URL = VALUES(NOTICE_INFO_URL),
                       INDUSTRY = VALUES(INDUSTRY)
                    """

    # 数据入库
    def writeMysql(self, data):
        # 根据item中的操作类型执行不同SQL
        try:
            # 事务开启
            self.open_mysql()
            for item in data:
                mysql_dict = (item['ART_CODE'], item['股票代码'], item['股票名称'], item['公告日期'], item['公告类型'], item['公告标题'],
                              item['公告详情'], item['所属行业'])
                self.cursor.execute(self.insert_anotices_sql, mysql_dict)
            self.conn.commit()  # 提交事务
            print(f'DB中一共插入{len(data)}件！')
        except pymysql.Error as e:
            self.isErrorFlag = True
            print(f'{logger_now_date()} 数据登录失败！！！{str(e)}')
            self.conn.rollback()  # 回滚事务
        finally:
            print(f'{logger_now_date()} 数据登录成功！！！')
            self.close_mysql()

    # 数据采集
    def exec(self):
        self.current_page = 1
        self.isExecFlag = False
        self.isErrorFlag = False
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
                    print('自动弹框出错了！')

                # 第一页跳转 输入1
                self.search_page.locator('//input[@id="gotopageindex"]').fill('1')
                self.search_page.wait_for_timeout(2000)

                # 点击确定
                self.search_page.click('//input[@value="确定"]')
                self.search_page.wait_for_timeout(2000)
                print(f'{logger_now_date()} 第 {self.current_page} 页，已采集完了！！！！')

                # 分页处理
                for index in range(1, self.max_pages):
                    # 是否继续执行
                    if self.isExecFlag:
                        print(f'采集终止！{len(self.result_data)}件')
                        break

                    self.current_page += 1
                    try:
                        # 单击下一页
                        nextPage = self.search_page.locator('//div[@class="pagerbox"]/a[text()="下一页"]')
                        if nextPage.is_visible():
                            nextPage.click()
                        else:
                            # 下一页没有了，退出循环
                            break
                    except Exception as e:
                        # 异常了，退出循环
                        break
                    self.search_page.wait_for_timeout(5000)
                    print(f'{logger_now_date()} 第 {self.current_page} 页，已采集完了！！！！')

                # 关闭页面
                self.search_page.close()
                # 有行业的股票数据保存
                if self.result_data:
                    noticeTypes = {}
                    anotices_data = []
                    print(f'{logger_now_date()} 有行业的股票数据保存: {len(self.result_data)}件')
                    now_ymd = now_date('%Y-%m-%d')
                    jsonFile = f'{dir_path}/StockNotices/all_notices_{now_ymd}.json'
                    with open(jsonFile, 'w+', encoding='utf-8') as w:
                        index = 1
                        for key, val in self.result_data.items():
                            # print(f'{key}')
                            json_data = json.dumps(f'{index}_<>{key}<>', ensure_ascii=False, indent=2) + ', \n'
                            w.write(json_data)
                            for item in val:
                                anotices_data.append(item)
                                if item["公告类型"] in noticeTypes.keys():
                                    noticeTypes[item["公告类型"]] = int(noticeTypes[item["公告类型"]]) + 1
                                else:
                                    noticeTypes[item["公告类型"]] = 1
                                # print(f'公告类型: {item["公告类型"]}, 公告标题: {item["公告标题"]}')
                                # 不显示的内容
                                item = {"公告日期": item["公告日期"], "公告详情": item["公告详情"], "公告类型": item["公告类型"],
                                        "公告标题": item["公告标题"]}
                                json_data = json.dumps(f'　　　　{item}', ensure_ascii=False, indent=2) + ', \n'
                                w.write(json_data)

                            index+= 1
                        # 公告汇总
                        for key, value in noticeTypes.items():
                            json_data = json.dumps(f'　　　　{key}: {value} 件', ensure_ascii=False, indent=2) + ', \n'
                            w.write(json_data)

                    # 数据插入DB
                    self.writeMysql(anotices_data)

                    # print(f'所有资产公告数据采集完毕！ {jsonFile}')
                    print(f'所有的公告类型：{noticeTypes}')
                    time.sleep(10)

                # 文章code保存
                if not self.isErrorFlag and len(self.now_arts) > 0:
                    # print(f'文章code保存:{self.now_arts} ')
                    self.write_artcode_json(self.now_arts)
            except Exception as e:
                print(f"{logger_now_date()} 数据处理中。。。。。。连接失败： {e}")

    def read_artcode_json(self):
        # 读取hybk.json文件中所有信息
        result = {}
        try:
            jsonPath = config['hybk']['output_file_path']
            nowYmd = now_date('%Y%m%d')
            self.artsJsonFile = f'{jsonPath}notices_art_{nowYmd}.json'
            print(f'文章codeJSON文件读取：{self.artsJsonFile}')
            with open(self.artsJsonFile, 'r', encoding='utf-8') as r:
                for line in r:
                    line = line.strip()
                    if line:  # 跳过空行
                        result = dict(json.loads(line))
                        # result[data['f12']] = data['hybk']
        except (FileNotFoundError, json.JSONDecodeError):
            return dict()
        # print(f'result: {result}')
        return result

    # 写入操作（文章代码）
    def write_artcode_json(self, result: dict = {}):
        # 读取userinfo.json文件中所有信息
        try:
            print(f'文章codeJSON文件保存：{self.artsJsonFile}')
            # jsonPath = self.settings.get('OUTPUT_FILE_PATH')
            # self.gridistJsonFile = f'{jsonPath}hybk.json'
            with open(self.artsJsonFile, 'w', encoding='utf-8') as w:
                json_data = json.dumps(result, ensure_ascii=False) + '\n'
                w.write(json_data)
        except (FileNotFoundError, json.JSONDecodeError) as ex:
            print(f'{logger_now_date()} hybk Json文件写入失败: {str(ex)}')

    # 服务器响应处理
    def notices_response(self, response):
        try:
            request_url = response.url
            # 沪深京A股公告数据：https://np-anotice-stock.eastmoney.com/api/security/ann?cb=jQuery112309602513623424559_1767684708729&sr=-1&page_size=50&page_index=2&ann_type=SHA%2CCYB%2CSZA%2CBJA%2CINV&client_source=web&f_node=0&s_node=0
            if response.headers.get('content-type') == 'text/plain;charset=UTF-8' and request_url.find(
                    '/api/security/ann') != -1:
                # print(f'沪深京A股公告数据: {request_url}')
                # 沪深京A股公告数据抓取
                self.parseNotices(response)

        except Exception as ex:
            print(f'{logger_now_date()} 服务器响应处理错误: {str(ex)}')

    # 沪深京A股公告数据抓取
    def parseNotices(self, response):
        try:
            json_data = str_to_json(response.body())
            result = json_data["data"]
            if result:
                diff_value = result["list"]  # 安全访问 'list' 字段
                for item in diff_value:
                    # 文章code不存在开始采集
                    if item['art_code'] not in self.now_arts.keys():
                        notice_date = format_ymdhms(item['notice_date'], '%Y-%m-%d %H:%M:%S', '%Y-%m-%d')
                        # 公告时间必须大于等于当前系统时间
                        if self.now_date <= notice_date:
                            item['notice_date'] = notice_date
                            self.editFields(item)
                        else:
                            self.isExecFlag = True
        except Exception as ex:
            raise Exception(f'板块资金流数据抓取错误: {str(ex)}')

    def format_string(self, input_str, target_length):
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

    # 采集数据编辑
    def editFields(self, item):
        try:
            notice_item = {}
            codes = item['codes'][0]
            # art_code
            notice_item["ART_CODE"] = item['art_code']
            notice_item["公告详情"] = f"https://data.eastmoney.com/notices/detail/{codes['stock_code']}/{item['art_code']}.html"
            # 股票代码
            notice_item["股票代码"] = codes['stock_code']
            # 缓存中保存股票代码和文字code
            self.now_arts[notice_item['ART_CODE']] = notice_item['股票代码']
            # 股票名称
            notice_item["股票名称"] = self.format_string(codes['short_name'], 4)
            # 公告类型
            if item['columns'] != None and len(item['columns']) > 0:
                notice_item["公告类型"] = item['columns'][0]['column_name']
            else:
                notice_item["公告类型"] = ''
            # 公告标题
            notice_item["公告标题"] = item['title']
            # 公告日期
            notice_item["公告日期"] = item['notice_date']
            # 行业
            if notice_item['股票代码'] not in self.gridistHybkDict.keys():
                notice_item["所属行业"] = ''
            else:
                hybkName = self.gridistHybkDict[notice_item['股票代码']]
                if hybkName == 'None':
                    notice_item["所属行业"] = ''
                else:
                    notice_item["所属行业"] = hybkName

            stockKey = f"{notice_item['股票代码']}_{notice_item['股票名称']}"
            if stockKey in self.result_data.keys():
                item = list(self.result_data[stockKey])
                item.append([notice_item])
            else:
                self.result_data[stockKey] = [notice_item]
        except Exception as ex:
            print(f'item: {item}_数据编辑错误: {str(ex)}')

if __name__ == '__main__':
    es = NoticesPlaywright('https://data.eastmoney.com/notices/', 100)
    if not es.isExec():
        es.exec()
        time.sleep(5)

    sys.exit()