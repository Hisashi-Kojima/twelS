# -*- coding: utf-8 -*-
"""this file has tests for functions not implemented.
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

def test_get_snippet_1(response):
    """何を確かめるテストにするのかまだ決めていない．
    """
    actual = functions.get_snippet(response)

    with open('test_data/方程式 - Wikipedia.html') as f:
        text_list = f.readlines()
        # extract body data
        body_list = text_list[34:811]
    expected = ''.join(body_list)
    # TODO: 修正
    assert actual == False
