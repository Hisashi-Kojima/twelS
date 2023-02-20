# -*- coding: utf-8 -*-
"""module description
"""

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Page(scrapy.Item):
    # define the fields for your item here like:
    uri = scrapy.Field()
    title = scrapy.Field()
    snippet = scrapy.Field()
    lang = scrapy.Field()
    exprs = scrapy.Field()  # そのページにあるMathMLすべて


class DownloadItem(scrapy.Item):
    title = scrapy.Field()
    file_urls = scrapy.Field()
    files = scrapy.Field()


class DownloadKatexItem(scrapy.Item):
    title = scrapy.Field()
    snippet = scrapy.Field()
