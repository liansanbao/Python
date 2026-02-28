# _*_ coding: utf-8 _*_
# @Time : 2025/10/23 星期四 23:13
# @Author : 韦丽
# @Version: V 1.0
# @File : EastMoneyPw.py
# @desc : 东方财富网数据模块采集

import datetime
import json
import logging
import os
import sys
import time
import jsonpath
import pymysql
import requests
from fake_useragent import UserAgent
from playwright.sync_api import sync_playwright

from eastmoneyTools import generate_jquery_callback, quote_str, unquote_str, str_to_json, now_date, amountUnitEdit, \
    timestamp_13, str_to_float, str_to_int

with open('db_config.json') as f:
    config = json.load(f)

# 获取日志配置（带默认值）
log_dir = config['logging']['log_dir']

# 确保日志目录存在
os.makedirs(log_dir, exist_ok=True)

# 配置日志文件和级别
logging.basicConfig(
    filename=os.path.join(log_dir, 'EastMoneyPlaywright.log'),
    level=logging.INFO,
    encoding='utf-8',
    # maxBytes=5*1024*1024,
    # backupCount=3,
    # mode='a',
    # format='%(asctime)s %(levelname)-5s %(module)s:%(lineno)s %(message)s'
    format='%(asctime)s %(module)s:%(lineno)s %(levelname)-5s %(message)s'
)

