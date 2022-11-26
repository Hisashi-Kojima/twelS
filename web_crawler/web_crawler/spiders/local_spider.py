# -*- coding: utf-8 -*-
"""module description
"""

import glob
import json
import os

import scrapy
from scrapy.http.response.html import HtmlResponse
from scrapy.utils.httpobj import urlparse

from ..items import Page
from ..spiders import functions


class LocalSpider(scrapy.Spider):
    # type 'scrapy crawl local' to crawl.
    name = 'local'
    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'ROBOTSTXT_OBEY': False,  # because not exists in local
        'ITEM_PIPELINES': {'web_crawler.pipelines.WebCrawlerPipeline': 300}
    }

    base_path = os.path.abspath(__file__)  # local_spider.pyのpath
    norm_path = os.path.normpath(os.path.join(base_path, '../../../web_pages'))
    # 数学と物理学のページを登録
    target_paths = glob.glob(f'{norm_path}/wiki/math/*')
    target_paths.extend(glob.glob(f'{norm_path}/wiki/physics/*'))
    start_urls = [f'file://{path}' for path in target_paths]

    count = 0

    def parse(self, response: HtmlResponse):
        LocalSpider.count += 1
        print(f'{LocalSpider.count}番目')
        yield Page(
            uri=self._get_wiki_uri(response),
            title=functions.get_title(response),
            snippet=functions.get_snippet(response),
            lang=functions.get_lang(response),
            exprs=functions.get_exprs(response)
        )

    @staticmethod
    def _get_domain_from_uri(uri: str) -> str:
        """URIからドメインを抽出して返す関数．"""
        parseResult = urlparse(uri)
        return f'{parseResult.scheme}://{parseResult.netloc}'

    def _get_wiki_uri(self, response) -> str:
        """WikipediaのページからそのページのURI(URL)を取得する関数．"""
        info_json: str = response.xpath('//script[@type="application/ld+json"]/text()').get()
        info_dict: dict = json.loads(info_json)
        return info_dict['url']
