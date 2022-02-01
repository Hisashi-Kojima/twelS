# -*- coding: utf-8 -*-
"""module description
made by Hisashi
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
    descr = scrapy.Field()
    lang = scrapy.Field()
    exprs = scrapy.Field()  # そのページにあるMathMLすべて
