# -*- coding: utf-8 -*-
"""module description
"""
from twels.indexer.info import Info


def test_info_1():
    """正の数。
    """
    foo = {
        "lang": ["ja"],
        "uri_id": ["1"],
        "area": [
            [[40, 54], [200, 214]]
        ]
    }
    actual = Info(foo)

    expected_lang = 'ja'
    expected_uri_id = '1'
    expected_area = [40, 54]
    assert actual.lang_list[0] == expected_lang
    assert actual.uri_id_list[0] == expected_uri_id
    assert actual.area_list[0][0] == expected_area
