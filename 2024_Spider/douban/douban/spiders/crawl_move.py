import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import *

class CrawlMoveSpider(CrawlSpider):
    name = "crawl_move" # 爬虫名称
    allowed_domains = ["douban.com"] # 容许爬取的域名
    start_urls = ["https://movie.douban.com/top250"] # 起始URL

    rules = ( # 创建了一个Rule对象(创建一个LinkExtractor对象)， 每一个对象都是详情页的请求对象的构造
        # 匹配到的详情页url会自动发送请求
        Rule(LinkExtractor(allow=r"^https://movie.douban.com/subject/\d+/$"), callback="parse_item", follow=False),
        # 下面这个Rule是用来匹配下一页url，没有匹配数据内容的需求所以不需要知道callback, follow=True代表我们匹配到链接发送请求获取响应内容之后，是否还有继续在后面的响应内容使用
        # Rule(LinkExtractor(restrict_xpaths=r"//a[text()='后页>']"), follow=True),
    )

    def parse_item(self, response):# 解析详情页面的方法
        item = DoubanItem()
        # 电影名称
        item["name"] = response.xpath('//h1/span[1]/text()').get()
        # 评分
        item["score"] = response.xpath('//strong/text()').get()
        # 导演
        item["director"] = response.xpath('//div[@id="info"]/span[1]/span/a/text()').get()
        # 海报图片
        item["image_urls"] = [response.xpath('//a[@class="nbgnbg"]/img/@src').get()]
        # 海报图片
        # item["file_urls"] = [response.xpath('//a[@class="nbgnbg"]/img/@src').get()]
        # 海报图片名称
        item["image_name"] = response.xpath('//h1/span[1]/text()').get().split(' ')[0]
        #item["domain_id"] = response.xpath('//input[@id="sid"]/@value').get()
        #item["name"] = response.xpath('//div[@id="name"]').get()
        #item["description"] = response.xpath('//div[@id="description"]').get()
        return item
