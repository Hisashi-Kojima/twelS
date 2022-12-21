# -*- coding: utf-8 -*-
"""module description
"""

import scrapy
from scrapy.http import TextResponse
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from ..items import DownloadItem


# Read the entire file as a list
def _load_script(path: str) -> str:
    script = 'scriptが読み込まれていません．'
    with open(path) as f:
        script = f.readlines()
    return script


class MathSpider(CrawlSpider):
    # type 'scrapy crawl math' to crawl.
    name = 'economics'

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'FILES_STORE': 'wiki_pages/economics',
        'ITEM_PIPELINES': {'wiki_crawler.pipelines.DownloadPipeline': 300},
        # 'DEPTH_LIMIT': 2,
    }

    count = 0
    category_urls = _load_script('wiki_crawler/spiders/category.txt')
    start_urls = category_urls
    # start_urls = ['https://ja.wikipedia.org/wiki/Category:%E7%B5%8C%E6%B8%88%E5%AD%A6']

    category_path = 'wiki/Category:'
    next_page = '/w/index'
    rules = (
        Rule(
            LinkExtractor(
                allow=(category_path, next_page),
                restrict_xpaths=([
                    '//a[contains(text(), "next page")]',  # for 'next page' links
                ]),
            )
        ),
        # extract page links to download.
        Rule(
            LinkExtractor(
                allow=('wiki/',),
                restrict_xpaths=([
                    '//*[@id="mw-pages"]'
                ]),
            ),
            callback='parse_item'
        ),
    )


    def parse_item(self, response: TextResponse) -> scrapy.Item:
        """ページを解析する関数．"""
        return DownloadItem(
            # replace in order to avoid FileNotFoundError because of '/'
            title=response.css('title::text').get().replace('/', '÷'),
            # FilesPipeline needs 'file_urls' and 'files' fields.
            file_urls=[response.url]
        )