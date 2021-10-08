# -*- coding: utf-8 -*-
"""module description
made by Hisashi
"""

import scrapy


class WikiSpider(scrapy.Spider):
    # type 'scrapy crawl wiki' to crawl.
    name = 'wiki'

    custom_settings = {
        'ROBOTSTXT_OBEY': False,
    }

    count = 0
    start_urls = [
        # 1 数学
        'https://ja.wikipedia.org/wiki/Category:%E6%95%B0%E5%AD%A6%E3%81%AB%E9%96%A2%E3%81%99%E3%82%8B%E8%A8%98%E4%BA%8B',
    ]


    def parse(self, response):
        # そのページをダウンロード
        MathSpider.count += 1
        filename = f'wiki_pages/page_{MathSpider.count}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)

        # 200ページをダウンロード
        for css in response.css('div.mw-category-group ul li a'):
            download_page = response.urljoin(css.attrib['href'])
            yield scrapy.Request(url=download_page, callback=self._download)
        
        # 次のページへ移動
        next_page = response.xpath('//div[@id="mw-pages"]/a[text()="次のページ"]/@href').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)[:-9]  # remove last 9 characters("#mw-pages")
            print('next_page:', next_page)
            yield scrapy.Request(url=next_page, callback=self.parse)
        else:
            print('next_page: None!')
        

    def _download(self, response):
        """ページをダウンロードする関数"""
        title = response.css('title::text').get()
        title = title.replace('/', '÷')  # avoid FileNotFoundError because of '/'
        filename = f'wiki_pages/{title}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
