# _*_ coding: utf-8 _*_
# @Time : 2025/4/12 15:49
# @Author : 韦丽
# @Version: V 1.0
# @File : 31_crwalspider模板介绍.py
# @desc :

'''
crawlspider >> 模板 >> 用来创建爬虫任务
basic > 模版 默认的
使用 crawlspider 作为模板创建爬虫任务 》 方便我们提取URL

老任务     新模版
使用     crawlspider 作为模板创建爬虫任务
scrapy genspider 爬虫任务名称 域名.com
scrapy genspider -t crawl 爬虫任务名称 域名.com

使用场景：
   获取文本呀，只能使用basice模板
   获取图片 使用crawl模板

区别：
    basic：
    crawl：
        linkextractors(链接URL提取器)：规范URL的提取范围
            allow=(), 里面写正则去规范要提取哪些URL
            deny=(), 跟allow相反，不常用
            allow_domains=(), 容许的范围域
            deny_domains=(), 相反
            restrict_xpaths=(), 使用xpath来规范一个范围， 再使用allow正则匹配
            tags=("a", "area"), 指定标签
            attrs=("href",), 指定属性


        CrawlSpider:是一个类模板，继承子Spider，功能更加强大
        Rule（规则）：规范URL构造请求对象的规则
    疑问，解析主页的parse方法没有了
      Rule对象，接收
'''