# -*- coding: utf-8 -*-
"""module description
"""

from lark import Token

from twels.normalizer.normalizer import Normalizer
from twels.expr.parser_const import ParserConst


def test_normalize_1():
    """0.999を0.9にする"""
    num_token = Token('TOKEN', '0.999')
    expected = Token(ParserConst.token_type, '0.9')
    assert expected == Normalizer.normalize_num(num_token)


def test_normalize_2():
    """0.9999999を0.9にする"""
    num_token = Token('TOKEN', '0.9999999')
    expected = Token(ParserConst.token_type, '0.9')
    assert expected == Normalizer.normalize_num(num_token)


def test_normalize_3():
    """0.33333333333333を0.3にする"""
    num_token = Token('TOKEN', '0.33333333333333')
    expected = Token(ParserConst.token_type, '0.3')
    assert expected == Normalizer.normalize_num(num_token)


def test_normalize_4():
    """0.837の場合はそのまま返す"""
    num_token = Token('TOKEN', '0.837')
    expected = Token(ParserConst.token_type, '0.837')
    assert expected == Normalizer.normalize_num(num_token)


def test_normalize_5():
    """5555の場合は5にする"""
    num_token = Token('TOKEN', '5555')
    expected = Token(ParserConst.token_type, '5')
    assert expected == Normalizer.normalize_num(num_token)


def test_normalize_subsup_1():
    """<msubsup>を<munderover>に置き換える．"""
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                    <mrow>
                        <msubsup>
                            <mo>&#x02211;</mo>
                            <mrow>
                                <mi>i</mi>
                                <mo>&#x0003D;</mo>
                                <mn>1</mn>
                            </mrow>
                            <mi>n</mi>
                        </msubsup>
                        <msub>
                            <mi>x</mi>
                            <mi>i</mi>
                        </msub>
                    </mrow>
                </math>"""
    actual = Normalizer.normalize_subsup(mathml)
    expected = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                    <mrow>
                        <munderover>
                            <mo>&#x02211;</mo>
                            <mrow>
                                <mi>i</mi>
                                <mo>&#x0003D;</mo>
                                <mn>1</mn>
                            </mrow>
                            <mi>n</mi>
                        </munderover>
                        <msub>
                            <mi>x</mi>
                            <mi>i</mi>
                        </msub>
                    </mrow>
                </math>"""
    assert actual == expected
