# -*- coding: utf-8 -*-
"""test modules of functions.py.
"""

import pytest
from scrapy.http.response.html import HtmlResponse

from web_crawler.web_crawler.spiders import functions


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


def test_render_katex_1():
    """KaTeXで書かれた数式がMathMLに変換されているか確認するテスト。
    """
    expr_katex = 'a+b'
    actual = functions.render_katex(expr_katex)
    assert '<math' in actual


def test_render_katex_2():
    """変換後の数式がきれいなMathMLになっているか確認するテスト。
    """
    expr_katex = 'a-b'
    actual = functions.render_katex(expr_katex)
    assert actual[:5] == '<math'
