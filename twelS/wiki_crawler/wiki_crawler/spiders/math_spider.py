# -*- coding: utf-8 -*-
"""module description
made by Hisashi
"""

import scrapy
from scrapy_splash import SplashRequest

from wiki_crawler.items import Page
from wiki_crawler.spiders import functions

import sys
from pathlib import Path
path = Path(__file__)  # math_spider.pyのpath
sys.path.append(str(path.parent.parent.parent.parent))  # src/twelS


def _load_script(path: str) -> str:
    script = 'scriptが読み込まれていません．'
    with open(path) as f:
        script = f.read()
    return script


class MathSpider(scrapy.Spider):
    # type 'scrapy crawl math' to crawl.
    name = 'math'
    custom_settings = {}
    start_urls = ['https://qiita.com/e869120/items/b4a0493aac567c6a7240']

    lua_script = _load_script('wiki_crawler/spiders/wait_rendering.lua')

    def parse(self, response):
        yield SplashRequest(
            response.url,
            self._parse_response,
            endpoint='execute',
            args={
                'lua_source': MathSpider.lua_script,
            }
        )

    def _parse_response(self, response):
        """要素を取得してItemに追加する関数．"""
        yield Page(
            uri = response.url,
            title = functions.get_description(response),
            descr = functions.get_description(response),
            lang = functions.get_lang(response),
            exprs = functions.get_exprs(response)
        )
