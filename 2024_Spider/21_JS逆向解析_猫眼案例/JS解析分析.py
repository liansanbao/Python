# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/3/29 14:17
# @Author : 连三保
# @Version: V 1.0
# @File : JS解析分析.py
# @desc :
'''
如何取得JS代码, 得到加密参数值

首先下载node.js
 -- 下载地址：https://nodejs.org/en/download/package-manager
 --  安装说明：https://cloud.tencent.com/developer/article/2103639
      cmd 窗口 输入: node -v 出现版本号说明安装成功了
 二。需要pycharm里配置 pycharm 必须为专业版
    --https://blog.csdn.net/weixin_45081575/article/details/105223948
    1.--文件--设置--插件--搜索(nodejs)
    --作用：方便直接在js文件调式js代码
    2.--文件--设置--语言和框架--配置好node.exe和npmd 路径
 三。重启pycharm

实战
  1.下载一个第三库 PyExecJS pip install PyExecJS

  实战项目：
   https://piaofang.maoyan.com/dashboard-ajax?
      orderType=0
      &uuid=195d664f88dc8-0898cbbf1fec4c-26011d51-1fa400-195d664f88dc8
      &timeStamp=1744070782192
      &User-Agent=TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEzNC4wLjAuMCBTYWZhcmkvNTM3LjM2
      &index=921
      &channelId=40009
      &sVersion=2
      &signKey=d31babb8e0bdc2a37218b0259ca4270b
      &WuKongReady=h5
'''
import os
import re

import execjs
import jsonpath
import pandas
import requests
from PIL import Image, ImageDraw, ImageFont
from ddddocr import DdddOcr
from fontTools.ttLib import TTFont
from fake_useragent import FakeUserAgent

# 获取字体文件密文字符和明文字形的关系
def parser_font(fontfile):
    font_obj = TTFont(fontfile)
    cmap_dict = font_obj.getBestCmap()
    ocr = DdddOcr(show_ad=False)
    print(f'字体原生内容： {cmap_dict}')
    key_map = {}
    for k, v in cmap_dict.items():
        name = chr(k)
        # 创建一个图像
        img = Image.new('RGB', (200, 200), color='red')
        # 创建一个在图片中绘-g制内容的画笔
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(fontfile, size=150)
        # 在图片中绘制内容
        draw.text(xy=(50, 50), text=name, font=font, fill='pink')
        # 识别字符对应的字形是什么
        value = ocr.classification(img)
        key_map[v] = value
    return key_map

# 请求某些参数进行加密
def getRequestParam(userAgent):
    # 1.使用文件的读写拿到js文件里面的代码
    with open('maoyan.js', 'r', encoding='utf-8') as r:
        js_data = r.read()

    # 2.拿到js代码时候，需要进行一个类似编码的操作
    js_obj = execjs.compile(js_data)

    # 3.执行js代码
    re = js_obj.call('getQueryKey', userAgent)
    return re

# 发送请求
def getRequests():
    userAgent = FakeUserAgent().random
    param = getRequestParam(userAgent)
    header = {
        'User-Agent':userAgent
    }

    url = 'https://piaofang.maoyan.com/dashboard-ajax?orderType=0&uuid=19b797640acc8-0f834cbc521c858-26061a51-1fa400-19b797640adc8' \
          '&timeStamp='+ str(param['timeStamp']) +'&User-Agent='+ param['User-Agent'] +'&index='+ str(param['index']) +'' \
          '&channelId='+ str(param['channelId']) +'&sVersion='+ str(param['sVersion']) +'&signKey='+ param['signKey'] +'&WuKongReady=h5'

    print(f'爬取的URL： {url}')
    return requests.get(url, headers=header)

# 响应数据处理
def run():
    try:
        response = getRequests()
        json_data = response.json()
        print(f'爬取的结果：{json_data}')
        # 字体URL取得
        rank_list = jsonpath.jsonpath(json_data, '$..fontStyle')
        str_woff = re.findall(r',url\("(.*?)"\);', rank_list[0])[0]
        woff_url = "https:" + str_woff
        woff_name = str_woff.split('/font/')[1]

        print(f'已下载的字体文件：{woff_url, woff_name}')
        if not os.path.exists(woff_name):
            woff_response = requests.get(woff_url)
            if woff_response.status_code == 200:
                with open(woff_name, 'wb') as write:
                    write.write(woff_response.content)
        res = parser_font(woff_name)
        # print(f'字体处理结果：{res}')
        # 影片名称
        movieName_list = jsonpath.jsonpath(json_data, '$..movieInfo.movieName')
        # 综合票房 boxSplitUnit
        box_num_list = jsonpath.jsonpath(json_data, '$..boxSplitUnit.num')
        box_num_list_up = []
        for i in box_num_list:
            i = str(i).upper().replace('&#X', 'uni', -1).replace(';', '')
            for k, v in res.items():
                i = i.replace(k, v, -1)

            box_num_list_up.append(i)
        # print(f'综合票房split: {splitnum_list}')
        # 票房占比
        boxRate_list = jsonpath.jsonpath(json_data, '$..boxRate')
        # 排片场次
        showCount_list = jsonpath.jsonpath(json_data, '$..showCount')

        result_dict = zip(movieName_list, box_num_list_up, boxRate_list, showCount_list)
        result_list = []
        for item in result_dict:
            result_list.append([item[0], item[1], item[2], item[3]])

        pandas_data = pandas.DataFrame(data=result_list, columns=['影片名称', '综合票房', '票房占比', '排片场次'])

        # 猫眼实时数据保存
        pandas_data.to_csv('maoyan.csv')
    except Exception as e:
        print(f'报错了："{str(e)}')

if __name__ == '__main__':
    # 此方法不可行了
    print('此采集方法不可行了！！！')
    run()