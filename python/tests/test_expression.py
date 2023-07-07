# -*- coding: utf-8 -*-
"""module description
"""
import latex2mathml.converter
import pytest

from twels.expr.expression import Expression


def test_expression_1():
    """Expression()のテスト。
    frac{d}{dx}
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                    <mfrac>
                        <mi>d</mi>
                        <mrow>
                            <mi>d</mi>
                            <mi>x</mi>
                        </mrow>
                    </mfrac>
                </math>"""
    actual = Expression(mathml)
    expected = '<math><mfrac><mi>d</mi><mrow><mi>d</mi><mi>x</mi></mrow></mfrac></math>'
    assert actual.mathml == expected


def test_expression_2():
    """Expression()のテスト。
    semantics, mstyle, annotationを含む。
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML"  alttext="{\displaystyle {\frac {d}{dx}}e^{x}=e^{x},}">
                    <semantics>
                        <mrow class="MJX-TeXAtom-ORD">
                        <mstyle displaystyle="true" scriptlevel="0">
                            <mrow class="MJX-TeXAtom-ORD">
                                <mfrac>
                                    <mi>d</mi>
                                    <mrow>
                                        <mi>d</mi>
                                        <mi>x</mi>
                                    </mrow>
                                </mfrac>
                            </mrow>
                            <msup>
                                <mi>e</mi>
                                <mrow class="MJX-TeXAtom-ORD">
                                    <mi>x</mi>
                                </mrow>
                            </msup>
                            <mo>=</mo>
                            <msup>
                                <mi>e</mi>
                                <mrow class="MJX-TeXAtom-ORD">
                                    <mi>x</mi>
                                </mrow>
                            </msup>
                            <mo>,</mo>
                        </mstyle>
                        </mrow>
                        <annotation encoding="application/x-tex">{\displaystyle {\frac {d}{dx}}e^{x}=e^{x},}</annotation>
                    </semantics>
                </math>"""
    actual = Expression(mathml)
    expected = """<math><mrow><mrow><mfrac><mi>d</mi><mrow><mi>d</mi><mi>x</mi></mrow></mfrac></mrow><msup><mi>e</mi><mrow><mi>x</mi></mrow></msup><mo>=</mo><msup><mi>e</mi><mrow><mi>x</mi></mrow></msup><mo>,</mo></mrow></math>"""
    assert actual.mathml == expected


def test_expression_3():
    """Expression()のテスト。
    コメント、スペースを含む。
    """
    mathml = """<math>
                    <mover accent="true">
                        <mrow>
                            <mi> x </mi>
                            <mo> + </mo>
                            <mi> y </mi>
                            <mo> + </mo>
                            <mi> z </mi>
                        </mrow>
                        <mo> &#x23DE; <!--TOP CURLY BRACKET--> </mo>
                    </mover>
                </math>"""
    actual = Expression(mathml)
    expected = """<math><mover><mrow><mi>x</mi><mo>+</mo><mi>y</mi><mo>+</mo><mi>z</mi></mrow><mo>⏞</mo></mover></math>"""
    assert actual.mathml == expected


def test_expression_4():
    """Expression()のテスト。
    a < b
    """
    actual = Expression(latex2mathml.converter.convert('a < b'))
    expected = """<math><mrow><mi>a</mi><mo>&lt;</mo><mi>b</mi></mrow></math>"""
    assert actual.mathml == expected


def test_invalid_expression_1():
    """Expression()のテスト。
    無効な形式。
    """
    invalid_mathml = """<math><mi>x</mi><mo>+</mo><mi>y</mi>"""
    with pytest.raises(ValueError) as e:
        Expression(invalid_mathml)

    assert 'invalid MathML syntax' in str(e.value)


def test_invalid_expression_2():
    """Expression()のテスト。
    違う型の値。
    """
    invalid_mathml = [1, 2]
    with pytest.raises(TypeError) as e:
        Expression(invalid_mathml)

    assert 'Expression does not support' in str(e.value)


def test_expression_is_hashable_1():
    """Expression()のテスト。
    """
    mathml1 = """<math>1</math>"""
    mathml2 = """<math>2</math>"""

    expr1 = Expression(mathml1)
    expr2 = Expression(mathml2)
    expr3 = Expression(mathml1)

    exprs = [expr1, expr2, expr3]
    actual = set(exprs)
    expected = {expr1, expr2}
    assert actual == expected
