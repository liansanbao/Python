# _*_ coding: utf-8 _*_
# @Time : 2025/8/13 星期三 23:21
# @Author : 韦丽
# @Version: V 1.0
# @File : testPlaywright.py
# @desc :
# import json
# import os
# import re
# import subprocess
# import time
# 
# import jsonpath
# import requests
# from playwright.sync_api import sync_playwright
# 
# class TaobaoProductActivateCrawl:
#     def __init__(self, url):
#         """定义远程调试参数"""
#         path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
#         params = "--remote-debugging-port=9222"
#         user_data_dir = r"D:\chrome_userData"  # 自定义目录
#         cmd = f'"{path}" {params}'
#         subprocess.Popen([path, "--remote-debugging-port=6789", f"--user-data-dir={user_data_dir}"], shell=True)
#         # 爬取URL
#         self.url = url
# 
#     def exec(self):
#         """爬虫程序的入口函数"""
#         with sync_playwright() as p:
#             # 连接本地启动的浏览器
#             browser = p.chromium.connect_over_cdp('http://127.0.0.1:6789')
#             # 选择默认的浏览器上下文对象
#             self.context = browser.contexts[0]
#             # 选择默认打开的页面
#             self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
#             # 添加初始化js脚本代码，隐藏webdriver属性，防止检测出来
#             js = "Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});"
#             self.page.add_init_script(js)
# 
#             # 给playwright添加响应事件的侦听处理函数
#             self.page.on('response', self.handler_response)
# 
#             # 指定访问的URL
#             self.page.goto(self.url, timeout=60000)
#             self.page.wait_for_load_state('load')
# 
#             self.page.wait_for_selector('body', state='attached')
# 
#             # 关闭页面
#             self.page.close()
# 
#     # json数据
#     def handler_response(self, response):
#         request_url = response.url
#         # https://h5api.m.taobao.com/h5/mtop.taobao.pcdetail.data.get/1.0/?jsv=2.7.4&appKey=12574478&t=1754672750412&sign=cd1f61bc098afd9600fbf71130935acb&api=mtop.taobao.pcdetail.data.get&v=1.0&isSec=0&ecode=0&timeout=10000&jsonpIncPrefix=pcdetail&ttid=2022%40taobao_litepc_9.17.0&AntiFlood=true&AntiCreep=true&type=jsonp&dataType=jsonp&callback=mtopjsonppcdetail3&data=%7B%22id%22%3A%22937920164396%22%2C%22detail_v%22%3A%223.3.2%22%2C%22exParams%22%3A%22%7B%5C%22abbucket%5C%22%3A%5C%225%5C%22%2C%5C%22id%5C%22%3A%5C%22937920164396%5C%22%2C%5C%22ns%5C%22%3A%5C%221%5C%22%2C%5C%22priceTId%5C%22%3A%5C%22213e055c17546725395342171e1425%5C%22%2C%5C%22skuId%5C%22%3A%5C%225831322641670%5C%22%2C%5C%22spm%5C%22%3A%5C%22a21n57.1.hoverItem.49%5C%22%2C%5C%22utparam%5C%22%3A%5C%22%7B%5C%5C%5C%22aplus_abtest%5C%5C%5C%22%3A%5C%5C%5C%2283267e7c07402b205018ee57e2ada6a3%5C%5C%5C%22%7D%5C%22%2C%5C%22xxc%5C%22%3A%5C%22taobaoSearch%5C%22%2C%5C%22queryParams%5C%22%3A%5C%22abbucket%3D5%26id%3D937920164396%26ltk2%3D1754672713855ux9sdj5rpesjik19uvtj%26ns%3D1%26priceTId%3D213e055c17546725395342171e1425%26skuId%3D5831322641670%26spm%3Da21n57.1.hoverItem.49%26utparam%3D%257B%2522aplus_abtest%2522%253A%252283267e7c07402b205018ee57e2ada6a3%2522%257D%26xxc%3DtaobaoSearch%5C%22%2C%5C%22domain%5C%22%3A%5C%22https%3A%2F%2Fitem.taobao.com%5C%22%2C%5C%22path_name%5C%22%3A%5C%22%2Fitem.htm%5C%22%2C%5C%22pcSource%5C%22%3A%5C%22pcTaobaoMain%5C%22%2C%5C%22refId%5C%22%3A%5C%22qCU%2Fv2eMQNRPc35X2WqRNg3eiUoCIkbsljuV2IMCnhw%3D%5C%22%2C%5C%22nonce%5C%22%3A%5C%22U1DZdqoQI0GGqwaubbsKqw%3D%3D%5C%22%2C%5C%22feTraceId%5C%22%3A%5C%22d27f5db2-d4f9-43ba-b0fd-bb1d48915ba0%5C%22%7D%22%7D&bx-ua=fast-load
#         if response.headers.get('content-type') == 'application/json;charset=UTF-8' and request_url.find('mtop.taobao.pcdetail.data.get/1.0/?') != -1:
#             print(f'滚动滚动条时的异步请求URL：{request_url}')
#             # 获取滚动条滚动时的异步请求响应数据
#             str_data = response.body()
#             # 转Json数据
#             json_data = self.str_to_json(str_data)
# 
#             print(f'json_data: {json_data}')
# 
#     # 将字符串转Json格式
#     def str_to_json(self, str_data):
#         str_result = str_data.decode('utf-8')
#         # 去掉JSONP包装
#         start = str_result.find('(') + 1
#         end = str_result.rfind(')')
#         json_str = str_result[start:end]
#         # 解析Json
#         return json.loads(json_str)
import random

