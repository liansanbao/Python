# Scrapy settings for douban_redis project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "douban_redis"

SPIDER_MODULES = ["douban_redis.spiders"]
NEWSPIDER_MODULE = "douban_redis.spiders"


# 能够在终端看到cookie的传递传递过程
COOKIES_DEBUG = True

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "douban_redis (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# MongoDB连接配置
MONGODB_HOST = '192.168.1.17'
MONGODB_PORT = 27017

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 2
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
   "Accept-Language": "en",
   "Cookie":'bid=aJnjl0hV6uU; _pk_id.100001.4cf6=1f1cef55d8f5a5cd.1742830123.; __yadk_uid=J8HjHjvQSGrLq0LLUIjLbRxirqH0CwXE; ll="118251"; _vwo_uuid_v2=D9C285026C19E3252FD65A86F57D0D94E|e882b02b4d90d0d8f547652298f2ddbd; push_noty_num=0; push_doumail_num=0; __utmv=30149280.28801; dbcl2="285469272:Wl7bhJ9v9XQ"; __utmz=30149280.1744449432.11.4.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmz=223695111.1744449432.11.4.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/; ck=jfpW; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1744457420%2C%22https%3A%2F%2Faccounts.douban.com%2F%22%5D; _pk_ses.100001.4cf6=1; __utma=30149280.129806767.1742830124.1744449432.1744457420.12; __utmb=30149280.0.10.1744457420; __utmc=30149280; __utma=223695111.1628524852.1742830124.1744449432.1744457420.12; __utmb=223695111.0.10.1744457420; __utmc=223695111',
   "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
SPIDER_MIDDLEWARES = {
   "douban_redis.middlewares.DoubanRedisSpiderMiddleware": 544,
}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   "douban_redis.middlewares.DoubanRedisDownloaderMiddleware": 543,
}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    "douban_redis.pipelines.DoubanRedisPipeline": 400,
# }

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


# 当Redis队列持续空闲超过设定时间后自动关闭爬虫‌
CLOSESPIDER_TIMEOUT = 120  # 30分钟后强制终止: 1800

# redis数据库连接
REDIS_URL = 'redis://192.168.1.17:6379'
# 'REDIS_URL': 'url',
# 'REDIS_HOST': 'host',
# 'REDIS_PORT': 'port',
# 'REDIS_DB': 'db',
# 'REDIS_ENCODING': 'encoding',

DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
# 配置持久化 # 默认True（True会导致空跑）
SCHEDULER_PERSIST = False
# SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderPriorityQueue"
# SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderQueue"
# SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderStack"

# 管道配置
ITEM_PIPELINES = {
    # "example.pipelines.ExamplePipeline": 300,
    # "scrapy_redis.pipelines.RedisPipeline": 400
   "douban_redis.pipelines.DoubanRedisMyPipeline": 500
}

LOG_LEVEL = "DEBUG"