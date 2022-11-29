# -*- coding: utf-8 -*-
"""run multiple crawlers.
"""
from scrapy.crawler import CrawlerProcess

from local_manabitimes_spider import LocalManabitimesSpider
from local_wiki_spider import LocalWikiSpider


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(LocalWikiSpider)
    process.crawl(LocalManabitimesSpider)
    process.start()
