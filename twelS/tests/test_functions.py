import sys
from pathlib import Path
path = Path(__file__)  # test_functions.pyのpath
sys.path.append(str(path.parent.parent))  # src/twelS

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


def test_get_description_1(response):
    """何を確かめるテストにするのかまだ決めていない．
    """
    actual = functions.get_description(response)

    with open('test_data/方程式 - Wikipedia.html') as f:
        text_list = f.readlines()
        # extract body data
        body_list = text_list[34:811]
    expected = ''.join(body_list)
    assert actual == False 


def test_get_exprs_1(response):
    """何を確かめるテストにするのかまだ決めていない．
    """
    actual = functions.get_exprs(response)
    assert actual == False
