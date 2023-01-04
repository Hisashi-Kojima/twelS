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


def test_info_2():
    """infoを修正しても元データに影響がないことを確認。
    """
    data = {
        "lang": ["ja", "en"],
        "uri_id": ["1", "2"],
        "expr_start_pos": [
            [40, 74],
            [200, 310, 440]
        ]
    }
    info = Info(data)
    info.uri_id_list[0] = "100"
    assert data == {
        "lang": ["ja", "en"],
        "uri_id": ["1", "2"],
        "expr_start_pos": [
            [40, 74],
            [200, 310, 440]
        ]
    }


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


def test_extract_1():
    """Info.extract()のテスト。
    全部を指定する場合。
    """
    data = {
        "uri_id": ["1", "2", "3", "4"],
        "lang": ["ja", "en", "ja", "ja"],
        "expr_start_pos": [
            [40, 74],
            [200, 310, 440],
            [9],
            [222, 333, 444, 777]
        ]
    }
    info = Info(data)
    info_size = info.size()
    assert info_size == 4
    actual = info.extract(0, info_size)
    expected = info
    assert str(actual) == str(expected)
    # 元のデータが変わっていないことを確認
    assert str(info) == str(Info(data))


def test_extract_2():
    """Info.extract()のテスト。
    途中を指定する場合。
    """
    data = {
        "uri_id": ["1", "2", "3", "4"],
        "lang": ["ja", "en", "ja", "ja"],
        "expr_start_pos": [
            [40, 74],
            [200, 310, 440],
            [9],
            [222, 333, 444, 777]
        ]
    }
    info = Info(data)
    actual = info.extract(1, 3)

    expected = Info({
        "uri_id": ["2", "3"],
        "lang": ["en", "ja"],
        "expr_start_pos": [
            [200, 310, 440],
            [9],
        ]
    })
    assert str(actual) == str(expected)


def test_extract_3():
    """Info.extract()のテスト。
    開始位置が無効の場合。
    """
    data = {
        "uri_id": ["1", "2", "3", "4"],
        "lang": ["ja", "en", "ja", "ja"],
        "expr_start_pos": [
            [40, 74],
            [200, 310, 440],
            [9],
            [222, 333, 444, 777]
        ]
    }
    info = Info(data)
    actual = info.extract(10, 3)
    assert actual.is_empty()


def test_extract_4():
    """Info.extract()のテスト。
    終了位置がinfo.size()を超えている場合。
    """
    data = {
        "uri_id": ["1", "2", "3", "4"],
        "lang": ["ja", "en", "ja", "ja"],
        "expr_start_pos": [
            [40, 74],
            [200, 310, 440],
            [9],
            [222, 333, 444, 777]
        ]
    }
    info = Info(data)
    actual = info.extract(1, 10)
    expected = Info({
        "uri_id": ["2", "3", "4"],
        "lang": ["en", "ja", "ja"],
        "expr_start_pos": [
            [200, 310, 440],
            [9],
            [222, 333, 444, 777]
        ]
    })
    assert str(actual) == str(expected)


def test_extract_5():
    """Info.extract()のテスト。
    開始位置が有効で、かつ終了位置が開始位置よりも小さい場合。
    """
    data = {
        "uri_id": ["1", "2", "3", "4", "5", "6", "7"],
        "lang": ["ja", "en", "ja", "ja", "en", "ja", "en"],
        "expr_start_pos": [
            [40, 74],
            [200, 310, 440],
            [9],
            [222, 333, 444, 777],
            [1],
            [73, 100],
            [55, 149]
        ]
    }
    info = Info(data)
    actual = info.extract(2, 1)
    assert actual.is_empty()


def test_extract_6():
    """Info.extract()のテスト。
    終了位置を省略した場合。
    """
    data = {
        "uri_id": ["1", "2", "3", "4"],
        "lang": ["ja", "en", "ja", "ja"],
        "expr_start_pos": [
            [40, 74],
            [200, 310, 440],
            [9],
            [222, 333, 444, 777]
        ]
    }
    info = Info(data)
    actual = info.extract(1)
    expected = Info({
        "uri_id": ["2", "3", "4"],
        "lang": ["en", "ja", "ja"],
        "expr_start_pos": [
            [200, 310, 440],
            [9],
            [222, 333, 444, 777]
        ]
    })
    assert str(actual) == str(expected)


def test_merge_1():
    """Info.merge()のテスト。
    """
    data1 = {
        "uri_id": ["1", "2", "3", "4"],
        "lang": ["ja", "en", "ja", "ja"],
        "expr_start_pos": [
            [40, 74],
            [200, 310, 440],
            [9],
            [222, 333, 444, 777]
        ]
    }
    info1 = Info(data1)

    data2 = {
        "uri_id": ["5", "6", "7"],
        "lang": ["en", "ja", "en"],
        "expr_start_pos": [
            [1],
            [73, 100],
            [55, 149]
        ]
    }
    info2 = Info(data2)

    actual_info = info1.merge(info2)

    expected_info = Info({
        "uri_id": ["1", "2", "3", "4", "5", "6", "7"],
        "lang": ["ja", "en", "ja", "ja", "en", "ja", "en"],
        "expr_start_pos": [
            [40, 74],
            [200, 310, 440],
            [9],
            [222, 333, 444, 777],
            [1],
            [73, 100],
            [55, 149]
        ]
    })
    assert str(actual_info) == str(expected_info)
    # 元データが変わっていないことを確認
    assert str(info1) == str(Info(data1))
    assert str(info2) == str(Info(data2))
