# -*- coding: utf-8 -*-
"""module description
made by Hisashi
"""

import glob
import json
import os

import scrapy
from scrapy.http.response.html import HtmlResponse

from wiki_crawler.items import Page
from wiki_crawler.spiders import functions


class LocalMathSpider(scrapy.Spider):
    # type 'scrapy crawl local_math' to crawl.
    name = 'local_math'
    custom_settings = {
        'DOWNLOAD_DELAY': 0,
        'ROBOTSTXT_OBEY': False  # because not exists in local
    }

    base_path = os.path.abspath(__file__)  # local_math_spider.pyのpath
    path = os.path.normpath(os.path.join(base_path, '../../../wiki_pages'))
    math_paths = glob.glob(f'{path}/math/*')
    # physics_paths = glob.glob(f'{path}/physics/*')
    start_urls = [f'file://{path}' for path in math_paths]

    count = 0

    def parse(self, response: HtmlResponse):
        LocalMathSpider.count += 1
        print(f'{LocalMathSpider.count}番目')
        yield Page(
            uri=self._get_wiki_uri(response),
            title=functions.get_title(response),
            descr=functions.get_description(response),
            lang=functions.get_lang(response),
            exprs=functions.get_exprs(response)
        )

    def _get_wiki_uri(self, response) -> str:
        """WikipediaのページからそのページのURI(URL)を取得する関数．"""
        info_json: str = response.xpath('//script[@type="application/ld+json"]/text()').get()
        info_dict: dict = json.loads(info_json)
        return info_dict['url']
