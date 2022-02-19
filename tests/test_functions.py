# -*- coding: utf-8 -*-
"""module description
"""

import pytest
from scrapy.http.response.html import HtmlResponse

from wiki_crawler.wiki_crawler.spiders import functions


@pytest.fixture
def response():
    with open('test_data/方程式 - Wikipedia.html') as f:
        body = f.read().encode()
    return HtmlResponse(url='local', body=body)


# tests

def test_get_lang_1(response):
    actual = functions.get_lang(response)
    expected = 'ja'
    assert actual == expected


def test_get_title_1(response):
    actual = functions.get_title(response)
    expected = '方程式 - Wikipedia'
    assert actual == expected
