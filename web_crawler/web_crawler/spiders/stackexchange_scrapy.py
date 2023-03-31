# -*- coding: utf-8 -*-
"""module description
"""

import time
import scrapy
from scrapy.http import TextResponse
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


from ..items import DownloadItem


# Read the entire file as a list
def _load_script(path: str) -> str:
    script = 'scriptが読み込まれていません．'
    with open(path) as f:
        script = f.readlines()
    return script

class StackExchangeSpider(scrapy.Spider):
    # type 'scrapy crawl stackexchange' to crawl.
    name = 'stackexchange'
    allowed_domains = [
        'math.stackexchange.com',
    ]

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
    }

    count = 0
    category_urls = _load_script('web_crawler/spiders/stackexchange_urls.txt')
    start_urls = category_urls

    def parse(self, response):
        # 50ページをダウンロード
        for css in response.css('h3.s-post-summary--content-title a'):
            download_page = response.urljoin(css.attrib['href'])
            yield scrapy.Request(url=download_page, callback=self._download)

    def _download(self, response):
        """ページをダウンロードする関数"""
        time.sleep(3)  # 3秒のDOWNLOAD_DELAY
        title = response.css('title::text').get()
        title = title.replace('/', '÷')  # avoid FileNotFoundError because of '/'
        filename = f'web_pages/stackexchange/{title}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)

