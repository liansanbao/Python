# Scrapy settings for xiaohongshu project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "xiaohongshu"

SPIDER_MODULES = ["xiaohongshu.spiders"]
NEWSPIDER_MODULE = "xiaohongshu.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "xiaohongshu (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# MongoDB连接配置
MONGODB_HOST = '192.168.1.10'
MONGODB_PORT = 27017
MONGODB_DATABASE = 'xiaohongshuSpider'
MONGODB_COLLECTION = 'xhs_crawl'

# 登录小红书的COOKIE
# COOKIE_STR = 'abRequestId=bb197601-041c-57d5-9124-91293741b13c; a1=196b57fcbc8414dgopmg2tgbnsfxqj8rwexz5sw3750000102108; webId=e5be0ab84c1f53c63f12868a10e28b52; gid=yjKD2WifdjEYyjKD2WiSDdMESY4y4fklU6kJCqW9kDIMiu28CAVYF2888y8Jy8Y8KJ4yY880; xsecappid=xhs-pc-web; webBuild=4.62.3; loadts=1747009934239; acw_tc=0a0bb32017470099352812252eb204eee6cac68618caa4aea3899939654fff; websectiga=f3d8eaee8a8c63016320d94a1bd00562d516a5417bc43a032a80cbf70f07d5c0; sec_poison_id=69a76452-61f1-4815-85e3-fbd70779f2d3; web_session=040069b96eae313016ffdd09143a4b0338db6f'
COOKIE_STR = 'acw_tc=0a0b124a17545464326738569e2281133b9471b4a3e1b91c654c2e2d9dad47; a1=198831ed84bz4ohdhm1mtum0mttma87qjdjirw9lz50000378181; webId=b06c9b4f127681ca7ec08f85d7778b69; gid=yjYYqyddDdV4yjYYqydfYfEj4Du4lxfx6y69V1u76869932860YWAF888qWYyYy8W2iDdD0K; abRequestId=b06c9b4f127681ca7ec08f85d7778b69; webBuild=4.75.2; xsecappid=xhs-pc-web; websectiga=29098a4cf41f76ee3f8db19051aaa60c0fc7c5e305572fec762da32d457d76ae; sec_poison_id=f5cd2f72-6b35-4f67-ba9c-c73771fe8222; web_session=040069b96eae313016fff709a13a4beb689381; loadts=1754546645826; unread={%22ub%22:%22689061230000000005009238%22%2C%22ue%22:%2268932a9b00000000030331a0%22%2C%22uc%22:24}'

# 设置Page数
XHS_PAGE = 3

# 设置日志文件路径（建议绝对路径）
# LOG_FILE = 'xhs_crawl05141.log'
# 设置全局日志级别为INFO（屏蔽DEBUG日志）
LOG_LEVEL = 'DEBUG'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
   "xiaohongshu.middlewares.XiaohongshuSpiderMiddleware": 544,
}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   "xiaohongshu.middlewares.XiaohongshuDownloaderMiddleware": 543,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   "xiaohongshu.pipelines.XiaohongshuPipeline": 400,
   "xiaohongshu.pipelines.XiaohongshuMongoPipeline": 500,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
