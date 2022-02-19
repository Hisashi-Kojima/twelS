# -*- coding: utf-8 -*-
"""module description
"""

import time

import scrapy


class WikiSpider(scrapy.Spider):
    """Wikipediaの物理学のページをダウンロードするためのクラス．
    """
    # type 'scrapy crawl wiki_physics' to crawl.
    name = 'wiki_physics'

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
    }

    count = 0
    start_urls = [
        # 物理学に関する記事の一覧
        'https://ja.wikipedia.org/wiki/%E7%89%A9%E7%90%86%E5%AD%A6%E3%81%AB%E9%96%A2%E3%81%99%E3%82%8B%E8%A8%98%E4%BA%8B%E3%81%AE%E4%B8%80%E8%A6%A7',
    ]

    def parse(self, response):
        # 物理学の各記事をダウンロード
        for css in response.css('p a'):
            download_page = response.urljoin(css.attrib['href'])
            yield scrapy.Request(url=download_page, callback=self._download)

    def _download(self, response):
        """ページをダウンロードする関数"""
        time.sleep(3)  # 3秒のDOWNLOAD_DELAY
        title = response.css('title::text').get()
        title = title.replace('/', '÷')  # avoid FileNotFoundError because of '/'
        filename = f'wiki_pages/physics/{title}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
