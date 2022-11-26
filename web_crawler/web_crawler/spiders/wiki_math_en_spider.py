# -*- coding: utf-8 -*-
"""module description
"""

import scrapy
from scrapy.http import TextResponse
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from ..items import DownloadItem


class WikiEnSpider(CrawlSpider):
    """Wikipediaの英語の数学のページをダウンロードするためのクラス．
    TODO:
        CategoryがMathematicsあるいはMathematicsのSubcategoriesである
        ページのみをクロールする．
        サブフォルダを作成する？
    """
    # type 'scrapy crawl wiki_math_en' to crawl.
    name = 'wiki_math_en'
    allowed_domains = [
        'en.wikipedia.org',
    ]

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'FILES_STORE': 'web_pages/wiki/en/math',
        'ITEM_PIPELINES': {'web_crawler.pipelines.DownloadPipeline': 300},
    }

    count = 0
    start_urls = [
        # 数学に関する記事の一覧
        'https://en.wikipedia.org/wiki/Category:Mathematics',
    ]

    category_path = 'wiki/Category:'
    next_page = '/w/index'
    rules = (
        # extract category links to crawl all categories.
        Rule(
            LinkExtractor(
                allow=(category_path, next_page),
                restrict_xpaths=([
                    '//div[@id="mw-subcategories"]',
                    '//a[contains(text(), "next page")]',  # for 'next page' links
                ]),
            )
        ),

        # extract page links to download.
        Rule(
            LinkExtractor(
                allow=('wiki/',),
                restrict_xpaths=(['//div[@id="mw-pages"]']),
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
