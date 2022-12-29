# -*- coding: utf-8 -*-
"""module description
"""
import json

from twels.indexer.info import Info


def test_info_1():
    """2ページ登録されている場合。
    """
    data = {
        "lang": ["ja", "en"],
        "uri_id": ["1", "2"],
        "expr_start_pos": [
            [40, 74],
            [200, 310, 440]
        ]
    }
    actual = Info(data)

    expected_lang = 'ja'
    expected_uri_id = '1'
    expected_expr_start_pos = [40, 74]
    assert actual.lang_list[0] == expected_lang
    assert actual.uri_id_list[0] == expected_uri_id
    assert actual.expr_start_pos_list[0] == expected_expr_start_pos


def test_dumps_1():
    """Info.dumps()のテスト。
    """
    data = {
        "uri_id": ["1", "2"],
        "lang": ["ja", "en"],
        "expr_start_pos": [
            [40, 74],
            [200, 310, 440]
        ]
    }
    info = Info(data)
    actual = info.dumps()
    expected = json.dumps(data)
    assert actual == expected
