# Scrapy settings for eastmoney project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
from scrapy.settings.default_settings import RANDOMIZE_DOWNLOAD_DELAY, CONCURRENT_REQUESTS, DOWNLOAD_DELAY, \
    CONCURRENT_REQUESTS_PER_DOMAIN, RETRY_TIMES, RETRY_HTTP_CODES

BOT_NAME = "eastmoney"

SPIDER_MODULES = ["eastmoney.spiders"]
NEWSPIDER_MODULE = "eastmoney.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "eastmoney (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# 文件出力 '/var/output/scrapy/' ** centos
OUTPUT_FILE_PATH = '/var/output/scrapy/'
# 文件出力 '/var/output/scrapy/' ** windows
# OUTPUT_FILE_PATH = 'D:\learing\Python\output\\'

# MongoDB连接配置
MONGODB_HOST = '192.168.1.12'
MONGODB_PORT = 27017
MONGODB_DATABASE = 'eastmoneySpider'
# 个股资金流
MONGODB_COLLECTION_ZJLX = 'zjlx_crawl'
# 行业资金流
MONGODB_COLLECTION_HYZJL = 'hyzjl_crawl'
# 涨停股
MONGODB_COLLECTION_DAILYLIMIT = 'dailylimit_crawl'
# 主力排名
MONGODB_COLLECTION_MAINSTOCK = 'mainstock_crawl'
# 通达信涨停分析
MONGODB_COLLECTION_TDXDAILYLIMIT = 'tdx_dailylimit_crawl'

# MYSQL连接配置
MYSQL_HOST = '192.168.1.12'
MYSQL_PORT = 3306
MYSQL_DATABASE = 'idiom'
MYSQL_USER = 'root'
MYSQL_PASS = 'Lian+2040'
MYSQL_CHARSET = 'utf8mb4'     # 字符编码

# 设置日志文件路径（建议绝对路径）
# LOG_FILE = '/var/log/scrapy/eastmoney_spider.log'
# 设置全局日志级别为INFO（屏蔽DEBUG日志）
LOG_LEVEL = 'INFO'

# 设置主力排名爬取件数: 1至100, 默认：50
MAINSTOCK_PZ = 50
# 设置主力排名爬取页数
MAINSTOCK_PN = 3
# 设置主力排名爬取涨幅大于4
MAINSTOCK_ZF = 4
# 设置主力排名爬取价格大于4
MAINSTOCK_JJ = 4

# 通达信涨停原因数据采集
TDX_COOKIE_STR = 'Hm_lvt_5c4c948b141e4d66943a8430c3d600d0=1751931399; HMACCOUNT=E0736FD4E47DB5C7; ASPSessionID=; LST=00; Hm_lpvt_5c4c948b141e4d66943a8430c3d600d0=1752067365'

# 并发请求数，4个或者5比较安装
CONCURRENT_REQUESTS = 4
# 每个域名并发，2
CONCURRENT_REQUESTS_PER_DOMAIN = 2
# 下载延迟3秒
DOWNLOAD_DELAY = 3
RANDOMIZE_DOWNLOAD_DELAY = True
# 重试3次，遇到403、503这些错误就重试
RETRY_TIMES = 3
RETRY_HTTP_CODES = [403, 503]

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
   "Accept-Language": "en",
    "Cookie":'qgqp_b_id=450dced73e12534b085223494793bc8c; fullscreengg=1; fullscreengg2=1; st_si=77262958631860; st_asi=delete; st_pvi=59833866217406; st_sp=2025-03-25%2022%3A38%3A51; st_inirUrl=https%3A%2F%2Fquote.eastmoney.com%2Fztb%2Fdetail; st_sn=10; st_psi=20250416230447167-113300300813-8910461462',
   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
   "eastmoney.middlewares.EastmoneySpiderMiddleware": 544,
}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   "eastmoney.middlewares.EastmoneyDownloaderMiddleware": 543,
}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    "eastmoney.pipelines.EastmoneyPipeline": 300,
    # "eastmoney.pipelines.EastmoneyMongoPipeline":400,
    "eastmoney.pipelines.EastmoneyMysqlPipeline":200
}

# Set settings whose default value is deprecated to a future-proof value
# REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
