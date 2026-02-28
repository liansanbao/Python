# _*_ coding: utf-8 _*_
# @Time : 2025/8/14 星期四 11:20
# @Author : 韦丽
# @Version: V 1.0
# @File : AsyncPlaywright.py
# @desc : chrome 浏览器采集数据
import json
import random
import re
from typing import List, Dict

import asyncio
import jsonpath
from playwright.async_api import async_playwright

class Async_TPA_Crawl:
    def __init__(self):
        self.browser = None
        self.page = None

    async def init_browser(self):
        """初始化浏览器实例 headless=True 无窗口 反之：有窗口"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch_persistent_context(
            executable_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            user_data_dir= r"D:\chrome_userData",
            headless=True
        )

    async def ensure_browser(self):
        """确保浏览器连接有效"""
        if not self.browser:
            print('确保浏览器连接有效')
            await self.init_browser()

    async def reboot(self):
        print('浏览器重启')
        if self.page:
            await self.page.close()
            self.page = None
        if self.browser:
            await self.browser.close()
            self.browser = None
        await self.playwright.stop()

    async def tpa_exec(self, url, proxy) -> bool:
        try:
            await self.ensure_browser()
            print('开始采集数据')
            # 创建新页面（避免页面状态污染）
            self.page = await self.browser.new_page()

            # # 请求头伪装
            await self.page.set_extra_http_headers({
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Referer': 'https://www.taobao.com/'
            })

            # 增强反检测脚本
            await self.page.add_init_script("""
                Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});
            """)

            # 处理可能的登录跳转
            await self.page.route('&zwnj;**/login.**&zwnj;', lambda route: route.continue_())

            # 设置请求拦截
            self.page.on('response', lambda response: asyncio.create_task(self.handle_api_request(response)))

            # 随机延迟访问
            await asyncio.sleep(random.uniform(1, 3))
            await self.page.goto(url, timeout=60000)

            # 等待关键元素
            await self.page.wait_for_selector('body', state='attached')
            # await asyncio.sleep(2)  # 增加等待时间

            return True
        except Exception as ex:
            if self.page:
                await self.page.close()
                self.page = None
            if self.browser:
                await self.browser.close()
                self.browser = None
            print(f'Error: {str(ex)}')
            raise
        finally:
            if self.page and not self.page.is_closed():
                await self.page.close()
            # if self.browser:
            #     await self.browser.close()

    # json数据
    async def handle_api_request(self, response):
        request_url = response.url
        # https://h5api.m.taobao.com/h5/mtop.taobao.pcdetail.data.get/1.0/?jsv=2.7.4&appKey=12574478&t=1754672750412&sign=cd1f61bc098afd9600fbf71130935acb ...
        if response.headers.get('content-type') == 'application/json;charset=UTF-8' and request_url.find(
                'mtop.taobao.pcdetail.data.get/1.0/?') != -1:
            # 获取滚动条滚动时的异步请求响应数据
            str_data = await response.body()
            # 转Json数据
            json_data = await self.str_to_json(str_data)
            # 图片URL
            # thumburl_list = jsonpath.jsonpath(json_data, '$.data.componentsVO.extensionInfoVO.infos[0]..items..text')
            thumburl_list = jsonpath.jsonpath(json_data, '$.data.componentsVO.extensionInfoVO.infos[?(@.title=="优惠")]..items..text')
            print(f'thumburl_list: {thumburl_list}')

    # 将字符串转Json格式
    async def str_to_json(self, str_data):
        # 确保传入的是bytes类型
        if isinstance(str_data, bytes):
            str_result = str_data.decode('utf-8')
        else:
            str_result = str(str_data)
        # 去掉JSONP包装
        start = str_result.find('(') + 1
        end = str_result.rfind(')')
        json_str = str_result[start:end]
        # 解析Json
        return json.loads(json_str)


class Async_TPE_Crawl:
    def __init__(self):
        self.browser = None
        self.page = None

    async def init_browser(self):
        """初始化浏览器实例 headless=True 无窗口 反之：有窗口"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch_persistent_context(
            executable_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            user_data_dir= r"D:\chrome_userData",
            headless=False
        )

    async def ensure_browser(self):
        """确保浏览器连接有效"""
        if not self.browser:
            print('确保浏览器连接有效')
            await self.init_browser()

    async def reboot(self):
        print('浏览器重启')
        if self.page:
            await self.page.close()
            self.page = None
        if self.browser:
            await self.browser.close()
            self.browser = None
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
            self.playwright = None

    async def tpe_exec(self, url, proxy) -> bool:
        try:
            await self.ensure_browser()
            print('开始采集数据')
            # 创建新页面（避免页面状态污染）
            self.page = await self.browser.new_page()

            # 增强反检测脚本
            await self.page.add_init_script("""
                // 禁用WebDriver属性
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                
                // 模拟真实用户环境
                Object.defineProperty(navigator, 'hardwareConcurrency', {value: 4});
                
                // 修改屏幕尺寸属性
                Object.defineProperty(window, 'innerWidth', {value: 1920});
                Object.defineProperty(window, 'innerHeight', {value: 1080});
                
                // 覆盖插件检测
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [{
                        name: 'Chrome PDF Plugin',
                        filename: 'internal-pdf-viewer'
                    }]
                });
            """)

            # 随机延迟访问
            await asyncio.sleep(random.uniform(1, 3))
            response = await self.page.goto(url, timeout=60000, wait_until="domcontentloaded")

            if not response.ok:
                raise Exception(f"页面加载失败, 状态码: {response.status}")

            # 等待关键元素
            try:
                await self.page.wait_for_selector('body', state='attached', timeout=10000)
            except Exception as e:
                print(f"等待元素超时: {str(e)}")
                return False

            await self.page.wait_for_load_state("domcontentloaded", timeout=10000)

            # 分页处理改进
            max_retries = 100
            current_page = 0

            while current_page < max_retries:
                try:
                    # 等待新页面加载 next-btn next-small next-btn-normal next-pagination-item next-next  getAttribute：aria-label
                    await self.page.wait_for_function('''() => {
                                                            return document.querySelector('button.next-btn.next-small.next-btn-normal.next-pagination-item.next-next')
                                                                .getAttribute('aria-label').includes('下一页，当前第''' + str(
                        current_page + 1) + '''页');
                                                        }''', timeout=10000)

                    # 改进的元素定位方式
                    product_list = await self.page.locator('//a[@data-spm-protocol="i"]').all()
                    print(f'当前页商品数量: {len(product_list)}')

                    if product_list:
                        for a in product_list:
                            try:
                                detal_url = (await a.get_attribute('href') or '').strip()
                                if not detal_url:
                                    continue
                                self.detal_url = detal_url if detal_url.startswith(
                                    ('http:', 'https:')) else f"https:{detal_url}"
                                print(f"商品链接: {self.detal_url}")
                            except Exception as e:
                                print(f"获取商品链接失败: {str(e)}")
                                continue

                    # 检查拦截层是否存在
                    # has_interception = await self.page.wait_for_selector(".J_MIDDLEWARE_FRAME_WIDGET", timeout=1000)
                    has_interception = await self.page.evaluate('''() => {
                            return document.querySelector('.J_MIDDLEWARE_FRAME_WIDGET') !== null;
                        }''')

                    print(f'has_interception: {has_interception}')

                    if has_interception:
                        pass
                        # 移除可能存在的拦截层
                        # while True:
                        #     print(f'滑动开始。。。。。')
                        #     if await self.handle_slider():
                        #         print(f'滑动结束。。。。。')
                        #         break

                    # 改进的元素定位方式
                    next_btn = await self.page.wait_for_selector(
                        'button.next-btn.next-small.next-btn-normal.next-pagination-item.next-next:not([disabled])',
                        state='visible',
                        timeout=15000
                    )

                    # 随机滚动页面
                    await self.page.mouse.wheel(0, random.randint(100, 300))
                    await asyncio.sleep(random.uniform(0.5, 1.5))

                    # 使用JavaScript直接点击
                    await self.page.evaluate('(btn) => btn.click()', next_btn)

                    current_page += 1  # 成功则重置重试计数
                except Exception as e:
                    print(f"分页失败(第{current_page}页): {str(e)}")
                    # 尝试滚动页面解除可能的覆盖
                    await self.page.mouse.wheel(0, random.randint(200, 500))
                    await asyncio.sleep(2)
                    current_page += 1
                    continue

            return True
        except Exception as ex:
            if self.page:
                await self.page.close()
                self.page = None
            if self.browser:
                await self.browser.close()
                self.browser = None
            print(f'严重错误: {str(ex)}')
            raise
        finally:
            if hasattr(self, 'page') and self.page and not self.page.is_closed():
                await self.page.close()
                self.page = None

    async def handle_slider(self, max_retries=3):
        """改进后的滑块验证处理函数，包含结果判断逻辑"""
        retry_count = 0

        while retry_count < max_retries:
            try:
                # 检查拦截层是否存在
                has_interception = await self.page.evaluate('''() => {
                    return document.querySelector('.J_MIDDLEWARE_FRAME_WIDGET') !== null;
                }''')

                if not has_interception:
                    return True  # 拦截层不存在，说明无需验证或已通过

                print(f'滑动处理开始。。。。。')
                # 获取iframe框架
                frame = await self.page.wait_for_selector(
                    'iframe[src*="captcha"]',
                    timeout=10000
                )
                iframe = await frame.content_frame()

                # 多重定位策略获取滑块元素
                slider = None
                for selector in [
                    '.nc_iconfont.btn_slide',
                    '#nc_1_n1z',
                    '[role="slider"]',
                    '.btn_slide'
                ]:
                    try:
                        slider = await iframe.wait_for_selector(
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
                await slider.hover()
                await self.page.mouse.down()
                box = await slider.bounding_box()
                start_x = box['x']
                start_y = box['y']
                end_x = start_x + 280

                print(f'拖动滑块起始位置：({start_x}, {start_y})')

                # 模拟人类拖动行为
                for i in range(1, 101):
                    progress = i / 100
                    x = start_x + (end_x - start_x) * (progress ** 1.5)
                    y = start_y + random.gauss(0, 1.5)
                    await self.page.mouse.move(x, y)
                    await asyncio.sleep(random.uniform(0.02, 0.08))

                await self.page.mouse.up()

                # 验证结果判断 - 等待最多5秒验证结果
                try:
                    print(f'方案3：检查是否有错误提示')
                    error_element = await iframe.wait_for_selector(
                        '.errloading',  # 淘宝错误提示常见选择器
                        timeout=2000
                    )
                    error_text = await error_element.inner_text()
                    if "验证失败" in error_text:
                        print(f"滑块验证失败: {error_text}")
                        await error_element.click()
                        raise Exception("滑块验证失败")

                except TimeoutError:
                    # 未明确判断成功或失败，默认视为失败
                    raise Exception("无法确定验证结果")

            except TimeoutError:
                print("滑块验证超时，正在重试...")
                retry_count += 1
                await self.page.reload()
                continue

            except Exception as e:
                print(f"滑块验证出错: {str(e)}")
                retry_count += 1
                # await self.page.reload()
                continue

        # 达到最大重试次数仍未成功
        raise Exception(f"滑块验证失败，已达最大重试次数({max_retries})")

    # async def handle_slider(self):
    #     """手动模拟滑块验证过程"""
    #     # 检查拦截层是否存在
    #     has_interception = await self.page.evaluate('''() => {
    #         return document.querySelector('.J_MIDDLEWARE_FRAME_WIDGET') !== null;
    #     }''')
    #
    #     if has_interception:
    #         try:
    #             # 获取iframe框架
    #             frame = await self.page.wait_for_selector(
    #                 'iframe[src*="captcha"]',
    #                 timeout=10000
    #             )
    #             iframe = await frame.content_frame()
    #
    #             # 多重定位策略获取滑块元素
    #             slider = None
    #             for selector in [
    #                 '.nc_iconfont.btn_slide',  # 淘宝常见滑块选择器
    #                 '#nc_1_n1z',  # 淘宝新版滑块选择器
    #                 '[role="slider"]',  # ARIA角色选择器
    #                 '.btn_slide'  # 通用滑块选择器
    #             ]:
    #                 try:
    #                     slider = await iframe.wait_for_selector(
    #                         selector,
    #                         timeout=3000,
    #                         state='visible'
    #                     )
    #                     if slider: break
    #                 except:
    #                     continue
    #
    #             if not slider:
    #                 raise Exception("无法定位滑块元素")
    #
    #                 # 获取滑块位置信息
    #             await slider.hover()
    #             await self.page.mouse.down()
    #             box = await slider.bounding_box()
    #             start_x = box['x']
    #             start_y = box['y']
    #             end_x = start_x + 280  # 假设滑动距离为280px
    #
    #             print(f'拖动滑块起始位置：({start_x}, {start_y})')
    #
    #             # 优化后的拖动轨迹模拟（带加速度和随机抖动）
    #             for i in range(1, 101):
    #                 progress = i / 100
    #                 # 非线性加速度
    #                 x = start_x + (end_x - start_x) * (progress ** 1.5)
    #                 # 垂直方向随机抖动
    #                 y = start_y + random.gauss(0, 1.5)
    #                 await self.page.mouse.move(x, y)
    #                 # 动态调整延迟时间
    #                 await asyncio.sleep(random.uniform(0.02, 0.08))
    #
    #             await self.page.mouse.up()
    #
    #         except TimeoutError:
    #             await self.page.reload()
    #             return await self.handle_slider()
    #         except Exception as e:
    #             print(f"滑块验证失败: {str(e)}")
    #             await self.page.reload()
    #             return await self.handle_slider()

