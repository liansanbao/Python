# !/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/4/3 21:30
# @Author : 连三保
# @Version: V 1.0
# @File : 22_js逆向解析.py
# @desc : 加密参数的处理（爬虫重点）

'''
sign = md5
js代码过多，解析困难，利用Python代码模仿生成加密参数也非常困难
分析：既然我们要的参数是由JS代码运行生成的，那么直接把相关的js加密逻辑代码拿过来运行，得到加密参数

目标：执行JS代码
一。需要安装node.js
   下载地址：https://nodejs.org/en/download
   安装教程：https://cloud.tencent.com/developer/article/2103639
   
二、需要Pycharm做2项配置
   1.settings > plug-in > marketplace > 搜索’Node.js'
        作用：方便调式JS代码
   2.settings > languages& Frameworks > Node.js and NPM 配置安装的nodejs路径

三、重启Pycharm就OK了

四、第三方库
   1、PyExecJS
     pip install PyExecJS -i https://pypi.tuna.tsinghua.edu.cn/simple --user

   2.安装CryptoJS cmd窗口执行
     npm install crypto-js
     import CryptoJS from 'crypto-js';

   3.pip install pycryptodome  python 使用Crypto中的MODE_CBC加密数据
'''
import time
import timeit

import jsonpath
import requests

'''
js逆向笔记
1.js逆向主要找js文件 css html >> 忽略
2.刷新可以实现js断点 但是如果js加密是通过判断网页缓存来执行的话，就最好点击'下一页'
3.调试不同页面的参数发现，没有发生变化的参数，就可以写固定；如果是动态变化，后续就需要根据请求歌曲/页数的变化而变化
4. JSON.stringify(i4m)  把 字典 >> 字符串方法
5.!function() {}(); 自执行函数！ (不需要进行调用，可以自动运行的函数)
6. ReferenceError: window is not defined
    最容易碰到的报错提示  xxxx 没有被定义 ！！
    解决：需要手动定义
    window=global;    window={};    window=this;
7.缺什么补什么！！
ReferenceError: CryptoJS is not defined
8.全局搜索关键字时，可以加空格或者等号进行搜索
9.发现定义的位置在调用位置的上面，而且在同一个文件
  从定义的位置 一直复制到调用的位置  先调试第一遍
  如果定义的变量多了，不调用，没事
'''

import execjs
from datetime import datetime
import requests
from fake_useragent import FakeUserAgent

def timestamp_to_date(ts):
    """
    将时间戳转换为日期对象，支持秒级和毫秒级时间戳。
    :param ts: 时间戳
    :return: 返回格式为：%Y-%m-%d %H:%M:%S 的日期
    """
    try:
        ts = int(ts)
    except ValueError:
        return "时间戳输入错误，请检查后重试！"

    if len(str(ts)) == 10:
        date_obj = datetime.fromtimestamp(ts)
    elif len(str(ts)) == 13:
        date_obj = datetime.fromtimestamp(ts / 1000)
    else:
        return "时间戳输入错误，请检查后重试！"

    return date_obj.strftime("%Y-%m-%d %H:%M:%S")

# js代码执行
def runJs(id, pageNo):
    # 使用文件读写拿到JS文件内容
    with open('22_MyJsFile.js', 'r', encoding='utf-8') as f:
        js_content = f.read()

    # 拿到js代码之后，需要进行一个类似编码的操作
    js_obj = execjs.compile(js_content)

    rid = f'R_SO_4_{id}'
    threadId = f'R_SO_4_{id}'
    pageSize = 20
    cursor = int(datetime.timestamp(datetime.today()) * 1000)
    str_param = '{"rid":"'+rid+'","threadId":"'+threadId+'","pageNo":"'+str(pageNo)+'","pageSize":"'+str(pageSize)+'","cursor":"'+ str(cursor) + '","offset":"20","orderType":"1","csrf_token":""}'

    # 执行js代码
    result = js_obj.call('get', str_param)
    # print(type(result), result)
    return result

