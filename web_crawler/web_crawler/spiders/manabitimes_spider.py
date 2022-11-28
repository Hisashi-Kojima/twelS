# -*- coding: utf-8 -*-
"""Download articles of manabitimes.jp.
"""

import scrapy
from scrapy.http import TextResponse
from scrapy.spiders import SitemapSpider

from ..items import DownloadKatexItem
from .functions import render_katex_page


class ManabitimesSpider(SitemapSpider):
    # type 'scrapy crawl manabitimes' to crawl.
    name = 'manabitimes'

    # only page 'manabitimes.jp'
    allowed_domains = [
        'manabitimes.jp',
    ]

    custom_settings = {
        'FILES_STORE': 'web_pages/manabitimes',
        'ITEM_PIPELINES': {'web_crawler.pipelines.DownloadKatexPipeline': 300},
    }

    count = 0

    sitemap_urls = [
        # List of physics and math articles
        'https://manabitimes.jp/sitemap.xml',
    ]

    sitemap_rules = [
        ('math/', 'parse_item'),
        ('physics/', 'parse_item'),
    ]

    def parse_item(self, response: TextResponse) -> scrapy.Item:
        """KaTeXで書かれた数式をrenderしてpipelineに渡す関数。
        """
        rendered_text = render_katex_page(response.text)
        return DownloadKatexItem(
            # replace in order to avoid FileNotFoundError because of '/'
            title=response.css('title::text').get().replace('/', '÷'),
            # FilesPipeline needs 'file_urls' and 'files' fields.
            snippet=rendered_text
        )
