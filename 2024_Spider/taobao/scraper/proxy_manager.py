# _*_ coding: utf-8 _*_
# @Time : 2025/8/13 星期三 16:00
# @Author : 韦丽
# @Version: V 1.0
# @File : proxy_manager.py
# @desc :
from typing import Optional

import redis


class ProxyManager:
    def __init__(self):
        self.redis = redis.Redis(
            host='192.168.1.13',
            port=6379
        )

    def get_proxy(self) -> Optional[str]:
        # 4. 从Redis获取代理IP
        proxy = self.redis.rpop('lian')
        print(f'proxy: {proxy}')
        return proxy.decode() if proxy else None

    def save_proxy(self, proxy: str):
        self.redis.lpush('proxy_pool', proxy)