def post(url,id, pageNo):
    header = {
        'User-Agent':f'{FakeUserAgent().random}',
        'Cookie':'NMTID=00Omb5MQYlrSBOYi0yTuR4he0JsBv0AAAGVzdjnmQ; _iuqxldmzr_=32; _ntes_nnid=88f046217d425d6367f8135dc35d0c10,1742915299525; _ntes_nuid=88f046217d425d6367f8135dc35d0c10; WEVNSM=1.0.0; WNMCID=ptdsie.1742915301230.01.0; sDeviceId=YD-Zc9TOOclIQVEEgVRBVfTcqSissT7heWI; WM_TID=4eRg84FNLxpBAQFAEBfGZuG2s5NGDo8R; ntes_utid=tid._.smIedhYW9hhARhUBQUaTJ%252FGj88C70Xur._.0; __snaker__id=eu2J34DgoJInRmIY; gdxidpyhxdE=e0tc3YlREu8UEBqYq2IHVc%2Bpl%2FouYOH%2F63b9ajaaVzNfdL17KCJehHPlE3LaLctHH0%2BynOmCYG34iid2ejjjs%2BVVD9z4YVJCHPgDjIaYywh6LTENeiyJ5ymS8m%2ByxwCahGwlOm%2BW12zcMrrHn8pYKBYcUE0tdm2jM9hoScNrQysEi0le%3A1743769898363; WM_NI=bD1RBm%2FC6j9M5BPDluNWIQVz2AqSuRucBrXP15Mpl5afIRks1SdVtOg%2BFVGXvQxAhc1hJgW2uidzkkRmA7c%2Fzy1JNtcSBfqbpOjIJkeXKcFpbQ1QO95Y8Dm2peiYvWw7RUo%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee8beb348caefab4ce4eb3ef8ba7d44e829b9f82db6f879cb7b5e562f6abb6a4b32af0fea7c3b92aa29cffb3c167ed9dfa8bbc47f79ea0a5ef7f8e8987b2d572f29fbfb4f85ab7bd8e93db5cf3eb8391ef3fa3ba87b3ea79f38dacb7f745a5f58ab7c654b68fb8a2eb69f3b88688d63ab7b7ac9bea6192b38fd8e225baa7ffabcd80a18d8e87f46ab491a6aac961a7888584c57ca28fffb2ce33f787f8a5f03ab4bba7baf55db5e99eb6ee37e2a3; JSESSIONID-WYYY=me1vz3w8nAJeHO3Yj%2FaPss9gj9fr73fTUs4yjJEZX8%5C5FZyYUn6IM%2F4zpEM9gGGGuzlSMlXAXkCIoyW5F%5CAo%2BwctNO%2F36z%2FsIWUS%5CjO%5CDiToxXXw1cXnY9l20Aw2aH20GmrmxriF%5C%5CtDaWCKgpDApSl8htP4G3Ke1eoi%2Bpz6g8X3%2F0hu%3A1743998098761',
    }

    data_js_dict = runJs(id, pageNo)
    data_dict = {
        "params":f"{data_js_dict['params']}",
        "encSecKey":f"{data_js_dict['encSecKey']}"
    }
    print(data_dict)
    return requests.post(url, headers=header, data=data_dict)

def runSpider():
    '''
    如果请求的响应的结果为JSON数据，注意一下点
        response.content虽然也是Json数据，但是字符串类型数据是Bytes类型需要转String
        response.json() 返回的是string类型数据无需转换
    :return:
    '''
    result = []
    id = 150633
    for pageNo in range(1, 11):
        response = post('https://music.163.com/weapi/comment/resource/comments/get?csrf_token=', id, pageNo)
        if response.status_code == 200:
            py_data = response.json()
            print(py_data)
            # 用户图片
            avatarUrl_list = jsonpath.jsonpath(py_data, '$..avatarUrl')
            # 用户名称
            nickname_list = jsonpath.jsonpath(py_data, '$..nickname')
            # 评论
            content_list = jsonpath.jsonpath(py_data, '$..content')
            # 评论时间
            timeStr_list = jsonpath.jsonpath(py_data, '$..timeStr')
            # 点赞数量
            likedCount_list = jsonpath.jsonpath(py_data, '$..likedCount')

            # 构造字典数据
            data_dict = zip(avatarUrl_list, nickname_list, content_list, timeStr_list, likedCount_list)

            for i in data_dict:
                dict_data = {
                    '用户图片':i[0],
                    '用户名称':i[1],
                    '评论':i[2],
                    '评论时间':i[3],
                    '点赞数量':i[4]
                }
                result.append(dict_data)
        time.sleep(5)
    print(result)

if __name__ == '__main__':
    runSpider()
    # byte_data = b'\xe5\x85\xa8\xe9\x83\xa8\xe8\xaf\x84\xe8\xae\xba'
    # if isinstance(byte_data, bytes):
    #     string_data = byte_data.decode()
    #     print(string_data)
