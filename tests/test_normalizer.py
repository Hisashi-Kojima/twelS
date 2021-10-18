from add_path import add_path
add_path()

from lark import Token

from normalizer.normalizer import Normalizer
from constant.const import Const


def test_normalize_1():
    """0.999を0.9にする"""
    num_token = Token('TOKEN', '0.999')
    expected = Token(Const.token_type, '0.9')
    assert expected == Normalizer.normalize_num(num_token)


def test_normalize_2():
    """0.9999999を0.9にする"""
    num_token = Token('TOKEN', '0.9999999')
    expected = Token(Const.token_type, '0.9')
    assert expected == Normalizer.normalize_num(num_token)


def test_normalize_3():
    """0.33333333333333を0.3にする"""
    num_token = Token('TOKEN', '0.33333333333333')
    expected = Token(Const.token_type, '0.3')
    assert expected == Normalizer.normalize_num(num_token)


def test_normalize_4():
    """0.837の場合はそのまま返す"""
    num_token = Token('TOKEN', '0.837')
    expected = Token(Const.token_type, '0.837')
    assert expected == Normalizer.normalize_num(num_token)


def test_normalize_5():
    """5555の場合は5にする"""
    num_token = Token('TOKEN', '5555')
    expected = Token(Const.token_type, '5')
    assert expected == Normalizer.normalize_num(num_token)
