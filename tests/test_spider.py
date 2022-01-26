# -*- coding: utf-8 -*-
"""module description
made by Hisashi
"""

import os
import subprocess

from wiki_crawler.wiki_crawler.spiders.local_math_spider import LocalMathSpider


def test_crawl_1():
    """正常にクロールできるか確認．
    このテストがsubprocess.CalledProcessErrorで失敗したとき，
    terminalで'scrapy list'を実行すると，エラーになるだろう．
    クロール時にModuleNotFoundError: No module named 'crawler.settings'が
    出るときにはこのテストは失敗する．
    """
    os.chdir('../wiki_crawler')  # move to scrapy root directory

    command = ['scrapy', 'list']
    subprocess.run(command, check=True)
    assert True


def test_get_domain_from_uri_1():
    """与えたURIからドメインを正しく抽出できているか確認するテスト"""
    expected = 'https://docs.scrapy.org'
    uri = 'https://docs.scrapy.org/en/latest/_modules/scrapy/spidermiddlewares/offsite.html'
    actual = LocalMathSpider._get_domain_from_uri(uri)
    assert expected == actual
