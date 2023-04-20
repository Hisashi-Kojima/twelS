# -*- coding: utf-8 -*-
"""module description
"""
from twels.snippet.snippet import Snippet
from twels.expr.expression import Expression


def test_snippet_str_1():
    """str(Snippet())のテスト。
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline"><mrow><mn>1</mn><mo>+</mo><mn>2</mn></mrow></math>"""
    body = f'ページの説明。{mathml}は数式です。'
    actual = str(Snippet(body))
    cleaned_mathml = """<math><mrow><mn>1</mn><mo>+</mo><mn>2</mn></mrow></math>"""
    expected = f'ページの説明。{cleaned_mathml}は数式です。'
    assert actual == expected


def test_parse_snippet_1():
    """Snippet._parse_snippet()のテスト。
    非数式 + 数式 + 非数式の形。
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline"><mrow><mn>1</mn><mo>+</mo><mn>2</mn></mrow></math>"""
    body = f'ページの説明。{mathml}は数式です。'
    actual = Snippet._parse_snippet(body)
    expr = Expression(mathml)
    expected = ['ページの説明。', expr, 'は数式です。']
    assert actual == expected


def test_parse_snippet_2():
    """Snippet._parse_snippet()のテスト。
    非数式 + 数式 + 非数式 + 数式 + 非数式の形。
    """
    mathml1 = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline"><mrow><mn>1</mn><mo>+</mo><mn>2</mn></mrow></math>"""
    mathml2 = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline"><mrow><mn>3</mn><mo>-</mo><mn>4</mn></mrow></math>"""
    body = f'ページの説明。{mathml1}は数式1です。{mathml2}は数式2です。'
    actual = Snippet._parse_snippet(body)
    expr1 = Expression(mathml1)
    expr2 = Expression(mathml2)
    expected = ['ページの説明。', expr1, 'は数式1です。', expr2, 'は数式2です。']
    assert actual == expected


def test_parse_snippet_3():
    """Snippet._parse_snippet()のテスト。
    数式 + 非数式 + 数式の形。
    """
    mathml1 = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline"><mrow><mn>1</mn><mo>+</mo><mn>2</mn></mrow></math>"""
    mathml2 = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline"><mrow><mn>3</mn><mo>-</mo><mn>4</mn></mrow></math>"""
    body = f'{mathml1}ともう１つの数式{mathml2}'
    actual = Snippet._parse_snippet(body)
    expr1 = Expression(mathml1)
    expr2 = Expression(mathml2)
    expected = [expr1, 'ともう１つの数式', expr2]
    assert actual == expected


def test_parse_snippet_4():
    """Snippet._parse_snippet()のテスト。
    非数式の形。
    """
    body = 'ページの説明。'
    actual = Snippet._parse_snippet(body)
    expected = ['ページの説明。']
    assert actual == expected


def test_search_expr_start_pos_1():
    """Snippet.search_expr_start_pos()のテスト。
    数式に改行や空白が含まれている。
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline"><mrow><mn>1</mn><mo>+</mo><mn>2</mn></mrow></math>"""
    body = f'ページの説明。{mathml}は数式です。'
    snippet = Snippet(body)
    actual_pos = snippet.search_expr_start_pos(Expression(mathml))
    expected_pos = [7]
    assert actual_pos == expected_pos


def test_search_expr_start_pos_2():
    """Snippet.search_expr_start_pos()のテスト。
    複数箇所に対象の数式がある場合。
    """
    mathml = '<math>a</math>'
    body = f'ページの説明。{mathml}は数式です。{mathml}は基本的な式です。'
    snippet = Snippet(body)
    actual_pos = snippet.search_expr_start_pos(Expression(mathml))
    expected_pos = [7, 27]
    assert actual_pos == expected_pos


def test_search_expr_start_pos_3():
    """Snippet.search_expr_start_pos()のテスト。
    数式やbodyに改行や空白が含まれている場合。
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                    <mrow>
                        <mn>1</mn>
                        <mo>+</mo>
                        <mn>2</mn>
                    </mrow>
                </math>"""
    body = f'{mathml}は数式です。'
    snippet = Snippet(body)
    actual_pos = snippet.search_expr_start_pos(Expression(mathml))
    expected_pos = [0]
    assert actual_pos == expected_pos


def test_clean_1():
    """英文のスペースが削除されていないことを確認するテスト。
    """
    text = """The ratio of the circumference of a circle to its diameter."""
    actual = Snippet(text)
    assert actual.text == text


def test_clean_2():
    """英語の文章と数式が正しくcleanできているか確認するテスト。
    """
    text = """The ratio of the circumference of a circle to its diameter.
        <math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
            <mfrac>
                <mi>d</mi>
                <mrow>
                    <mi>d</mi>
                    <mi>x</mi>
                </mrow>
            </mfrac>
        </math>"""
    actual = Snippet(text)

    # 文章中の2つ以上のスペースは1つになる。
    # MathML中のスペースは全て削除される。
    expected = """The ratio of the circumference of a circle to its diameter. <math><mfrac><mi>d</mi><mrow><mi>d</mi><mi>x</mi></mrow></mfrac></math>"""
    assert actual.text == expected
