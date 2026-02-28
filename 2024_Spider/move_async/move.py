# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/4/11 21:38
# @Author : 连三保
# @Version: V 1.0
# @File : move.py
# @desc :https://movie.douban.com/top250

import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

def parse(html):
    soup = BeautifulSoup(html, 'lxml')
    movies = []
    for item in soup.find_all('div', class_='item'):
        rank = item.find('em').text
        title = item.find('span', class_='title').text
        rating_num = item.find('span', class_='rating_num').text
        movies.append({
            'rank': rank,
            'title': title,
            'rating': rating_num
        })
    return movies


async def main():
    base_url = 'https://movie.douban.com/top250'
    tasks = []

    # 创建异步会话
    async with aiohttp.ClientSession() as session:
        for i in range(10):
            url = f'{base_url}?start={i * 25}&filter='
            print(f'爬取的URL：{url}')
            tasks.append(asyncio.create_task(fetch(session, url)))

        # 等待所有请求完成
        html_contents = await asyncio.gather(*tasks)

        # 解析并存储数据
        all_movies = []
        for html in html_contents:
            movies = parse(html)
            all_movies.extend(movies)

        # 将数据写入文件（这里以JSON格式为例）
        with open('douban_movies.json', 'w', encoding='utf-8') as f:
            json.dump(all_movies, f, ensure_ascii=False, indent=4)


# 运行主函数
asyncio.run(main())