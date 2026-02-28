# _*_ coding: utf-8 _*_
# @Time : 2025/4/26 08:38
# @Author : 韦丽
# @Version: V 1.0
# @File : playwright_travelQunar.py
# @desc : 使用python采集去哪儿旅游攻略 网站：https://travel.qunar.com/travelbook/list.htm?order=hot_heat
import time
import datetime
import pandas
from playwright.sync_api import sync_playwright
from pymongo import MongoClient

'''
    要求：
        1.爬取攻略库的200页数据
        2.数据内容应该包括：'攻略地点','短评','浏览量','出发日期','天数','人均费用','人物','玩法','详情页'
        3.数据保存：Excel一份，数据存储于MongoDB或MySQL一份
        4.使用一种反爬方法
'''
class TravelQunar(object):
    def __init__(self, pageNo = 1):
        # 定义实例变量number_,表示翻页的页数
        self.pageNo = pageNo

    def exec(self):
        self.detail_data = []
        """爬虫程序的入口函数"""
        with sync_playwright() as p:
            # 连接本地启动的浏览器
            browser = p.chromium.launch(headless=False,
                              executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                              args=['--start-maximized'])
            # 1.爬取攻略库的200页数据
            for page in range(1, self.pageNo + 1):
                try:
                    self.url = f'https://travel.qunar.com/travelbook/list.htm?page={page}&order=hot_heat'
                    print(f'第{page}页URL: {self.url}')
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
                    # 进行数据提取，执行run_detail_data方法
                    self.run_detail_data()

                    # 关闭页面
                    self.page.close()
                except Exception as e:
                    print(f'连接失败： {e}')

        # 出力execl文件
        self.save_execl()
        # MongoDB中保存
        self.save_mongodb()

    def run_detail_data(self):
        # 选择默认打开的页面
        self.pageDeatil = self.context.new_page()
        # 页面详情元素取得
        detail_elements = self.page.locator('//li//h2//a').all()
        for element in detail_elements:
            time.sleep(2)
            try:
                self.pageDeatil.goto('https://travel.qunar.com' + element.get_attribute('href'), wait_until="domcontentloaded")
            except:
                self.pageDeatil.goto('https://travel.qunar.com' + element.get_attribute('href'), wait_until="domcontentloaded")
            rowData = {}
            # 数据不存在，跳过
            if self.pageDeatil.locator('//div[@class="fix_box"]').count() == 0:
                continue
            # 攻略地点 strategy_location
            rowData["攻略地点"] = self.getInnerText(self.pageDeatil.locator('//p[@class="b_crumb_cont"]/a[2]'))
            # 短评 short_comment
            rowData["短评"] = self.getInnerText(self.pageDeatil.locator('//div[@class="user_info"]/div/h1/span'))
            # 浏览量 page_view
            rowData["浏览量"] = self.getInnerText(self.pageDeatil.locator('//li[@class="date"]/span[3]'))
            # 出发日期 departure_date
            rowData["出发日期"] = self.getInnerText(self.pageDeatil.locator('//li[@class="f_item when"]/p/span[2]'))
            # 天数 dasys
            rowData["天数"] = self.getInnerText(self.pageDeatil.locator('//li[@class="f_item howlong"]/p/span[2]'))
            # 人均费用 per_capita_cost
            rowData["人均费用"] = self.getInnerText(self.pageDeatil.locator('//li[@class="f_item howmuch"]/p/span[2]'))
            # 人物 character
            rowData["人物"] = self.getInnerText(self.pageDeatil.locator('//li[@class="f_item who"]/p/span[2]'))
            # 玩法 gameplay
            rowData["玩法"] = self.getInnerText(self.pageDeatil.locator('//li[@class="f_item how"]/p/span[2]'))
            # 详情页 details_page
            rowData["详情页"] = self.pageDeatil.url
            print(rowData)
            self.detail_data.append(rowData)
            time.sleep(2)

        self.pageDeatil.close()
        self.page.wait_for_timeout(5000)

    # text值取得
    def getInnerText(self, li):
        text_list = li
        try:
            if text_list.count() > 0:
                return text_list.inner_text().replace('\xa0', ' ')
        except:
            pass
        return ''

    # 出力execl文件
    def save_execl(self):
        df = pandas.DataFrame(self.detail_data)
        nowdate = datetime.date.today().strftime('%Y%m%d')
        df.to_excel(f'crawl_qunar_{nowdate}.xlsx', index=False)

    # MongoDB中保存
    def save_mongodb(self):
        with MongoClient(host='192.168.1.15', port=27017) as con:  # 实例化mongoclient
            collection = con['travelQunarSpider']['crawl_qunar']
            for py_dict in self.detail_data:
                with con.start_session() as session:
                    session.start_transaction()
                    try:
                        # 以详情页作为更新条件，upsert=True不满足就进行插入操作
                        resutl = collection.update_one(
                            {'详情页': py_dict['详情页']},
                            {'$set': py_dict},
                            upsert=True,
                            session=session
                        )
                        print(f'更新件数： {resutl.modified_count}')
                        session.commit_transaction()
                    except Exception as e:
                        session.abort_transaction()

if __name__ == '__main__':
    travelQunar = TravelQunar(200)
    travelQunar.exec()
