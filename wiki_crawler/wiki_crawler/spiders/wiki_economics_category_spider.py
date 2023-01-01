# -*- coding: utf-8 -*-
"""module description
"""

import scrapy
from scrapy.http import TextResponse
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from ..items import DownloadItem


class WikiEconomicsCategorySpider(CrawlSpider):
    # type 'scrapy crawl wiki_economics' to crawl.
    name = 'economics_category'
    allowed_domains = [
        'ja.wikipedia.org',
    ]

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'DEPTH_LIMIT': 3,
    }

    count = 0
    start_urls = [
        # 経済学に関する記事の一覧
        'https://ja.wikipedia.org/wiki/Category:%E7%B5%8C%E6%B8%88%E5%AD%A6',
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
                ]),
            )
        ),

        # extract page links to download.
        Rule(
            LinkExtractor(
                allow=('wiki/Category:'),
                restrict_xpaths=([
                    '//*[@id="mw-normal-catlinks"]',
                ]),
                # Category:学科別分類はいらない
                deny=('https://ja.wikipedia.org/wiki/Category:%E5%AD%A6%E7%A7%91%E5%88%A5%E5%88%86%E9%A1%9E'),
            ),
            callback='parse'
        ),
    )

    # Get wiki category links
    def parse(self, response: TextResponse) -> scrapy.Item:
        with open("wiki_crawler/spiders/category.txt", "a", encoding='utf-8',newline="\n") as file:
            file.write(response.url),
            file.write("\n"),

