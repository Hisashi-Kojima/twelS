# -*- coding: utf-8 -*-
"""module description
"""

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# Typical uses of item pipelines are:
# 1. cleansing HTML data
# 2. validating scraped data (checking that the items contain certain fields)
# 3. checking for duplicates (and dropping them)
# 4. storing the scraped item in a database



# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

from scrapy.http import Request
from scrapy.pipelines.files import FilesPipeline
from scrapy.spiders import Spider

from twels.indexer.indexer import Indexer


class DownloadPipeline(FilesPipeline):
    """
    source code of FilesPipeline: https://github.com/scrapy/scrapy/blob/master/scrapy/pipelines/files.py
    """
    def file_path(self, request: Request, response=None, info=None, *, item):
        title = item['title']
        return f'{title}.html'


class DownloadKatexPipeline(object):
    """KaTeXで書かれたページをダウンロードする関数。
    """
    def process_item(self, item, spider: Spider):
        title = item['title']
        filename = f'web_pages/manabitimes/{title}.html'
        with open(filename, 'w') as f:
            f.write(item['snippet'])
        return item


class WebCrawlerPipeline:
    def process_item(self, item, spider: Spider):
        """数式をデータベースに登録する関数．
        """
        Indexer.update_db(ItemAdapter(item))
        return item


class TestCrawlerPipeline:
    """Crawlerの動作確認のためのPipeline。"""
    def process_item(self, item, spider: Spider):
        Indexer.update_db(ItemAdapter(item), test=True)
        return item
