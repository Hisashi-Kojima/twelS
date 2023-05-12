# -*- coding: utf-8 -*-
"""module description
"""

import glob
import os

import scrapy
from scrapy.http.response.html import HtmlResponse

from web_crawler.items import Page
from web_crawler.spiders import functions


class LocalManabitimesSpider(scrapy.Spider):
    # type 'scrapy crawl local_manabitimes' to crawl.
    name = 'local_manabitimes'
    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'ROBOTSTXT_OBEY': False,  # because not exists in local
        # ITEM_PIPELINES raise exception because of path when you type 'scrapy crawl local_wiki'.
        # use local_spider.py.
        'ITEM_PIPELINES': {'web_crawler.web_crawler.pipelines.WebCrawlerPipeline': 300}
    }

    base_path = os.path.abspath(__file__)  # local_nanabitimes_spider.pyのpath
    norm_path = os.path.normpath(os.path.join(base_path, '../../../web_pages'))
    # manabitimesのページを登録
    target_paths = glob.glob(f'{norm_path}/manabitimes/*')
    start_urls = [f'file://{path}' for path in target_paths]

    count = 0

    def parse(self, response: HtmlResponse):
        LocalManabitimesSpider.count += 1
        print(f'{LocalManabitimesSpider.count}番目')
        yield Page(
            uri=self._get_manabitimes_uri(response),
            title=functions.get_title(response),
            snippet=functions.get_snippet(response),
            lang=functions.get_lang(response),
            exprs=functions.get_exprs(response)
        )

    def _get_manabitimes_uri(self, response: HtmlResponse) -> str:
        """manabitimesのページからそのページのURI(URL)を取得する関数．"""
        return response.xpath('//meta[@data-hid="og:url"]/@content').get()
