# _*_ coding: utf-8 _*_
# @Time : 2025/8/14 星期四 11:48
# @Author : 韦丽
# @Version: V 1.0
# @File : Async_TPA_Scheduler.py
# @desc : 淘宝商品活动数据采集任务调度
import asyncio
import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from scraper.AsyncPlaywright import Async_TPA_Crawl
from scraper.proxy_manager import ProxyManager
from database.mysql_repository import MySQLRepository
from utils.Kill_Processes import kill_chrome_processes

class TaskController:
    def __init__(self):
        self.is_processing = False
        self.scheduler = None

async def batch_task(repo, crawl, controller):
    if controller.is_processing:
        return

    try:
        controller.is_processing = True
        print(f'{datetime.datetime.now().strftime("%Y%m%d %H:%M:%S.%f")}:开始执行批量任务')

        # 1. 检索表数据
        crawl_exists = await repo.get_product_exists(['0', '1'])
        if crawl_exists:
            # 临时暂停调度器
            controller.scheduler.pause()
            # 检索数据进行活动数据采集
            await repo.get_product_list(['0', '1'], crawl)

        # 2. 采集数据
        # proxy_manager = ProxyManager()

    except Exception as ex:
        print(f'任务异常: {str(ex)}')

    finally:
        controller.is_processing = False
        # 恢复调度器
        if controller.scheduler:
            controller.scheduler.resume()
        print(f'{datetime.datetime.now().strftime("%Y%m%d %H:%M:%S.%f")}:批量任务执行完毕')


async def main():
    controller = TaskController()
    repo = MySQLRepository("root:Lian+2040@192.168.1.13:3306/taobao")
    crawl = Async_TPA_Crawl()
    scheduler = AsyncIOScheduler()
    controller.scheduler = scheduler
    scheduler.add_job(
        batch_task,
        'interval',
        seconds=60,
        args=[repo, crawl, controller],
        max_instances=1,
        misfire_grace_time=30)
    scheduler.start()

    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        scheduler.shutdown()


if __name__ == "__main__":
    # 在程序启动时清理残留进程
    # kill_chrome_processes()
    asyncio.run(main())
    # 执行流程说明：
    # 1. 初始每10秒检查一次数据库
    # 2. 当检测到待处理URL时暂停定时检查
    # 3. 顺序处理所有URL数据
    # 4. 处理完成后恢复10秒间隔检查
    # 5. 循环执行上述过程