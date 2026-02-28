# _*_ coding: utf-8 _*_
# @Time : 2025/11/13 星期四 21:22
# @Author : 韦丽
# @Version: V 1.0
# @File : gnzjl_playwright.py
# @desc :
import json
import os
import sys
import time

import pymysql
from pymysql.cursors import DictCursor
from eastmoneyBase import EmBase

from eastmoneyTools import str_to_json, amountUnitEdit, now_date, logger_now_date
from playwright.sync_api import sync_playwright

# 获取当前脚本的绝对路径
script_path = os.path.abspath(__file__)

# 获取所在文件夹路径
dir_path = str(os.path.dirname(script_path))

dir_path = dir_path.replace('\\', '/')

'''
    要求：
        东方财富网数据采集
            概念资金流数据
'''
class GnzjlPlaywright(EmBase):
    # 构造函数
    def __init__(self, url, maxPage):
        super().__init__()
        self.url = url
        self.max_pages = maxPage
        self.result_data = []
        self.notBkResult_data = {}
        # 板块资金流向表数据插入
        self.insert_hyzjl_sql = f"""
            INSERT INTO HYZJL_CRAWL (
               CREATE_DATE,
               F12,
               F14,
               F2,
               F3,
               F62,
               F184,
               F66,
               F69,
               F72,
               F75,
               F78,
               F81,
               F84,
               F87,
               F204,
               F205,
               ActivateType,
               hyType
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
               CREATE_DATE = VALUES(CREATE_DATE),
               F12 = VALUES(F12),
               F14 = VALUES(F14),
               F2 = VALUES(F2),
               F3 = VALUES(F3),
               F62 = VALUES(F62),
               F184 = VALUES(F184),
               F66 = VALUES(F66),
               F69 = VALUES(F69),
               F72 = VALUES(F72),
               F75 = VALUES(F75),
               F78 = VALUES(F78),
               F81 = VALUES(F81),
               F84 = VALUES(F84),
               F87 = VALUES(F87),
               F204 = VALUES(F204),
               F205 = VALUES(F205),
               ActivateType = VALUES(ActivateType),
               hyType = VALUES(hyType)
            """

    # 数据入库
    def writeMysql(self, data):
        # 根据item中的操作类型执行不同SQL
        try:
            # 事务开启
            self.open_mysql()
            for item in data:
                mysql_dict = (item['frq'], item['f12'], item['f14'], item['f2'], item['f3'],
                              item['f62'], item['f184'], item['f66'], item['f69'],
                              item['f72'], item['f75'], item['f78'], item['f81'], item['f84'], item['f87'],
                              item['f204'], item['f205'], '1', '2')
                self.cursor.execute(self.insert_hyzjl_sql, mysql_dict)
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
                self.search_page.on('response', self.hyzjl_response)
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

                # 概念资金流按钮单击
                self.search_page.locator('//ul[@id="filter_bk"]/li[text()="概念资金流"]').click()
                self.search_page.wait_for_timeout(3000)
                print(f'{logger_now_date()} 第 {self.current_page} 页，已采集完了！！！！')

                # 分页处理
                for index in range(1, self.max_pages):
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
            except Exception as e:
                print(f"{logger_now_date()} 数据处理中。。。。。。连接失败： {e}")

        # 有行业的股票数据保存
        if self.result_data:
            print(f'{logger_now_date()} 有行业的股票数据保存: {len(self.result_data)}件')
            self.writeMysql(self.result_data)

    # 服务器响应处理
    def hyzjl_response(self, response):
        try:
            request_url = response.url
            # 沪深京A股数据：https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery112303754194046966902_1763382737624&fid=f62&po=1&pz=50&pn=2&np=1&fltt=2&invt=2&ut=8dec03ba335b81bf4ebdf7b29ec27d15&fs=m%3A90+t%3A3&fields=f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13
            if response.headers.get('content-type') == 'application/javascript; charset=UTF-8' and request_url.find(
                    'fs=m%3A90+t%3A3') != -1:
                # print(f'沪深京A股数据: {request_url}')
                # 沪深京A股数据抓取
                self.parseHyzjl(response)

        except Exception as ex:
            print(f'{logger_now_date()} 服务器响应处理错误: {str(ex)}')

    # 板块资金流数据抓取
    def parseHyzjl(self, response):
        try:
            # 当日日期 yyyymmdd
            now_ymd = now_date()
            json_data = str_to_json(response.body())
            result = json_data['data']
            if result:
                diff_value = result['diff']  # 安全访问 'diff' 字段
                for item in diff_value:
                    self.editFields(item, now_ymd)
        except Exception as ex:
            raise Exception(f'板块资金流数据抓取错误: {str(ex)}')

    # 采集数据编辑
    def editFields(self, item, now_ymd):
        zjlx_item = {}
        # 行业代码
        zjlx_item["f12"] = item['f12']
        # 行业名称
        zjlx_item["f14"] = item['f14']
        # 最新价
        zjlx_item["f2"] = str(item['f2']) + '元'
        # 今日涨跌幅
        zjlx_item["f3"] = str(item['f3']) + '%'
        # 今日主力净流入(净额) amountUnitEdit 这里不需要转换，有画面来转换
        zjlx_item["f62"] = item['f62']
        # 今日主力净流入(净占比)
        zjlx_item["f184"] = str(item['f184']) + '%'
        # 今日超大单净流入(净额) amountUnitEdit 这里不需要转换，有画面来转换
        zjlx_item["f66"] = amountUnitEdit(item['f66'])
        # 今日超大单净流入(净占比)
        zjlx_item["f69"] = str(item['f69']) + '%'
        # 今日大单净流入(净额) amountUnitEdit 这里不需要转换，有画面来转换
        zjlx_item["f72"] = amountUnitEdit(item['f72'])
        # 今日大单净流入(净占比)
        zjlx_item["f75"] = str(item['f75']) + '%'
        # 今日中单净流入(净额) amountUnitEdit 这里不需要转换，有画面来转换
        zjlx_item["f78"] = amountUnitEdit(item['f78'])
        # 今日中单净流入(净占比)
        zjlx_item["f81"] = str(item['f81']) + '%'
        # 今日小单净流入(净额) amountUnitEdit 这里不需要转换，有画面来转换
        zjlx_item["f84"] = amountUnitEdit(item['f84'])
        # 今日小单净流入(净占比)
        zjlx_item["f87"] = str(item['f87']) + '%'
        # 今日主力净流入(最大股名称)
        zjlx_item["f204"] = item['f204']
        # 今日主力净流入(最大股代码)
        zjlx_item["f205"] = item['f205']
        # 数据采集日期
        zjlx_item["frq"] = now_ymd
        self.result_data.append(zjlx_item)

if __name__ == '__main__':
    es = GnzjlPlaywright('https://data.eastmoney.com/bkzj/hy.html', 30)
    if not es.isExec():
        es.exec()
        time.sleep(5)

    sys.exit()