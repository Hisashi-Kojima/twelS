# -*- coding: utf-8 -*-
"""module description
made by Hisashi
"""

from wiki_crawler.wiki_crawler.spiders.local_math_spider import LocalMathSpider


def test_get_domain_from_uri_1():
    """与えたURIからドメインを正しく抽出できているか確認するテスト"""
    expected = 'https://docs.scrapy.org'
    uri = 'https://docs.scrapy.org/en/latest/_modules/scrapy/spidermiddlewares/offsite.html'
    actual = LocalMathSpider._get_domain_from_uri(uri)
    assert expected == actual
