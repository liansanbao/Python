# _*_ coding: utf-8 _*_
# @Time : 2025/8/21 星期四 17:17
# @Author : 韦丽
# @Version: V 1.0
# @File : Async_Wlw_Stock.py
# @desc : 自动统计中国股市股票均线情况

import asyncio
import configparser
import datetime
import json

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from LoggingWLW import logger
from Wlw_repository import WLWRepository

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini', 'utf-8')  # 确保config.ini文件存在

# 获取db配置
db_mysql = config.get('DATABASE', 'db_mysql')

# 获取运行的时间设定（单位：秒）
seconds = config.get('TASKJOB', 'seconds')
sleep = config.get('TASKJOB', 'sleep')

class TaskController:
    def __init__(self, hybkFlag, now_date_list):
        self.is_processing = False
        self.scheduler = None
        self.execTotal = 0
        self.hybkFlag = hybkFlag
        # 交易日
        self.now_date_list = now_date_list

async def batch_task(repo, controller):
    if controller.is_processing:
        return

    try:
        controller.is_processing = True
        # 当日日期取得
        now_date = datetime.date.today().strftime('%Y-%m-%d')
        if len(controller.now_date_list) > controller.execTotal:
            now_date = controller.now_date_list[controller.execTotal]

        # 1. 检索表数据
        crawl_exists = await repo.get_aboard_exists(now_date)
        controller.execTotal += 1
        if crawl_exists:
            # 临时暂停调度器
            controller.scheduler.pause()
            logger.info(f'{datetime.datetime.now().strftime("%Y%m%d %H:%M:%S.%f")}:第{controller.execTotal}次, 开始执行批量任务。 now_date：{now_date}')
            print(
                f'{datetime.datetime.now().strftime("%Y%m%d %H:%M:%S.%f")}:第{controller.execTotal}次, 开始执行批量任务。 now_date：{now_date}')
            # M5、M10、M20、M60、M120、M250值计算并保存至Json文件中
            await repo.get_aboard_list(now_date, controller.hybkFlag)
            # 将检索出来的数据状态更新成已处理
            await repo.update_aboard_status(now_date)
            logger.info(f'{datetime.datetime.now().strftime("%Y%m%d %H:%M:%S.%f")}:第{controller.execTotal}次, 批量任务执行完毕。 now_date：{now_date}')
            print(
                f'{datetime.datetime.now().strftime("%Y%m%d %H:%M:%S.%f")}:第{controller.execTotal}次, 批量任务执行完毕。 now_date：{now_date}')
        else:
            logger.info(f'{datetime.datetime.now().strftime("%Y%m%d %H:%M:%S.%f")}:第{controller.execTotal}次, 没有要执行的任务。 now_date：{now_date}')
            print(f'{datetime.datetime.now().strftime("%Y%m%d %H:%M:%S.%f")}:第{controller.execTotal}次, 没有要执行的任务。 now_date：{now_date}')

        # 2. 采集数据
        # proxy_manager = ProxyManager()
        if controller.execTotal == 1:
            controller.hybkFlag = False

    except Exception as ex:
        logger.error(f'任务异常: {str(ex)}')

    finally:
        controller.is_processing = False
        # 恢复调度器
        if controller.scheduler:
            controller.scheduler.resume()


async def main():
    # 交易日
    now_date_list = [
        '2025-10-08', '2025-10-09', '2025-10-10', '2025-10-13', '2025-10-14', '2025-10-15', '2025-10-16', '2025-10-17', '2025-10-20', '2025-10-21']
    controller = TaskController(True, now_date_list)
    repo = WLWRepository(db_mysql)
    scheduler = AsyncIOScheduler()
    controller.scheduler = scheduler
    scheduler.add_job(
        batch_task,
        'interval',
        seconds=int(seconds),
        args=[repo, controller],
        max_instances=1,
        misfire_grace_time=30)
    scheduler.start()

    try:
        while True:
            await asyncio.sleep(int(sleep))
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
