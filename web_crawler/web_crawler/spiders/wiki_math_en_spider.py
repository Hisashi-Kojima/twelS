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
    category_urls = _load_script('wiki_crawler/spiders/category.txt')
    start_urls = category_urls

    category_path = 'wiki/Category:'
    next_page = '/w/index'
    rules = (
        # extract category links to crawl all categories.
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