import asyncio
# import json
# import random
# import time
# from typing import List, Dict
#
# import asyncio
# import jsonpath
# from fake_useragent import FakeUserAgent
# from playwright.sync_api import sync_playwright
#
#
# class TaobaoProductActivateCrawl:
#     def __init__(self):
#         self.browser = None
#         self.context = None
#         self.page = None
#
#     def init_browser(self):
#         """初始化浏览器实例"""
#         playwright = sync_playwright().start()
#         self.browser = playwright.chromium.launch_persistent_context(
#             executable_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe",
#             user_data_dir= r"D:\chrome_userData",
#             viewport={'width': 1920, 'height': 1080},
#             user_agent=FakeUserAgent().random,
#             headless=False
#         )
#         return self.browser
#
#     def ensure_browser(self):
#         """确保浏览器连接有效"""
#         if not self.browser or not self.browser.is_connected():
#             print('1111')
#             self.init_browser()
#
#         # if not self.context or self.context.is_close():
#         #     print(f'2222: {self.browser}')
#         #     self.context = self.browser.new_context()
#         #     print('3333')
#
#     def exec(self, url, proxy) -> List[Dict]:
#         try:
#             self.ensure_browser()
#             print('4444')
#             # 创建新页面（避免页面状态污染）
#             self.page = self.browser.new_page()
#
#             # 请求头伪装
#             self.page.set_extra_http_headers({
#                 'Accept-Language': 'zh-CN,zh;q=0.9',
#                 'Referer': 'https://www.tmall.com/'
#             })
#
#             # 增强反检测脚本
#             self.page.add_init_script("""
#                 Object.defineProperty(navigator, 'webdriver', {get: () => false});
#                 Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]});
#                 window.chrome = {runtime: {}};
#             """)
#
#             # 处理可能的登录跳转
#             self.page.route('&zwnj;**/login.**&zwnj;', lambda route: route.continue_())
#
#             # 设置请求拦截
#             self.page.route('&zwnj;**/mtop.taobao.pcdetail.data.get/**&zwnj;', self.handle_api_request)
#
#             # 随机延迟访问
#             # asyncio.sleep(random.uniform(1, 3))
#             self.page.goto(url, timeout=60000)
#
#             time.sleep(10)
#             # 等待关键元素
#             self.page.wait_for_selector('body', state='attached')
#             # asyncio.sleep(2)  # 增加等待时间
#         except Exception as ex:
#             if self.page:
#                 self.page.close()
#             print(f'Error: {str(ex)}')
#             raise
#         finally:
#             if self.page and not self.page.is_closed():
#                 self.page.close()
#
#     # json数据
#     def handle_api_request(self, response):
#         request_url = response.url
#         # https://h5api.m.taobao.com/h5/mtop.taobao.pcdetail.data.get/1.0/?jsv=2.7.4&appKey=12574478&t=1754672750412&sign=cd1f61bc098afd9600fbf71130935acb ...
#         if response.headers.get('content-type') == 'application/json;charset=UTF-8' and request_url.find(
#                 'mtop.taobao.pcdetail.data.get/1.0/?') != -1:
#             # 获取滚动条滚动时的异步请求响应数据
#             str_data = response.body()
#             # 转Json数据
#             json_data = self.str_to_json(str_data)
#             # 图片URL
#             thumburl_list = jsonpath.jsonpath(json_data, '$.data.componentsVO.extensionInfoVO.infos..items..text')
#             print(f'thumburl_list: {thumburl_list}')
#
#     # 将字符串转Json格式
#     def str_to_json(self, str_data):
#         # 确保传入的是bytes类型
#         if isinstance(str_data, bytes):
#             str_result = str_data.decode('utf-8')
#         else:
#             str_result = str(str_data)
#         # 去掉JSONP包装
#         start = str_result.find('(') + 1
#         end = str_result.rfind(')')
#         json_str = str_result[start:end]
#         # 解析Json
#         return json.loads(json_str)
#
# if __name__ == '__main__':
#     # 电脑：https://s.taobao.com/search?page=2&q=%E7%94%B5%E8%84%91%E6%95%B4%E6%9C%BA&spm=a21bo.jianhua%2Fa.201867-main.d2_2.3de02a89OHEQWl&tab=all
#     #      https://s.taobao.com/search?page=3&q=%E7%94%B5%E8%84%91%E6%95%B4%E6%9C%BA&spm=a21bo.jianhua%2Fa.201867-main.d2_2.3de02a89OHEQWl&tab=all
#     #      https://s.taobao.com/search?page=4&q=%E7%94%B5%E8%84%91%E6%95%B4%E6%9C%BA&spm=a21bo.jianhua%2Fa.201867-main.d2_2.3de02a89OHEQWl&tab=all
#     # 家电：https://s.taobao.com/search?page=1&q=%E5%AE%B6%E7%94%B5&spm=a21bo.jianhua%2Fa.201867-main.d4_first.3de02a89OHEQWl&tab=all
#     #      https://s.taobao.com/search?page=2&q=%E5%AE%B6%E7%94%B5&spm=a21bo.jianhua%2Fa.201867-main.d4_first.3de02a89OHEQWl&tab=all
#     #      https://s.taobao.com/search?page=3&q=%E5%AE%B6%E7%94%B5&spm=a21bo.jianhua%2Fa.201867-main.d4_first.3de02a89OHEQWl&tab=all
#     tpac = TaobaoProductActivateCrawl()
#     tpac.exec('https://detail.tmall.com/item.htm?ali_refid=a3_430582_1006%3A1232930108%3AN%3AKV%2Fu6HT5hnIF5S%2F00x%2BYSQ%3D%3D%3A852f38a485c4eb92cecb42ce4eef118d&ali_trackid=162_852f38a485c4eb92cecb42ce4eef118d&id=595733677157&mi_id=nq5O6PNbc6XUDEJyaL5YWORylfiwnCdNXej3XsZTI8XVaz_eHsH9Efd0Xtt_p5EMWkVR-aPoi2ZBEgk_xm86EtOtABbuQIF4iNjKWqXa4QE&mm_sceneid=7_0_450650167_0&priceTId=215041c017550393941591411e1371&skuId=4566066668610&spm=a21n57.1.hoverItem.1&utparam=%7B%22aplus_abtest%22%3A%226e18d7ad0d17624698dde0503577ce6a%22%7D&xxc=ad_ztc', None)

