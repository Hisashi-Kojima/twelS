# -*- coding: utf-8 -*-
"""module description
"""

import scrapy
from scrapy_splash import SplashRequest
from scrapy_splash.response import SplashTextResponse

from wiki_crawler.items import Page
from wiki_crawler.spiders import functions


def _load_script(path: str) -> str:
    script = 'scriptが読み込まれていません．'
    with open(path) as f:
        script = f.read()
    return script


class MathSpider(scrapy.Spider):
    # type 'scrapy crawl math' to crawl.
    name = 'math'
    custom_settings = {}
    # start_urls = ['https://qiita.com/e869120/items/b4a0493aac567c6a7240']
    start_urls = ['https://qiita.com/catatsuy/items/d501ae85c99c70d1c104']

    lua_script = _load_script('wiki_crawler/spiders/wait_rendering.lua')

    def parse(self, response):
        yield SplashRequest(
            response.url,
            self._parse_response,
            args={
                'lua_source': MathSpider.lua_script,
            },
            endpoint='execute',
        )

    def _parse_response(self, response: SplashTextResponse):
        """要素を取得してItemに追加する関数．"""
        yield Page(
            uri=response.url,
            title=functions.get_title(response),
            snippet=functions.get_snippet(response),
            lang=functions.get_lang(response),
            exprs=functions.get_exprs(response)
        )
