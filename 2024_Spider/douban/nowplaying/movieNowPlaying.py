# _*_ coding: utf-8 _*_
# @Time : 2025/6/9 0009 20:17
# @Author : 韦丽
# @Version: V 1.0
# @File : movieNowPlaying.py
# @desc : 豆瓣多部热门电影短评论数据采集
import json
import os
import time

from playwright.sync_api import sync_playwright


class NowPlaying:
    def __init__(self, chromePath, chromeUserPath, url):
        self.chromePath = chromePath
        self.chromeUserPath = chromeUserPath
        self.url = url

    # 豆瓣多部热门电影短评论数据采集
    def exec(self):
        """爬虫程序的入口函数"""
        with sync_playwright() as p:
            # 连接本地启动的浏览器
            self.browser = p.chromium.launch_persistent_context(
                executable_path=self.chromePath,
                user_data_dir=self.chromeUserPath,  # 在D盘根目录下创建chrome_userData文件夹
                headless=False)

            try:
                # 选择默认打开的页面
                self.search_page = self.browser.new_page()
                # 添加初始化js脚本代码，隐藏webdriver属性，防止检测出来
                js = "Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});"
                self.search_page.add_init_script(js)

                """爬虫执行的主要逻辑"""
                try:
                    self.search_page.goto(self.url, wait_until="domcontentloaded")
                except:
                    self.search_page.goto(self.url, wait_until="domcontentloaded")

                # 城市名称获取
                self.locationCity = self.getText(self.search_page.locator('//div[@id="hd"]//h1')).split(' - ')[1]
                # 以城市名称来新建文件夹存储热门电影短评数据
                self.makeDir(self.locationCity)
                # 等待2秒
                self.search_page.wait_for_timeout(2000)
                # 电影名称
                movie_list = []

                # 电影数据处理
                if self.search_page.is_visible('//div[@id="nowplaying"]'):
                    # 定位包含所有的数据
                    divs = self.search_page.locator('//li[@class="stitle"]//a').all()
                    for movie in divs:
                        self.result_data = []
                        # 电影 名称
                        movie_name = movie.get_attribute('title').replace('*','')
                        # 电影 短评 url https://movie.douban.com/subject/34807062/comments?status=P
                        movie_url = movie.get_attribute('href').split('?')[0]
                        # 短评数据采集
                        self.comments(movie_name, movie_url)
                        # 采集结果打印
                        print(f'电影《{movie_name}》采集结果：{self.result_data}')
                        # 保存Json文件
                        self.saveJson(movie_name)
                        movie_list.append(movie_name)
                        # 等待2秒
                        time.sleep(2)

                # 关闭页面
                self.search_page.close()
                # 电影名称打印
                print(f'一共爬取：{movie_list}')
            except Exception as e:
                print(f"数据处理中。。。。。。异常发生： {e}")

    # 保存Json文件
    def saveJson(self, fileName):
        with open(f'{self.locationCity}//{fileName}.json', 'w', encoding='utf-8') as w:
            for item in self.result_data:
                # 把字典数据转json
                json_data = json.dumps(item, separators=(',', ':'), ensure_ascii=False) + ', \n'
                w.write(json_data)

    # 短评数据采集
    def comments(self, movie_name, movieUrl):
        url = f'{movieUrl}comments?status=P'

        try:
            # 选择默认打开的页面
            self.user_page = self.browser.new_page()
            # 添加初始化js脚本代码，隐藏webdriver属性，防止检测出来
            js = "Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});"
            self.user_page.add_init_script(js)

            """爬虫执行的主要逻辑"""
            try:
                self.user_page.goto(url, wait_until="domcontentloaded")
            except:
                self.user_page.goto(url, wait_until="domcontentloaded")

            # 评论条数
            comment_count = 0

            # 每部正在上映热门电影选取50条
            while (comment_count < 50):
                all_element = self.user_page.locator('//div[@class="comment"]').all()
                for element in all_element:
                    rowData = {}
                    # 评论人取得
                    rowData["评论者"] = self.getText(element.locator('//span[@class="comment-info"]//a'))
                    # 评论人所在城市
                    rowData["所在地"] = self.getText(
                        element.locator('//span[@class="comment-info"]//span[@class="comment-location"]'))
                    # 看过文字获取
                    rowData["是否观看"] = self.getText(element.locator('//span[@class="comment-info"]//span[1]'))
                    # 推荐度
                    rowData["推荐度"] = self.getAllStar(element.locator('//span[@class="comment-info"]//span[2]').get_attribute('class'))
                    # 评论时间
                    rowData["评论时间"] = self.getText(element.locator('//span[@class="comment-info"]//span[@class="comment-time"]'))
                    # 评论内容
                    rowData["评论内容"] = self.getText(element.locator('//p[@class="comment-content"]//span[@class="short"]'))
                    self.result_data.append(rowData)
                    comment_count += 1
                    # 超出50条退出
                    if comment_count == 50:
                        break

                # 下一页URL获取
                if self.user_page.is_visible('//a[@class="next"]') and comment_count < 50:
                    self.user_page.locator('//a[@class="next"]').click()
                    # 等待页面加载完成（根据需要选择适当的等待条件）
                    self.user_page.wait_for_load_state('domcontentloaded')  # 或者使用 wait_for_timeout
                    # 等待5秒
                    self.user_page.wait_for_timeout(5000)
                else:
                    print(f'电影《{movie_name}》获取评论条数: {comment_count}')
                    break

            self.user_page.close()
        except Exception as e:
            print(f'电影《{movie_name}》短评数据采集失败： {e}')

    # 文件夹创建
    def makeDir(self, fileName):
        if not os.path.exists(fileName):
            os.makedirs(fileName)

    # text值取得
    def getText(self, li):
        try:
            if li.count() > 0:
                return li.inner_text()
        except:
            pass
        return ''

    # 推荐度
    def getAllStar(self, star):
        res = ''
        if 'allstar50 rating' == star:
            res = '五颗星'
        elif 'allstar40 rating' == star:
            res = '四颗星'
        elif 'allstar30 rating' == star:
            res = '三颗星'
        elif 'allstar20 rating' == star:
            res = '二颗星'
        elif 'allstar10 rating' == star:
            res = '一颗星'
        return res

if __name__ == '__main__':
    # 系统中安装Google chrome浏览器的路径
    executable_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
    # 使用Google chrome浏览器访问网站时，登录过的用户数据保存的路径
    user_data_dir = r'D:\chrome_userData'
    # 爬取的URL
    url = 'https://movie.douban.com/cinema/nowplaying/'
    nowPlaying = NowPlaying(executable_path, user_data_dir, url)
    # 数据爬取
    nowPlaying.exec()