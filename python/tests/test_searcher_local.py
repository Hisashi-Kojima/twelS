# -*- coding: utf-8 -*-
"""this file has tests for Searcher not implemented.
"""

import pytest

from twels.searcher.searcher import Searcher


@pytest.mark.parametrize('test_input, expected', [
    ('well-being', False),
    ('K8s', False),
    ('he/she', False)
])
def test_is_expr_1(test_input, expected):
    """入力が数式かどうかを判別する関数のテスト。"""
    assert Searcher._is_expr(test_input) == expected
