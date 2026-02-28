# _*_ coding: utf-8 _*_
# @Time : 2025/8/14 星期四 11:50
# @Author : 韦丽
# @Version: V 1.0
# @File : Kill_Processes.py
# @desc :
import sys

import psutil
import subprocess
import time


def kill_chrome_processes():
    """彻底清理残留Chrome进程"""
    try:
        chrome_processes = [p for p in psutil.process_iter(['name'])
                            if 'chrome' in p.info['name'].lower()]

        for proc in chrome_processes:
            try:
                print('彻底清理残留Chrome进程')
                proc.kill()
            except:
                pass

        # Windows系统额外清理
        if sys.platform == 'win32':
            subprocess.run(['taskkill', '/f', '/im', 'chrome.exe'],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)

        time.sleep(2)  # 确保进程完全终止
    except Exception as e:
        print(f"Cleanup error: {str(e)}")


# 在程序启动时清理残留进程
kill_chrome_processes()
