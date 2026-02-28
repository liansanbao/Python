# _*_ coding: utf-8 _*_
# @Time : 2025/7/30 星期三 16:20
# @Author : 韦丽
# @Version: V 1.0
# @File : Fetcher.py
# @desc : 多线程任务
import urllib.request
import urllib.error
from threading import Thread, Lock
from queue import Queue
import time

class Fetcher:
    def __init__(self, threads):
        self.opener = urllib.request.build_opener(urllib.request.HTTPHandler)
        self.lock = Lock()  # 线程同步锁
        self.q_req = Queue()  # 请求队列（存储待抓取URL）
        self.q_ans = Queue()  # 结果队列（存储URL与内容元组）
        self.threads = threads
        self.running = 0  # 正在运行的线程数计数器

        # 启动工作线程池
        for _ in range(threads):
            t = Thread(target=self.thread_get)
            t.daemon = True  # Python 3使用daemon替代setDaemon
            t.start()

    def __del__(self):
        """析构时等待队列任务完成"""
        time.sleep(0.5)
        self.q_req.join()
        self.q_ans.join()

    def task_left(self):
        """返回剩余任务总数"""
        return self.q_req.qsize() + self.q_ans.qsize() + self.running

    def push(self, req):
        """添加任务到队列"""
        self.q_req.put(req)

    def pop(self):
        """从结果队列获取数据"""
        return self.q_ans.get()

    def thread_get(self):
        """工作线程核心方法"""
        while True:
            req = self.q_req.get()

            # 原子操作更新计数器
            with self.lock:
                self.running += 1

            try:
                # Python 3的urllib.request返回bytes类型
                with self.opener.open(req) as response:
                    ans = response.read().decode('utf-8')
            except Exception as e:  # Python 3异常语法变更
                ans = ''
                print(f"Error fetching {req}: {str(e)}")

            self.q_ans.put((req, ans))

            # 原子操作更新计数器
            with self.lock:
                self.running -= 1

            self.q_req.task_done()
            time.sleep(0.1)  # 请求间隔控制

if __name__ == "__main__":
    # 创建10线程抓取实例
    fetcher = Fetcher(threads=10)

    links = [f'http://www.verycd.com/topics/{i}/' for i in range(5420, 5430)]

    # 提交所有任务
    for url in links:
        fetcher.push(url)

    # 处理结果
    while fetcher.task_left():
        url, content = fetcher.pop()
        print(f"{url} -> {len(content)} bytes")