from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright


class Async_TPE_Crawl:
    def __init__(self):
        self.browser = None
        self.page = None

    def init_browser(self):
        """初始化浏览器实例 headless=True 无窗口 反之：有窗口"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch_persistent_context(
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            user_data_dir=r"D:\chrome_userData",
            headless=False
        )

    def ensure_browser(self):
        """确保浏览器连接有效"""
        if not self.browser:
            print('确保浏览器连接有效')
            self.init_browser()

    def reboot(self):
        print('浏览器重启')
        if self.page:
            self.page.close()
            self.page = None
        if self.browser:
            self.browser.close()
            self.browser = None
        if hasattr(self, 'playwright'):
            self.playwright.stop()
            self.playwright = None

    def tpe_exec(self, url) -> bool:
        try:
            self.ensure_browser()
            print('开始采集数据')
            # 创建新页面（避免页面状态污染）
            self.page = self.browser.new_page()

            # 增强反检测脚本
            self.page.add_init_script("""
                Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});
            """)

            # 随机延迟访问
            # asyncio.sleep(random.uniform(1, 3))
            response = self.page.goto(url, timeout=60000, wait_until="domcontentloaded")
            print(f'response: {response}')

            if not response.ok:
                raise Exception(f"页面加载失败, 状态码: {response.status}")

            # 等待关键元素
            try:
                self.page.wait_for_selector('body', state='attached', timeout=10000)
            except Exception as e:
                print(f"等待元素超时: {str(e)}")
                return False

            self.page.wait_for_load_state("domcontentloaded", timeout=10000)

            # 检查拦截层是否存在
            has_interception = self.page.evaluate('''() => {
                                        return document.querySelector('.J_MIDDLEWARE_FRAME_WIDGET') !== null;
                                    }''')

            print(f'has_interception: {has_interception}')

            if has_interception:
                # 移除可能存在的拦截层
                while True:
                    print(f'滑动开始。。。。。')
                    if self.handle_slider():
                        print(f'滑动结束。。。。。')
                        break
            # 分页处理改进
            max_retries = 100
            current_page = 0

            while current_page < max_retries:
                try:
                    # 等待新页面加载 next-btn next-small next-btn-normal next-pagination-item next-next  getAttribute：aria-label
                    self.page.wait_for_function('''() => {
                                                            return document.querySelector('button.next-btn.next-small.next-btn-normal.next-pagination-item.next-next')
                                                                .getAttribute('aria-label').includes('下一页，当前第''' + str(
                        current_page + 1) + '''页');
                                                        }''', timeout=10000)

                    # 改进的元素定位方式
                    product_list = self.page.locator('//a[@data-spm-protocol="i"]').all()
                    print(f'当前页商品数量: {len(product_list)}')

                    if product_list:
                        for a in product_list:
                            try:
                                detal_url = (a.get_attribute('href') or '').strip()
                                if not detal_url:
                                    continue
                                self.detal_url = detal_url if detal_url.startswith(
                                    ('http:', 'https:')) else f"https:{detal_url}"
                                print(f"商品链接: {self.detal_url}")
                            except Exception as e:
                                print(f"获取商品链接失败: {str(e)}")
                                continue

                    # 检查拦截层是否存在
                    # has_interception = self.page.wait_for_selector(".J_MIDDLEWARE_FRAME_WIDGET", timeout=1000)
                    has_interception = self.page.evaluate('''() => {
                            return document.querySelector('.J_MIDDLEWARE_FRAME_WIDGET') !== null;
                        }''')

                    print(f'has_interception: {has_interception}')

                    if has_interception:
                        # 移除可能存在的拦截层
                        while True:
                            print(f'滑动开始。。。。。')
                            if self.handle_slider():
                                print(f'滑动结束。。。。。')
                                break

                    # 改进的元素定位方式
                    next_btn = self.page.wait_for_selector(
                        'button.next-btn.next-small.next-btn-normal.next-pagination-item.next-next:not([disabled])',
                        state='visible',
                        timeout=15000
                    )

                    # 随机滚动页面
                    self.page.mouse.wheel(0, random.randint(100, 300))
                    # asyncio.sleep(random.uniform(0.5, 1.5))

                    # 使用JavaScript直接点击
                    self.page.evaluate('(btn) => btn.click()', next_btn)

                    current_page += 1  # 成功则重置重试计数
                except Exception as e:
                    print(f"分页失败(第{current_page}页): {str(e)}")
                    # 尝试滚动页面解除可能的覆盖
                    self.page.mouse.wheel(0, random.randint(200, 500))
                    current_page += 1
                    continue

            return True
        except Exception as ex:
            if self.page:
                self.page.close()
                self.page = None
            if self.browser:
                self.browser.close()
                self.browser = None
            print(f'严重错误: {str(ex)}')
            raise
        finally:
            if hasattr(self, 'page') and self.page and not self.page.is_closed():
                self.page.close()
                self.page = None
    
    
    def handle_slider(self, max_retries=3):
        """改进后的滑块验证处理函数，包含结果判断逻辑"""
        retry_count = 0

        while retry_count < max_retries:
            try:
                # 检查拦截层是否存在
                has_interception = self.page.evaluate('''() => {
                    return document.querySelector('.J_MIDDLEWARE_FRAME_WIDGET') !== null;
                }''')

                if not has_interception:
                    return True  # 拦截层不存在，说明无需验证或已通过

                print(f'滑动处理开始。。。。。')
                # 获取iframe框架
                frame = self.page.wait_for_selector(
                    'iframe[src*="captcha"]',
                    timeout=10000
                )
                iframe = frame.content_frame()

                # 多重定位策略获取滑块元素
                slider = None
                for selector in [
                    '.nc_iconfont.btn_slide',
                    '#nc_1_n1z',
                    '[role="slider"]',
                    '.btn_slide'
                ]:
                    try:
                        slider = iframe.wait_for_selector(
                            selector,
                            timeout=3000,
                            state='visible'
                        )
                        if slider: break
                    except:
                        continue
                print(f'滑动多重定位策略获取滑块元素处理开始。。。。。')
                if not slider:
                    raise Exception("无法定位滑块元素")

                print(f'执行滑块拖动操作素处理开始。。。。。')
                # 执行滑块拖动操作
                slider.hover()
                self.page.mouse.down()
                box = slider.bounding_box()
                start_x = box['x']
                start_y = box['y']
                end_x = start_x + 280

                print(f'拖动滑块起始位置：({start_x}, {start_y})')

                # 模拟人类拖动行为
                for i in range(1, 101):
                    progress = i / 100
                    x = start_x + (end_x - start_x) * (progress ** 0.4)
                    y = start_y + random.gauss(0, 0.4)
                    self.page.mouse.move(x, y)
                    asyncio.sleep(random.uniform(0.02, 0.04))

                self.page.mouse.up()

                # 验证结果判断 - 等待最多5秒验证结果
                try:
                    print(f'方案3：检查是否有错误提示')
                    error_element = iframe.wait_for_selector(
                        '.errloading',  # 淘宝错误提示常见选择器
                        timeout=2000
                    )
                    error_text = error_element.inner_text()
                    if "验证失败" in error_text:
                        print(f"滑块验证失败: {error_text}")
                        error_element.click()
                        return self.handle_slider()

                except TimeoutError:
                    # 未明确判断成功或失败，默认视为失败
                    raise Exception("无法确定验证结果")

            except TimeoutError:
                print("滑块验证超时，正在重试...")
                retry_count += 1
                self.page.reload()
                continue

            except Exception as e:
                print(f"滑块验证出错: {str(e)}")
                retry_count += 1
                # self.page.reload()
                continue

        # 达到最大重试次数仍未成功
        raise Exception(f"滑块验证失败，已达最大重试次数({max_retries})")


if __name__ == '__main__':
    crawl = Async_TPE_Crawl()
    crawl.tpe_exec('https://s.taobao.com/search?page=1&q=%E5%AE%B6%E5%85%B7&spm=a21bo.jianhua%2Fa.201867-main.d5_first.5af92a895rAVOF&tab=all')