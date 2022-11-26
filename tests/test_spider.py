# -*- coding: utf-8 -*-
"""module description
"""

import os
import subprocess

from web_crawler.web_crawler.spiders.local_spider import LocalSpider


def test_crawl_1():
    """正常にクロールできるか確認．
    このテストがsubprocess.CalledProcessErrorで失敗したとき，
    terminalで'scrapy list'を実行すると，エラーになるだろう．
    クロール時にModuleNotFoundError: No module named 'crawler.settings'が
    出るときにはこのテストは失敗する．
    """
    # move to scrapy root directory.
    # use os.path.join() because Windows use '\' and Linux use '/'.
    os.chdir(os.path.join(os.path.dirname(__file__), '..', 'web_crawler'))

    command = ['scrapy', 'list']
    subprocess.run(command, check=True)
    assert True


def test_get_domain_from_uri_1():
    """与えたURIからドメインを正しく抽出できているか確認するテスト"""
    expected = 'https://docs.scrapy.org'
    uri = 'https://docs.scrapy.org/en/latest/_modules/scrapy/spidermiddlewares/offsite.html'
    actual = LocalSpider._get_domain_from_uri(uri)
    assert expected == actual