'''
    要求：
        东方财富网数据采集
        1.板块资金流数据
        2.概念数据
        3.涨幅(4%)以上数据
'''
class EastMoneyPlaywright:
    @property
    def logger(self):
        logger = logging.getLogger(self.execType)
        return logging.LoggerAdapter(logger, {"EastMoneyPlaywright": self})

    # 板块资金流数据采集URL
    def hyzjlUrl(self):
        cb = generate_jquery_callback()
        url_base = f'https://push2.eastmoney.com/api/qt/clist/get?cb={cb}&fid=f62&po=1&pz=99&pn={self.current_page}&np=1&fltt=2&invt=2&ut=8dec03ba335b81bf4ebdf7b29ec27d15'
        #           https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery112307581714048690535_1744844737268&fid=f62&po=1&pz=50&pn=1&np=1&fltt=2&invt=2&ut=8dec03ba335b81bf4ebdf7b29ec27d15&fs=m%3A90+t%3A2&fields=f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13
        #           https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery112304437305601807815_1745414051539&fid=f62&po=1&pz=50&pn=1&np=1&fltt=2&invt=2&ut=8dec03ba335b81bf4ebdf7b29ec27d15&fs=m%3A90+t%3A2&fields=f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13
        fs = 'm%3A90+t%3A2'
        fields = 'f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13'
        new_fs = quote_str(fs)
        new_fields = quote_str(unquote_str(fields))
        return f'{url_base}&fs={new_fs}&fields={new_fields}'

    # 概念数据采集URL
    def conceptUrl(self):
        cb = generate_jquery_callback()
        url_base = f'https://push2.eastmoney.com/api/qt/clist/get?cb={cb}&fid=f62&po=1&pz=99&pn={self.current_page}&np=1&fltt=2&invt=2&ut=8dec03ba335b81bf4ebdf7b29ec27d15'
        #           https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery112307581714048690535_1744844737268&fid=f62&po=1&pz=50&pn=1&np=1&fltt=2&invt=2&ut=8dec03ba335b81bf4ebdf7b29ec27d15&fs=m%3A90+t%3A2&fields=f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13
        #           https://push2.eastmoney.com/api/qt/clist/get?cb=jQuery112304437305601807815_1745414051539&fid=f62&po=1&pz=50&pn=1&np=1&fltt=2&invt=2&ut=8dec03ba335b81bf4ebdf7b29ec27d15&fs=m%3A90+t%3A2&fields=f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13
        #
        fs = 'm:90+t:3'
        fields = 'f12%2Cf14%2Cf2%2Cf3%2Cf62%2Cf184%2Cf66%2Cf69%2Cf72%2Cf75%2Cf78%2Cf81%2Cf84%2Cf87%2Cf204%2Cf205%2Cf124%2Cf1%2Cf13'
        new_fs = quote_str(fs)
        new_fields = quote_str(unquote_str(fields))
        return f'{url_base}&fs={new_fs}&fields={new_fields}'

    # 涨幅(4%)以上数据采集URL
    # hs_a_board: {
    #         fs: "m:0+t:6+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2,m:0+t:81+s:262144+f:!2",
    #         table: "hsj",
    #     },
    # 检索KEY：fs: "m:0+t:6+
    # webpack://quotecenter2023/src/components/quotetable/tablepage_config.ts
    def gridistUrl(self):
        base_url = 'https://push2.eastmoney.com/api/qt/clist/get'
        fields = quote_str(unquote_str(
            'f12%2Cf13%2Cf14%2Cf1%2Cf2%2Cf4%2Cf3%2Cf152%2Cf5%2Cf6%2Cf7%2Cf15%2Cf18%2Cf16%2Cf17%2Cf10%2Cf8%2Cf9%2Cf23'))
        fs = quote_str("m:0+t:6+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2,m:0+t:81+s:262144+f:!2")
        cb = generate_jquery_callback()
        ts = timestamp_13()
        return f'{base_url}?np=1&fltt=1&invt=2&cb={cb}&fs={fs}&fields={fields}&fid=f3&pn={self.current_page}&pz=20&po=1&dect=1&ut=fa5fd1943c7b386f172d6893dbfba10b&wbp2u=%7C0%7C0%7C0%7Cweb&_={ts}'

    def Get(self, url):
        if self.execType == 'hyzjl_crawl':
            # 板块资金流数据抓取
            cookie_str = 'st_nvi=nb4rfxyBwRaLY1ibnykCI7e8f; nid=04226935be5b7b9008ad6211850f4aae; nid_create_time=1755043960839; gvi=OpxM2WcqkDrLMwtTFuik6d940; gvi_create_time=1755043960840; qgqp_b_id=d4b99af124ca26c7284b2f9deef7acea; fullscreengg=1; fullscreengg2=1; st_si=41447558843754; st_pvi=46793535339739; st_sp=2025-05-26%2019%3A49%3A52; st_inirUrl=https%3A%2F%2Fwww.eastmoney.com%2F; st_sn=1; st_psi=20251103185801192-113300300820-6186373096; st_asi=delete'
        elif self.execType == 'concept_crawl':
            # 概念数据抓取
            cookie_str = 'qgqp_b_id=6a56383af907485ce0e0d8ee26bffcaf; st_nvi=HSp8NEXYJ6lQsspDvGJPaef5e; nid=056f78ce7884d0e39dd0615d06a7c418; nid_create_time=1754575795555; gvi=QjFEkx_yBtvnBH0QlNFd5ed71; gvi_create_time=1754575795555; fullscreengg=1; fullscreengg2=1; st_si=57482049183770; st_asi=delete; st_pvi=48093117281162; st_sp=2025-08-07%2022%3A09%3A55; st_inirUrl=https%3A%2F%2Fdata.eastmoney.com%2Fbkzj%2Fhy.html; st_sn=2; st_psi=20251029204426987-113300300820-6001282500'
        elif self.execType == 'gridist_crawl':
            #cookie_str = 'qgqp_b_id=6a56383af907485ce0e0d8ee26bffcaf; st_nvi=HSp8NEXYJ6lQsspDvGJPaef5e; nid=056f78ce7884d0e39dd0615d06a7c418; nid_create_time=1754575795555; gvi=QjFEkx_yBtvnBH0QlNFd5ed71; gvi_create_time=1754575795555; fullscreengg=1; fullscreengg2=1; st_si=08315278100656; st_pvi=48093117281162; st_sp=2025-08-07%2022%3A09%3A55; st_inirUrl=https%3A%2F%2Fdata.eastmoney.com%2Fbkzj%2Fhy.html; st_sn=1; st_psi=20251029204724457-113200301321-7385641335; st_asi=delete'
            cookie_str = 'qgqp_b_id=6a56383af907485ce0e0d8ee26bffcaf; st_nvi=HSp8NEXYJ6lQsspDvGJPaef5e; mtp=1; pi=4067047324305984%3Bu4067047324305984%3B%E8%82%A1%E5%8F%8BK3826H2973%3BiHjdlXErj%2BkKjvQzimAaFeCfMpQ72ZHv9fe8TAeYkv%2F%2Bg4g3D1VPoge8xohGiS9kDSbayLyez26o7CNiJur0YjM0JVkeo95oBiOjnoEgVWkWKMTK5v88ahpLoKB6c4U2Kh5JMoqoKELRdQEpZlGI7cTa7o0WPJGYubFVf8DDYBqQ44xZF2k4GYoQQ9%2B%2FIstzpZNn5eCj%3BuFmaB%2BCJj%2FQJWTVmzA0Uxnx%2BpmLllUC026tuKsw81hZhVx52MN6j6RJZqFEzzyWT91Vac%2BGjTZ0FP%2BmxB4v4FKqt0ssgMGwPyvuAZICoVFQQs282Em8p8IhjsqwiRaewk8UEYbLIcP46tdculqiGWY34dpJ3%2Bw%3D%3D; uidal=4067047324305984%e8%82%a1%e5%8f%8bK3826H2973; sid=; ct=Wxew7NtC1XQw-uy03DlrFx57TDKpwxS0Cu5HKNDMBDFQnKeL23iQpR_-UVILtLIN-AmgxkoMyfet4TkvyZZ37hMYvIw7FMH9q7fZIjU4-_leB72aW4QbAWkk7KYO2ME9DnEMEjV9hn41ae4LWTaOwrtoWAX0_MwXzvCSzRQ-x_g; ut=FobyicMgeV5mv3_J9jItPJvNHbAxfZ4lzNz3DZ1a8fFNYnjKkLRSWDoojp5znOY5bleq5XG_Kcdmgtl829iH0qyMOvsu99-DF_LNsVoNam7rTovjK9Wf-xemztNlC1r7HoSK1nt30iUXtFOYNcyDQ-_IPPXeaKw09iZTFnFVm6Ti8ljt7xHGoi57ZRwD1t5HT9W4BOFNWa9DFge1TIGNlFJo5lufinx6WS46XE-22J5xWIRSOleM6a39Bavvs80L2am6RpwqBTwiY9k2XjUh6Q; vtpst=%7c; fullscreengg=1; fullscreengg2=1; st_si=77146627823560; nid=0893ee1e543c3b89bd5896b5463fcce1; nid_create_time=1762424203169; gvi=vI6g4WCDT6rfoTT5mePykc9a5; gvi_create_time=1762424203169; wsc_checkuser_ok=1; st_asi=delete; st_pvi=48093117281162; st_sp=2025-08-07%2022%3A09%3A55; st_inirUrl=https%3A%2F%2Fdata.eastmoney.com%2Fbkzj%2Fhy.html; st_sn=104; st_psi=20251113213557733-113200301321-5803595486'
            #             qgqp_b_id=6a56383af907485ce0e0d8ee26bffcaf; st_nvi=HSp8NEXYJ6lQsspDvGJPaef5e; nid=056f78ce7884d0e39dd0615d06a7c418; nid_create_time=1754575795555; gvi=QjFEkx_yBtvnBH0QlNFd5ed71; gvi_create_time=1754575795555; fullscreengg=1; fullscreengg2=1; st_si=08315278100656; st_asi=delete; st_pvi=48093117281162; st_sp=2025-08-07%2022%3A09%3A55; st_inirUrl=https%3A%2F%2Fdata.eastmoney.com%2Fbkzj%2Fhy.html; st_sn=2; st_psi=20251029214757927-113200301321-8522586932; wsc_checkuser_ok=1
            #             qgqp_b_id=6a56383af907485ce0e0d8ee26bffcaf; st_nvi=HSp8NEXYJ6lQsspDvGJPaef5e; nid=056f78ce7884d0e39dd0615d06a7c418; nid_create_time=1754575795555; gvi=QjFEkx_yBtvnBH0QlNFd5ed71; gvi_create_time=1754575795555; fullscreengg=1; fullscreengg2=1; st_si=08315278100656; st_asi=delete; st_pvi=48093117281162; st_sp=2025-08-07%2022%3A09%3A55; st_inirUrl=https%3A%2F%2Fdata.eastmoney.com%2Fbkzj%2Fhy.html; st_sn=2; st_psi=20251029214757927-113200301321-8522586932; wsc_checkuser_ok=1
            #     30      qgqp_b_id=6a56383af907485ce0e0d8ee26bffcaf; st_nvi=HSp8NEXYJ6lQsspDvGJPaef5e; nid=056f78ce7884d0e39dd0615d06a7c418; nid_create_time=1754575795555; gvi=QjFEkx_yBtvnBH0QlNFd5ed71; gvi_create_time=1754575795555; fullscreengg=1; fullscreengg2=1; st_si=08315278100656; st_asi=delete; st_pvi=48093117281162; st_sp=2025-08-07%2022%3A09%3A55; st_inirUrl=https%3A%2F%2Fdata.eastmoney.com%2Fbkzj%2Fhy.html; st_sn=2; st_psi=20251029214757927-113200301321-8522586932; wsc_checkuser_ok=1
            #     70      qgqp_b_id=6a56383af907485ce0e0d8ee26bffcaf; st_nvi=HSp8NEXYJ6lQsspDvGJPaef5e; nid=056f78ce7884d0e39dd0615d06a7c418; nid_create_time=1754575795555; gvi=QjFEkx_yBtvnBH0QlNFd5ed71; gvi_create_time=1754575795555; fullscreengg=1; fullscreengg2=1; st_si=08315278100656; st_asi=delete; st_pvi=48093117281162; st_sp=2025-08-07%2022%3A09%3A55; st_inirUrl=https%3A%2F%2Fdata.eastmoney.com%2Fbkzj%2Fhy.html; st_sn=2; st_psi=20251029214757927-113200301321-8522586932; wsc_checkuser_ok=1
            #     101     qgqp_b_id=6a56383af907485ce0e0d8ee26bffcaf; st_nvi=HSp8NEXYJ6lQsspDvGJPaef5e; nid=056f78ce7884d0e39dd0615d06a7c418; nid_create_time=1754575795555; gvi=QjFEkx_yBtvnBH0QlNFd5ed71; gvi_create_time=1754575795555; fullscreengg=1; fullscreengg2=1; st_si=08315278100656; st_asi=delete; st_pvi=48093117281162; st_sp=2025-08-07%2022%3A09%3A55; st_inirUrl=https%3A%2F%2Fdata.eastmoney.com%2Fbkzj%2Fhy.html; st_sn=2; st_psi=20251029214757927-113200301321-8522586932; wsc_checkuser_ok=1
            #     150     qgqp_b_id=6a56383af907485ce0e0d8ee26bffcaf; st_nvi=HSp8NEXYJ6lQsspDvGJPaef5e; nid=056f78ce7884d0e39dd0615d06a7c418; nid_create_time=1754575795555; gvi=QjFEkx_yBtvnBH0QlNFd5ed71; gvi_create_time=1754575795555; fullscreengg=1; fullscreengg2=1; st_si=08315278100656; st_asi=delete; st_pvi=48093117281162; st_sp=2025-08-07%2022%3A09%3A55; st_inirUrl=https%3A%2F%2Fdata.eastmoney.com%2Fbkzj%2Fhy.html; st_sn=2; st_psi=20251029214757927-113200301321-8522586932; wsc_checkuser_ok=1
            #     200     qgqp_b_id=6a56383af907485ce0e0d8ee26bffcaf; st_nvi=HSp8NEXYJ6lQsspDvGJPaef5e; nid=056f78ce7884d0e39dd0615d06a7c418; nid_create_time=1754575795555; gvi=QjFEkx_yBtvnBH0QlNFd5ed71; gvi_create_time=1754575795555; fullscreengg=1; fullscreengg2=1; st_si=08315278100656; st_asi=delete; st_pvi=48093117281162; st_sp=2025-08-07%2022%3A09%3A55; st_inirUrl=https%3A%2F%2Fdata.eastmoney.com%2Fbkzj%2Fhy.html; st_sn=2; st_psi=20251029214757927-113200301321-8522586932; wsc_checkuser_ok=1
            #     250     qgqp_b_id=6a56383af907485ce0e0d8ee26bffcaf; st_nvi=HSp8NEXYJ6lQsspDvGJPaef5e; nid=056f78ce7884d0e39dd0615d06a7c418; nid_create_time=1754575795555; gvi=QjFEkx_yBtvnBH0QlNFd5ed71; gvi_create_time=1754575795555; fullscreengg=1; fullscreengg2=1; st_si=08315278100656; st_asi=delete; st_pvi=48093117281162; st_sp=2025-08-07%2022%3A09%3A55; st_inirUrl=https%3A%2F%2Fdata.eastmoney.com%2Fbkzj%2Fhy.html; st_sn=2; st_psi=20251029214757927-113200301321-8522586932; wsc_checkuser_ok=1
            #     273     qgqp_b_id=6a56383af907485ce0e0d8ee26bffcaf; st_nvi=HSp8NEXYJ6lQsspDvGJPaef5e; nid=056f78ce7884d0e39dd0615d06a7c418; nid_create_time=1754575795555; gvi=QjFEkx_yBtvnBH0QlNFd5ed71; gvi_create_time=1754575795555; fullscreengg=1; fullscreengg2=1; st_si=08315278100656; st_asi=delete; st_pvi=48093117281162; st_sp=2025-08-07%2022%3A09%3A55; st_inirUrl=https%3A%2F%2Fdata.eastmoney.com%2Fbkzj%2Fhy.html; st_sn=2; st_psi=20251029214757927-113200301321-8522586932; wsc_checkuser_ok=1
            #             qgqp_b_id=6a56383af907485ce0e0d8ee26bffcaf; st_nvi=HSp8NEXYJ6lQsspDvGJPaef5e; nid=056f78ce7884d0e39dd0615d06a7c418; nid_create_time=1754575795555; gvi=QjFEkx_yBtvnBH0QlNFd5ed71; gvi_create_time=1754575795555; fullscreengg=1; fullscreengg2=1; st_si=08315278100656; st_asi=delete; wsc_checkuser_ok=1; st_pvi=48093117281162; st_sp=2025-08-07%2022%3A09%3A55; st_inirUrl=https%3A%2F%2Fdata.eastmoney.com%2Fbkzj%2Fhy.html; st_sn=5; st_psi=2025102921553193-113200301321-8390298230
            #             qgqp_b_id=6a56383af907485ce0e0d8ee26bffcaf; st_nvi=HSp8NEXYJ6lQsspDvGJPaef5e; nid=056f78ce7884d0e39dd0615d06a7c418; nid_create_time=1754575795555; gvi=QjFEkx_yBtvnBH0QlNFd5ed71; gvi_create_time=1754575795555; fullscreengg=1; fullscreengg2=1; st_si=08315278100656; st_asi=delete; wsc_checkuser_ok=1; st_pvi=48093117281162; st_sp=2025-08-07%2022%3A09%3A55; st_inirUrl=https%3A%2F%2Fdata.eastmoney.com%2Fbkzj%2Fhy.html; st_sn=5; st_psi=2025102921553193-113200301321-8390298230

        header = {
            'User-Agent': UserAgent().random,
            'cookie': cookie_str
        }

        # if self.execType == 'gridist_crawl':
        #     proxies_1 = {'http': f'http://{self.proxies_list[0]}'}
        #     # print(f'{proxies_1}')
        #     return requests.get(url=url, headers=header, proxies=proxies_1, timeout=3)
        print(f'{self.execType} url: {url}')

        return requests.get(url, headers=header, timeout=5)

    # 付费版代理IP取得 需要替换一下URL
    def getProxies(self, num: int = 1):
        url = f'http://api.tianqiip.com/getip?secret=msqo66gmf1kowk4r&num={num}&type=txt&port=1&time=3&mr=1&sign=706041cda2ff3887e387232294db1783'
        ip_list = []
        response = requests.get(url=url)
        if response.status_code == 200:
            # 出力的IP：110.90.14.41:40011\r\n，需要替换\r\n
            ip_str = response.text.split('\r\n')
            ip_list.extend([ip for ip in ip_str if ip != ''])

        tianqiip_formate = f'获取的代码IP：{ip_list}'
        print(tianqiip_formate)
        self.logger.info(f'{self.execType} {tianqiip_formate}')

        return ip_list

    # 数据抓取
    def handler_response(self, response):
        if self.execType == 'hyzjl_crawl':
            # 板块资金流数据抓取
            self.parseHyzjl(response)
        elif self.execType == 'concept_crawl':
            # 概念数据抓取
            return self.parseConcept(response)
        elif self.execType == 'gridist_crawl':
            # 涨幅(4%)以上数据抓取
            return self.parseGridist(response)
        elif self.execType == 'dailylimit_crawl':
            # 涨停板数据抓取
            return self.parseGridist(response)

    # 板块资金流数据抓取
    def parseHyzjl(self, response):
        try:
            json_data = str_to_json(response.body())
            # content
            resultSets_list = jsonpath.jsonpath(json_data, '$..data')
            if resultSets_list[0] == None:
                self.logger.info(f'一共采集了{(self.current_page - 1)}页数据！！！！')
                self.execFlag = False
                return
            # 行业代码
            f12_list = jsonpath.jsonpath(json_data, '$..f12')
            # 行业名称
            f14_list = jsonpath.jsonpath(json_data, '$..f14')
            # 最新价
            f2_list = jsonpath.jsonpath(json_data, '$..f2')
            # 今日涨跌幅
            f3_list = jsonpath.jsonpath(json_data, '$..f3')
            # 今日主力净流入(净额)
            f62_list = jsonpath.jsonpath(json_data, '$..f62')
            # 今日主力净流入(净占比)
            f184_list = jsonpath.jsonpath(json_data, '$..f184')
            # 今日超大单净流入(净额)
            f66_list = jsonpath.jsonpath(json_data, '$..f66')
            # 今日超大单净流入(净占比)
            f69_list = jsonpath.jsonpath(json_data, '$..f69')
            # 今日大单净流入(净额)
            f72_list = jsonpath.jsonpath(json_data, '$..f72')
            # 今日大单净流入(净占比)
            f75_list = jsonpath.jsonpath(json_data, '$..f75')
            # 今日中单净流入(净额)
            f78_list = jsonpath.jsonpath(json_data, '$..f78')
            # 今日中单净流入(净占比)
            f81_list = jsonpath.jsonpath(json_data, '$..f81')
            # 今日小单净流入(净额)
            f84_list = jsonpath.jsonpath(json_data, '$..f84')
            # 今日小单净流入(净占比)
            f87_list = jsonpath.jsonpath(json_data, '$..f87')
            # 今日主力净流入(最大股名称)
            f204_list = jsonpath.jsonpath(json_data, '$..f204')
            # 今日主力净流入(最大股代码)
            f205_list = jsonpath.jsonpath(json_data, '$..f205')

            # 当日日期 yyyymmdd
            now_ymd = now_date()
            result_list = zip(f12_list, f14_list, f2_list, f3_list, f62_list, f184_list, f66_list, f69_list, f72_list,
                              f75_list, f78_list, f81_list, f84_list, f87_list, f204_list, f205_list)
            for item in result_list:
                zjlx_item = {}
                # 行业代码
                zjlx_item["f12"] = item[0]
                # 行业名称
                zjlx_item["f14"] = item[1]
                # 最新价
                zjlx_item["f2"] = str(item[2]) + '元'
                # 今日涨跌幅
                zjlx_item["f3"] = str(item[3]) + '%'
                # 今日主力净流入(净额) amountUnitEdit 这里不需要转换，有画面来转换
                zjlx_item["f62"] = item[4]
                # 今日主力净流入(净占比)
                zjlx_item["f184"] = str(item[5]) + '%'
                # 今日超大单净流入(净额) amountUnitEdit 这里不需要转换，有画面来转换
                zjlx_item["f66"] = amountUnitEdit(item[6])
                # 今日超大单净流入(净占比)
                zjlx_item["f69"] = str(item[7]) + '%'
                # 今日大单净流入(净额) amountUnitEdit 这里不需要转换，有画面来转换
                zjlx_item["f72"] = amountUnitEdit(item[8])
                # 今日大单净流入(净占比)
                zjlx_item["f75"] = str(item[9]) + '%'
                # 今日中单净流入(净额) amountUnitEdit 这里不需要转换，有画面来转换
                zjlx_item["f78"] = amountUnitEdit(item[10])
                # 今日中单净流入(净占比)
                zjlx_item["f81"] = str(item[11]) + '%'
                # 今日小单净流入(净额) amountUnitEdit 这里不需要转换，有画面来转换
                zjlx_item["f84"] = amountUnitEdit(item[12])
                # 今日小单净流入(净占比)
                zjlx_item["f87"] = str(item[13]) + '%'
                # 今日主力净流入(最大股名称)
                zjlx_item["f204"] = item[14]
                # 今日主力净流入(最大股代码)
                zjlx_item["f205"] = item[15]
                # 数据采集日期
                zjlx_item["frq"] = now_ymd
                self.result_data.append(zjlx_item)
        except Exception as ex:
            raise Exception(f'板块资金流数据抓取错误: {str(ex)}')

    # 概念数据抓取
    def parseConcept(self, response):
        try:
            json_data = str_to_json(response.body())
            # self.logger.info(f'json_data: {json_data}')

            # content
            resultSets_list = jsonpath.jsonpath(json_data, '$..data')
            if resultSets_list[0] == None:
                self.logger.info(f'一共采集了{(self.current_page - 1)}页数据！！！！')
                self.execFlag = False
                return

            # 行业代码
            f12_list = jsonpath.jsonpath(json_data, '$..f12')
            # 行业名称
            f14_list = jsonpath.jsonpath(json_data, '$..f14')
            # 最新价
            f2_list = jsonpath.jsonpath(json_data, '$..f2')
            # 今日涨跌幅
            f3_list = jsonpath.jsonpath(json_data, '$..f3')
            # 今日主力净流入(净额)
            f62_list = jsonpath.jsonpath(json_data, '$..f62')
            # 今日主力净流入(净占比)
            f184_list = jsonpath.jsonpath(json_data, '$..f184')
            # 今日超大单净流入(净额)
            f66_list = jsonpath.jsonpath(json_data, '$..f66')
            # 今日超大单净流入(净占比)
            f69_list = jsonpath.jsonpath(json_data, '$..f69')
            # 今日大单净流入(净额)
            f72_list = jsonpath.jsonpath(json_data, '$..f72')
            # 今日大单净流入(净占比)
            f75_list = jsonpath.jsonpath(json_data, '$..f75')
            # 今日中单净流入(净额)
            f78_list = jsonpath.jsonpath(json_data, '$..f78')
            # 今日中单净流入(净占比)
            f81_list = jsonpath.jsonpath(json_data, '$..f81')
            # 今日小单净流入(净额)
            f84_list = jsonpath.jsonpath(json_data, '$..f84')
            # 今日小单净流入(净占比)
            f87_list = jsonpath.jsonpath(json_data, '$..f87')
            # 今日主力净流入(最大股名称)
            f204_list = jsonpath.jsonpath(json_data, '$..f204')
            # 今日主力净流入(最大股代码)
            f205_list = jsonpath.jsonpath(json_data, '$..f205')

            # 当日日期 yyyymmdd
            now_ymd = now_date()
            result_list = zip(f12_list, f14_list, f2_list, f3_list, f62_list, f184_list, f66_list, f69_list, f72_list,
                              f75_list, f78_list, f81_list, f84_list, f87_list, f204_list, f205_list)
            for item in result_list:
                zjlx_item = {}
                # 行业代码
                zjlx_item["f12"] = item[0]
                # 行业名称
                zjlx_item["f14"] = item[1]
                # 最新价
                zjlx_item["f2"] = str(item[2]) + '元'
                # 今日涨跌幅
                zjlx_item["f3"] = str(item[3]) + '%'
                # 今日主力净流入(净额) amountUnitEdit 这里不需要转换，有画面来转换
                zjlx_item["f62"] = item[4]
                # 今日主力净流入(净占比)
                zjlx_item["f184"] = str(item[5]) + '%'
                # 今日超大单净流入(净额) amountUnitEdit 这里不需要转换，有画面来转换
                zjlx_item["f66"] = amountUnitEdit(item[6])
                # 今日超大单净流入(净占比)
                zjlx_item["f69"] = str(item[7]) + '%'
                # 今日大单净流入(净额) amountUnitEdit 这里不需要转换，有画面来转换
                zjlx_item["f72"] = amountUnitEdit(item[8])
                # 今日大单净流入(净占比)
                zjlx_item["f75"] = str(item[9]) + '%'
                # 今日中单净流入(净额) amountUnitEdit 这里不需要转换，有画面来转换
                zjlx_item["f78"] = amountUnitEdit(item[10])
                # 今日中单净流入(净占比)
                zjlx_item["f81"] = str(item[11]) + '%'
                # 今日小单净流入(净额) amountUnitEdit 这里不需要转换，有画面来转换
                zjlx_item["f84"] = amountUnitEdit(item[12])
                # 今日小单净流入(净占比)
                zjlx_item["f87"] = str(item[13]) + '%'
                # 今日主力净流入(最大股名称)
                zjlx_item["f204"] = item[14]
                # 今日主力净流入(最大股代码)
                zjlx_item["f205"] = item[15]
                # 数据采集日期
                zjlx_item["frq"] = now_ymd

                self.result_data.append(zjlx_item)
        except Exception as ex:
            raise Exception(f'概念数据抓取错误: {str(ex)}')

    # 涨幅(4%)以上数据抓取
    def parseGridist(self, response):
        try:
            json_data = str_to_json(response.body())
            print(f'parseGridist: {self.execType} json_data: {json_data}')
            # content
            resultSets_list = jsonpath.jsonpath(json_data, '$..data')
            if resultSets_list[0] == None:
                self.logger.info(f'一共采集了{(self.current_page - 1)}页数据！！！！')
                self.execFlag = False
                return

            # 数据采集
            for item in jsonpath.jsonpath(json_data, '$..data')[0]['diff']:
                # ST 不要
                stockName = str(item['f14'])
                if stockName.find('st') != -1 or stockName.find('ST') != -1:
                    self.logger.info(f"退市股票: {item['f12']}, {item['f14']}, {item['f2']}")
                    continue

                # 价格低于4元的不要
                f2 = str_to_float(item['f2'])
                if f2 < 400:
                    self.logger.info(f"价格低于4元的股票: {item['f12']}, {item['f14']}, {item['f2']}")
                    continue

                # 是否已经采集过 条件1：股票代码不存在需要采集
                if item['f12'] not in self.gridistHybkDict.keys():
                    self.logger.info(f"{item['f12']} 行业板块名称没有，数据采集中...")
                    self.requestDepthData(item)
                else:
                    item['hybk'] = self.gridistHybkDict[item['f12']]
                    if item['hybk'] == 'None':
                        self.logger.info(f"{item['f12']} 行业板块名称不正，数据采集中...")
                        self.requestDepthData(item)
                    else:
                        self.editFields(item)

        except Exception as ex:
            raise Exception(f'涨幅(4%)以上数据抓取错误: {str(ex)}')

    # 深度数据请求编辑
    def requestDepthData(self, item):
        # 深度数据采集
        # https://datacenter-web.eastmoney.com/api/data/v1/get?callback=jQuery112302766616683370249_1751982259257&reportName=RPT_F10_CORETHEME_CONTENT&columns=SECUCODE%2CSECURITY_CODE%2CMAINPOINT%2CMAINPOINT_CONTENT%2CKEY_CLASSIF%2CKEY_CLASSIF_CODE%2CMAINPOINT_NUM%2CKEYWORD&sortColumns=KEY_CLASSIF_CODE%2CMAINPOINT_RANK&sortTypes=1%2C1&source=WEB&client=WEB&filter=(SECURITY_CODE%3D%22601003%22)&_=1751982259258
        depthData_base = 'https://datacenter-web.eastmoney.com/api/data/v1/get'
        callback = generate_jquery_callback()
        columns = 'SECUCODE%2CSECURITY_CODE%2CMAINPOINT%2CMAINPOINT_CONTENT%2CKEY_CLASSIF%2CKEY_CLASSIF_CODE%2CMAINPOINT_NUM%2CKEYWORD'
        new_columns = quote_str(unquote_str(columns))
        sortColumns = 'KEY_CLASSIF_CODE%2CMAINPOINT_RANK'
        new_sortColumns = quote_str(unquote_str(sortColumns))
        sortTypes = '1%2C1'
        new_sortTypes = quote_str(unquote_str(sortTypes))
        filter = f'SECURITY_CODE%3D%22{item["f12"]}%22'
        new_filter = quote_str(unquote_str(filter))
        ts = timestamp_13()
        depthData_url = f'{depthData_base}?callback={callback}&reportName=RPT_F10_CORETHEME_CONTENT&columns={new_columns}&sortColumns={new_sortColumns}&sortTypes={new_sortTypes}' \
                        f'&source=WEB&client=WEB&filter=({new_filter})&_={ts}'
        self.logger.info(f'{item["f12"]}.深度数据_url: {depthData_url}')
        # response = self.Get(depthData_url)
        self.execDepthDataPlayWright(depthData_url)
        self.depthDataItem = item

    # 深度数据采集
    def parseDepthData(self, response):
        try:
            raw_data = self.depthDataItem
            json_data = str_to_json(response.body())
            depthData_list = jsonpath.jsonpath(json_data, '$..data')
            for item in depthData_list[0]:
                # 关键字
                keyword = str(item['KEY_CLASSIF']).strip()
                # 所属板块
                if keyword == '所属板块':
                    raw_data["hybk"] = str(item["MAINPOINT_CONTENT"]).split(" ")[0]
                    # 所属板块保存
                    hybk_dict = {'f12': raw_data['f12'], 'hybk': raw_data["hybk"]}

                    # 更新全局字典
                    self.gridistHybkDict.update(hybk_dict)
                break

            self.editFields(raw_data)
        except Exception as e:
            raise Exception(f"深度数据采集出错: {str(e)}")

    # 采集数据编辑
    def editFields(self, raw_data):
        # 数据处理
        item = {}
        item["f12"] = raw_data["f12"]  # 股票代码
        item["f14"] = str(raw_data["f14"]).strip()  # 股票名称
        item["f2"] = f'{round(str_to_int(raw_data["f2"]) / 100, 2)}'  # 最新价
        item["f3"] = f'{round(str_to_int(raw_data["f3"]) / 100, 2)}%'  # 涨跌幅
        item["f4"] = f'{round(str_to_int(raw_data["f4"]) / 100, 2)}'  # 涨跌额
        item["f5"] = amountUnitEdit(raw_data["f5"], '')  # 成交量(手)
        item["f6"] = amountUnitEdit(raw_data["f6"])  # 成交额
        item["f7"] = f'{round(str_to_int(raw_data["f7"]) / 100, 2)}%'  # 振幅
        item["f8"] = f'{round(str_to_int(raw_data["f8"]) / 100, 2)}%'  # 换手率
        item["f9"] = f'{round(str_to_int(raw_data["f9"]) / 100, 2)}%'  # 市盈率（动态）
        item[
            "f10"] = f'{round(str_to_int(raw_data["f10"]) / 100, 2)}' if f'{round(str_to_int(raw_data["f10"]) / 100, 2)}' != '0.0' else '-'  # 量比
        item["f15"] = f'{round(str_to_int(raw_data["f15"]) / 100, 2)}'  # 最高
        item["f16"] = f'{round(str_to_int(raw_data["f16"]) / 100, 2)}'  # 最低
        item["f17"] = f'{round(str_to_int(raw_data["f17"]) / 100, 2)}'  # 今开
        item["f18"] = f'{round(str_to_int(raw_data["f18"]) / 100, 2)}'  # 昨收
        item["f23"] = f'{round(str_to_int(raw_data["f23"]) / 100, 2)}'  # 市净率
        item["hybk"] = raw_data["hybk"]  # 所属板块
        self.result_data.append(item)

    def __init__(self, execType, maxPage):
        # 初始化数据库连接参数
        self.mysql_host = config['database']['Host']
        self.mysql_port = int(config['database']['Port'])
        self.mysql_db = config['database']['Dbname']
        self.mysql_user = config['database']['User']
        self.mysql_pass = config['database']['Password']
        self.mysql_charset = config['database']['Charset']
        self.execType = execType
        self.max_pages = maxPage

        # 连接对象和游标
        self.conn = None
        self.cursor = None
        # 板块资金流向表数据插入
        self.insert_hyzjl_sql = f"""
            INSERT INTO HYZJL_CRAWL (
               F12,
               F14,
               F2,
               F3,
               F62,
               F184,
               F66,
               F69,
               F72,
               F75,
               F78,
               F81,
               F84,
               F87,
               F204,
               F205,
               ActivateType,
               hyType
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
               F12 = VALUES(F12),
               F14 = VALUES(F14),
               F2 = VALUES(F2),
               F3 = VALUES(F3),
               F62 = VALUES(F62),
               F184 = VALUES(F184),
               F66 = VALUES(F66),
               F69 = VALUES(F69),
               F72 = VALUES(F72),
               F75 = VALUES(F75),
               F78 = VALUES(F78),
               F81 = VALUES(F81),
               F84 = VALUES(F84),
               F87 = VALUES(F87),
               F204 = VALUES(F204),
               F205 = VALUES(F205),
               ActivateType = VALUES(ActivateType),
               hyType = VALUES(hyType)
            """
        # 大盘主力资金表数据插入
        self.insert_gridist_stock_sql = f"""
                            INSERT INTO GRIDIST_STOCK (
                               CREATE_DATE,
                               F12,
                               F14,
                               F2,
                               F3,
                               F4,
                               F5,
                               F6,
                               F7,
                               F8,
                               F9,
                               F10,
                               F15,
                               F16,
                               F17,
                               F18,
                               F23,
                               hybk
                            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                            ON DUPLICATE KEY UPDATE
                               CREATE_DATE = VALUES(CREATE_DATE),
                               F12 = VALUES(F12),
                               F14 = VALUES(F14),
                               F2 = VALUES(F2),
                               F3 = VALUES(F3),
                               F4 = VALUES(F4),
                               F5 = VALUES(F5),
                               F6 = VALUES(F6),
                               F7 = VALUES(F7),
                               F8 = VALUES(F8),
                               F9 = VALUES(F9),
                               F10 = VALUES(F10),
                               F15 = VALUES(F15),
                               F16 = VALUES(F16),
                               F17 = VALUES(F17),
                               F18 = VALUES(F18),
                               F23 = VALUES(F23),
                               hybk = VALUES(hybk)
                            """
        # 中国A股表数据插入
        self.insert_aboard_sql = f"""
                                    INSERT INTO ABOARD (
                                       CREATE_DATE,
                                       F12,
                                       F14,
                                       F2,
                                       F3,
                                       F4,
                                       F5,
                                       F6,
                                       F7,
                                       F8,
                                       F9,
                                       F10,
                                       F15,
                                       F16,
                                       F17,
                                       F18,
                                       F23,
                                       hybk
                                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                                    ON DUPLICATE KEY UPDATE
                                       CREATE_DATE = VALUES(CREATE_DATE),
                                       F12 = VALUES(F12),
                                       F14 = VALUES(F14),
                                       F2 = VALUES(F2),
                                       F3 = VALUES(F3),
                                       F4 = VALUES(F4),
                                       F5 = VALUES(F5),
                                       F6 = VALUES(F6),
                                       F7 = VALUES(F7),
                                       F8 = VALUES(F8),
                                       F9 = VALUES(F9),
                                       F10 = VALUES(F10),
                                       F15 = VALUES(F15),
                                       F16 = VALUES(F16),
                                       F17 = VALUES(F17),
                                       F18 = VALUES(F18),
                                       F23 = VALUES(F23),
                                       hybk = VALUES(hybk)
                                    """

        if self.execType == 'gridist_crawl':
            # 行业板块存储, 减少访问服务器的负担
            self.gridistHybkDict = self.read_existing_json()  # 加载已有的行业板块
            # self.proxies_list = self.getProxies(1)

    # 读取已有的行业板块
    def read_existing_json(self):
        # 读取hybk.json文件中所有信息
        result = {}
        try:
            jsonPath = config['hybk']['output_file_path']
            self.gridistJsonFile = f'{jsonPath}hybk.json'
            with open(self.gridistJsonFile, 'r', encoding='utf-8') as r:
                for line in r:
                    line = line.strip()
                    if line:  # 跳过空行
                        result = dict(json.loads(line))
                        # result[data['f12']] = data['hybk']
        except (FileNotFoundError, json.JSONDecodeError):
            return dict()
        # print(f'result: {result}')
        return result

    # 读取已有的行业板块
    def write_existing_json(self, result: dict = {}):
        # 读取userinfo.json文件中所有信息
        try:
            # jsonPath = self.settings.get('OUTPUT_FILE_PATH')
            # self.gridistJsonFile = f'{jsonPath}hybk.json'
            with open(self.gridistJsonFile, 'w', encoding='utf-8') as w:
                json_data = json.dumps(result, ensure_ascii=False) + '\n'
                w.write(json_data)
        except (FileNotFoundError, json.JSONDecodeError) as ex:
            print(f'hybk Json文件写入失败: {str(ex)}')

    def open_mysql(self):
        # 爬虫启动时建立连接
        self.conn = pymysql.connect(
            host=self.mysql_host,
            port=self.mysql_port,
            user=self.mysql_user,
            password=self.mysql_pass,
            db=self.mysql_db,
            charset=self.mysql_charset,
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cursor = self.conn.cursor()
        self.logger.info(f'MYSQL已经打开了，{self.execType}可以写数据了！！！')

    def close_mysql(self):
        # 爬虫关闭时关闭连接
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        self.logger.info(f'MYSQL关闭了，{self.execType}数据记载完了！！！')

    # 数据入库
    def writeMysql(self, data):
        # 根据item中的操作类型执行不同SQL
        try:
            # 事务开启
            self.open_mysql()
            sale_data = datetime.date.today().strftime('%Y-%m-%d')
            for item in data:
                if self.execType == 'hyzjl_crawl':
                    activateType = '1' if datetime.datetime.now().strftime('%H%M%S') > '150100' else '0'
                    mysql_dict = (item['f12'], item['f14'], item['f2'], item['f3'],
                                  item['f62'], item['f184'], item['f66'], item['f69'],
                                  item['f72'], item['f75'], item['f78'], item['f81'], item['f84'], item['f87'],
                                  item['f204'], item['f205'], activateType, '1')
                    exec_sql = self.insert_hyzjl_sql
                elif self.execType == 'concept_crawl':
                    activateType = '1'
                    mysql_dict = (item['f12'], item['f14'], item['f2'], item['f3'],
                                  item['f62'], item['f184'], item['f66'], item['f69'],
                                  item['f72'], item['f75'], item['f78'], item['f81'], item['f84'], item['f87'],
                                  item['f204'], item['f205'], activateType, '2')
                    exec_sql = self.insert_hyzjl_sql
                elif self.execType == 'gridist_crawl':
                    mysql_dict = (sale_data, item['f12'], item['f14'], item['f2'],
                                  item['f3'], item['f4'], item['f5'], item['f6'],
                                  item['f7'], item['f8'], item['f9'], item['f10'], item['f15'], item['f16'], item['f17'],
                                  item['f18'], item['f23'], item['hybk'])
                    if float(str(item['f3']).replace('%', '')) >= 4:
                        exec_sql = self.insert_gridist_stock_sql
                        self.cursor.execute(exec_sql, mysql_dict)

                    if float(str(item['f2'])) > 0:
                        # 中国A股大盘数据采集
                        exec_sql = self.insert_aboard_sql
                        self.cursor.execute(exec_sql, mysql_dict)

                if self.execType != 'gridist_crawl':
                    self.cursor.execute(exec_sql, mysql_dict)

                self.conn.commit()  # 提交事务
        except pymysql.Error as e:
            self.logger.info(f'{self.execType} 数据登录失败！！！{str(e)}')
            self.conn.rollback()  # 回滚事务
            raise Exception(f"Failed to process item: {str(e)}")
        finally:
            self.logger.info(f'{self.execType} 数据登录成功！！！')
            self.close_mysql()

    # 数据采集URL
    def execUrl(self):
        if self.execType == 'hyzjl_crawl':
            return self.hyzjlUrl()
        elif self.execType == 'concept_crawl':
            return self.conceptUrl()
        elif self.execType == 'gridist_crawl':
            return self.gridistUrl()

    # Get请求
    def getResponse(self):
        url = self.execUrl()
        self.logger.info(f'{self.execType} {url}')
        # return self.Get(url)
        self.execPlayWright(url)

    def execPlayWright(self, url):
        """爬虫程序的入口函数"""
        with sync_playwright() as p:
            # 连接本地启动的浏览器 C:\Program Files\Google\Chrome\Application\chrome.exe
            self.browser = p.chromium.launch_persistent_context(
                executable_path=r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
                user_data_dir=r'D:\chrome_userData', # 在D盘根目录下创建chrome_userData文件夹
                # user_data_dir=r'C:\Users\Administrator\AppData\Local\Google\Chrome\User Data', # 系统默认chrome浏览器数据访问失败
                headless=False)

            try:
                # 选择默认打开的页面
                self.search_page = self.browser.new_page()
                # 添加初始化js脚本代码，隐藏webdriver属性，防止检测出来
                js = "Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});"
                self.search_page.add_init_script(js)
                # 给playwright添加响应事件的侦听处理函数
                self.search_page.on('response', self.handler_response)
                """爬虫执行的主要逻辑"""
                self.search_page.wait_for_timeout(2000)
                try:
                    self.search_page.goto(url, wait_until="domcontentloaded", timeout=2)
                except:
                    self.search_page.goto(url, wait_until="domcontentloaded")

                self.search_page.wait_for_timeout(5000)

                # 关闭页面
                self.search_page.close()
            except Exception as e:
                print(f"数据处理中。。。。。。连接失败： {e}")

    def execDepthDataPlayWright(self, url):
        """爬虫程序的入口函数"""
        with sync_playwright() as p:
            # 连接本地启动的浏览器
            self.browser = p.chromium.launch_persistent_context(
                executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                user_data_dir=r'D:\chrome_userData', # 在D盘根目录下创建chrome_userData文件夹
                # user_data_dir=r'C:\Users\Administrator\AppData\Local\Google\Chrome\User Data', # 系统默认chrome浏览器数据访问失败
                headless=False)

            try:
                # 选择默认打开的页面
                self.search_page = self.browser.new_page()
                # 添加初始化js脚本代码，隐藏webdriver属性，防止检测出来
                js = "Object.defineProperties(navigator, {webdriver:{get:()=>undefined}});"
                self.search_page.add_init_script(js)
                # 给playwright添加响应事件的侦听处理函数
                self.search_page.on('response', self.parseDepthData)
                """爬虫执行的主要逻辑"""
                self.search_page.wait_for_timeout(2000)
                try:
                    self.search_page.goto(url, wait_until="domcontentloaded", timeout=2)
                except:
                    self.search_page.goto(url, wait_until="domcontentloaded")

                self.search_page.wait_for_timeout(5000)

                # 关闭页面
                self.search_page.close()
            except Exception as e:
                print(f"数据处理中。。。。。。连接失败： {e}")

    # 主处理
    def exec(self):
        self.current_page = 1
        self.execFlag = True
        self.logger.info(f'{self.execType} 采集开始！！！')

        # 处理分页
        while self.current_page <= self.max_pages:
            try:
                self.result_data = []

                # 数据抓取
                self.getResponse()

                time.sleep(18)

                # 无数据退出
                if not self.execFlag:
                    break

                # 采集数据处理
                if self.result_data:
                    self.writeMysql(self.result_data)
                mesage = f'{self.execType} 第 {self.current_page} 页采集完了！！！'
                print(mesage)
                self.logger.info(mesage)
            except Exception as ex:
                self.logger.error(f'{str(ex)}')
            finally:
                # time.sleep(2)
                self.current_page += 1

        self.logger.info(f'{self.execType} 采集结束！！！')
        if self.execType == 'gridist_crawl':
            self.write_existing_json(self.gridistHybkDict)

if __name__ == '__main__':
    # 检查参数数量
    # if len(sys.argv) == 3:
    #     execType = sys.argv[1]
    #     maxPage = int(sys.argv[2])
    #     # client = EastMoneyPlaywright('hyzjl_crawl', 1)
    #     # client = EastMoneyPlaywright('concept_crawl', 10)
    #     # client = EastMoneyPlaywright('gridist_crawl', 300)
    #     client = EastMoneyPlaywright(execType, maxPage)
    #     client.exec()

    client = EastMoneyPlaywright('gridist_crawl', 300)
    client.exec()

    sys.exit()
