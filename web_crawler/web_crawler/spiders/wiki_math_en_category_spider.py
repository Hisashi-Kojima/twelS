# -*- coding: utf-8 -*-
"""module description
"""

import scrapy
from scrapy.http import TextResponse
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class WikiMathCategorySpider(CrawlSpider):
    # type 'scrapy crawl wiki_math_en' to crawl.
    name = 'wiki_math_en_category'
    allowed_domains = [
        'en.wikipedia.org',
    ]

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'DEPTH_LIMIT': 3,
    }

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
                # Category:Main topic classificationsはいらない
                deny=('https://en.wikipedia.org/wiki/Category:Main_topic_classifications'),
            ),
            callback='parse'
        ),
    )

    # Get wiki category links
    def parse(self, response: TextResponse) -> scrapy.Item:
        with open("wiki_crawler/spiders/category.txt", "a", encoding='utf-8',newline="\n") as file:
            file.write(response.url),
            file.write("\n"),
