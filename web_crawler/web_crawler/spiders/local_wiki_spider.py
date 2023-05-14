# -*- coding: utf-8 -*-
"""module description
"""

import glob
import json
import os

import scrapy
from scrapy.http.response.html import HtmlResponse

from web_crawler.web_crawler.items import Page
from web_crawler.web_crawler.spiders import functions


settings = {
        'DOWNLOAD_DELAY': 0,
        'ROBOTSTXT_OBEY': False,  # because not exists in local
        # ITEM_PIPELINES raise exception because of path when you type 'scrapy crawl local_wiki'.
        # use local_spider.py.
        'ITEM_PIPELINES': {'web_crawler.web_crawler.pipelines.WebCrawlerPipeline': 300}
    }
base_path = os.path.abspath(__file__)  # local_wiki_spider.pyのpath

def _get_wiki_uri(response: HtmlResponse) -> str:
    """WikipediaのページからそのページのURI(URL)を取得する関数．"""
    info_json: str = response.xpath('//script[@type="application/ld+json"]/text()').get()
    info_dict: dict = json.loads(info_json)
    return info_dict['url']


class LocalWikiSpider(scrapy.Spider):
    # type 'scrapy crawl local_wiki' to crawl.
    name = 'local_wiki'
    custom_settings = settings
    
    norm_path = os.path.normpath(os.path.join(base_path, '../../../web_pages/wiki'))
    # 数学と物理学、経済学のページを登録
    target_paths = glob.glob(f'{norm_path}/math/*')
    target_paths.extend(glob.glob(f'{norm_path}/physics/*'))
    target_paths.extend(glob.glob(f'{norm_path}/economics/*'))
    start_urls = [f'file://{path}' for path in target_paths]

    count = 0

    def parse(self, response: HtmlResponse):
        LocalWikiSpider.count += 1
        print(f'{LocalWikiSpider.count}番目')
        yield Page(
            uri=_get_wiki_uri(response),
            title=functions.get_title(response),
            snippet=functions.get_snippet(response),
            lang=functions.get_lang(response),
            exprs=functions.get_exprs(response)
        )


class LocalWikiEnSpider(scrapy.Spider):
    # type 'scrapy crawl local_wiki_en' to crawl.
    name = 'local_wiki_en'
    custom_settings = settings

    norm_path = os.path.normpath(os.path.join(base_path, '../../../web_pages/wiki/en'))
    # 数学のページを登録
    target_paths = glob.glob(f'{norm_path}/math/*')
    start_urls = [f'file://{path}' for path in target_paths]

    count = 0

    def parse(self, response: HtmlResponse):
        LocalWikiEnSpider.count += 1
        print(f'{LocalWikiEnSpider.count}番目')
        yield Page(
            uri=_get_wiki_uri(response),
            title=functions.get_title(response),
            snippet=functions.get_snippet(response),
            lang=functions.get_lang(response),
            exprs=functions.get_exprs(response)
        )
