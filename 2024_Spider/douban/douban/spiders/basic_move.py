import scrapy


class BasicMoveSpider(scrapy.Spider):
    name = "basic_move"
    allowed_domains = ["xxx.com"]
    start_urls = ["https://xxx.com"]

    def parse(self, response):
        pass
