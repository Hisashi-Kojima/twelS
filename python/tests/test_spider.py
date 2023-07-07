# -*- coding: utf-8 -*-
"""module description
"""
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from tests.functions import reset_tables
from web_crawler.web_crawler.spiders.local_wiki_spider import LocalTestSpider


def test_crawl_1():
    """正常にクロールできるか確認。
    """
    s = Settings()
    s.set('DOWNLOAD_DELAY', 0)
    s.set('ROBOTSTXT_OBEY', False)  # because not exists in local
    s.set('ITEM_PIPELINES', {'web_crawler.web_crawler.pipelines.TestCrawlerPipeline': 300})

    try:
        process = CrawlerProcess(s)
        process.crawl(LocalTestSpider)
        process.start()  # the script will block here until the crawling is finished.
        assert True

    finally:
        reset_tables
