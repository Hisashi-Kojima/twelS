# -*- coding: utf-8 -*-
"""module description
"""

import scrapy
from scrapy.http import TextResponse
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from ..items import DownloadItem


class WikiSpider(CrawlSpider):
    """Wikipediaの英語の数学のページをダウンロードするためのクラス．
    """
    # type 'scrapy crawl wiki_math_en' to crawl.
    name = 'wiki_math_en'
    allowed_domains = [
        'en.wikipedia.org',
    ]

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'FILES_STORE': 'wiki_pages/en/math',
        'ITEM_PIPELINES': {'wiki_crawler.pipelines.DownloadPipeline': 300},
    }

    count = 0
    start_urls = [
        # 数学に関する記事の一覧
        'https://en.wikipedia.org/wiki/Category:Mathematics',
    ]

    category_path = 'wiki/Category:'
    rules = (
        # extract category links to crawl all categories.
        Rule(LinkExtractor(allow=(category_path,))),

        # extract page links to download.
        Rule(
            LinkExtractor(allow=('wiki/',), deny=(category_path,)),
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
