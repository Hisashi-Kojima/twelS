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

from twels.indexer.indexer import Indexer


class DownloadPipeline(FilesPipeline):
    """
    source code of FilesPipeline: https://github.com/scrapy/scrapy/blob/master/scrapy/pipelines/files.py
    """
    def file_path(self, request: Request, response=None, info=None, *, item):
        title = item['title']
        return f'{title}.html'


class WebCrawlerPipeline:
    def process_item(self, item, spider):
        """数式をデータベースに登録する関数．
        """
        Indexer.update_db(ItemAdapter(item))
        return item
