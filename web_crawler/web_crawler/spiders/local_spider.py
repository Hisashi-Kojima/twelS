# -*- coding: utf-8 -*-
"""run multiple crawlers.
"""
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from local_manabitimes_spider import LocalManabitimesSpider
from local_wiki_spider import LocalWikiSpider, LocalWikiEnSpider


if __name__ == "__main__":
    # multiple spiders run simultaneously.
    # LocalManabitimesSpider ends before LocalWikiSpider.
    file_path = __file__.replace('/web_crawler/web_crawler/spiders/local_spider.py', '/logs/web_crawler/debug.log')
    s = Settings()
    s.set('DOWNLOAD_DELAY', 0)
    s.set('REQUEST_FINGERPRINTER_IMPLEMENTATION', '2.7')
    s.set('LOG_FILE', file_path)
    s.set('LOG_LEVEL', 'INFO')
    process = CrawlerProcess(s)
    process.crawl(LocalWikiSpider)
    process.crawl(LocalWikiEnSpider)
    process.crawl(LocalManabitimesSpider)
    process.start()
