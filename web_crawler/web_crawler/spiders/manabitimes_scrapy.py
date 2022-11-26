# -*- coding: utf-8 -*-
"""Download articles of manabitimes.jp.
"""

import scrapy
from scrapy.http import TextResponse
from scrapy.spiders import SitemapSpider

from ..items import DownloadItem


class ManabitimesSpider(SitemapSpider):
    # type 'scrapy crawl manabitimes' to crawl.
    name = 'manabitimes'

    # only page 'manabitimes.jp'
    allowed_domains = [
        'manabitimes.jp',
    ]

    custom_settings = {
        'FILES_STORE': 'wiki_pages/manabitimes',
        'ITEM_PIPELINES': {'wiki_crawler.pipelines.DownloadPipeline': 300},
    }

    count = 0
    sitemap_urls = [
        # List of Physics and math Articles
        'https://manabitimes.jp/sitemap.xml',
    ]

    sitemap_rules = [
        ('math/', 'parse_item'),
        ('physics/', 'parse_item'),
    ]

    def parse_item(self, response: TextResponse) -> scrapy.Item:
        """ページを解析する関数．"""
        return DownloadItem(
            # replace in order to avoid FileNotFoundError because of '/'
            title=response.css('title::text').get().replace('/', '÷'),
            # FilesPipeline needs 'file_urls' and 'files' fields.
            file_urls=[response.url]
        )
