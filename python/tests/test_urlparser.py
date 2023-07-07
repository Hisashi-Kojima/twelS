# -*- coding: utf-8 -*-
"""module description
"""
from twels.searcher.urlparser import parse_url


def test_parse_url_1():
    """URLがqとlrだけを含むとき。
    """
    query = 'q=a&lr=ja'
    expected = {
        'q': ['a'],
        'start': ['0'],
        'lr': ['ja']
    }
    actual = parse_url(query)
    assert actual == expected


def test_parse_url_2():
    """a+bを日本語と英語で調べたとき。
    """
    query = 'q=a%2Bb&lr=ja&lr=en'
    expected = {
        'q': ['a+b'],
        'start': ['0'],
        'lr': ['ja', 'en']
    }
    actual = parse_url(query)
    assert actual == expected


def test_parse_url_3():
    """axを英語で調べたとき。
    """
    query = 'q=a%20x&lr=en'
    expected = {
        'q': ['a x'],
        'start': ['0'],
        'lr': ['en']
    }
    actual = parse_url(query)
    assert actual == expected


def test_parse_url_4():
    """URLがqとlr、startを含むとき。
    """
    query = 'q=a&start=10&lr=ja'
    expected = {
        'q': ['a'],
        'start': ['10'],
        'lr': ['ja']
    }
    actual = parse_url(query)
    assert actual == expected


def test_parse_url_5():
    """クエリが2つあるとき。
    """
    query = 'q=a+b&lr=ja'
    expected = {
        'q': ['a', 'b'],
        'start': ['0'],
        'lr': ['ja']
    }
    actual = parse_url(query)
    assert actual == expected


def test_parse_url_6():
    """クエリが2つあり、式中にスペースがあるとき。
    """
    query = 'q=a%20x%5E2+b%20y&lr=ja'
    expected = {
        'q': ['a x^2', 'b y'],
        'start': ['0'],
        'lr': ['ja']
    }
    actual = parse_url(query)
    assert actual == expected


def test_parse_url_7():
    """クエリが空のとき。
    """
    query = ''
    expected = {
        'q': [],
        'start': ['0'],
        'lr': []
    }
    actual = parse_url(query)
    assert actual == expected
