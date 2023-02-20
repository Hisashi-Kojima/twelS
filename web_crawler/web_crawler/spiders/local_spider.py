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
    s = Settings()
    s.set('DOWNLOAD_DELAY', 0)
    s.set('REQUEST_FINGERPRINTER_IMPLEMENTATION', '2.7')
    s.set('LOG_LEVEL', 'INFO')
    process = CrawlerProcess(s)
    process.crawl(LocalWikiSpider)
    process.crawl(LocalWikiEnSpider)
    process.crawl(LocalManabitimesSpider)
    process.start()
