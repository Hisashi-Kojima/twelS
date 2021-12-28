# -*- coding: utf-8 -*-
"""module description
made by Hisashi
"""

from twels.search.searcher.searcher import Searcher


def test_search_1():
    """不正な数式のときには空の結果を返す．
    """
    result_dict = Searcher.search("a^'")
    expected = {
        'search_result': [],
        'result_num': 0
        }
    assert result_dict == expected
