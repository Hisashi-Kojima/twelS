# -*- coding: utf-8 -*-
"""module description
"""
from twels.snippet.snippet import Snippet


def test_search_expr_start_pos_1():
    """Snippet.search_expr_start_pos()のテスト。
    数式に改行や空白が含まれている。
    """
    mathml = """
        <math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
            <mrow>
                <mn>1</mn>
                <mo>+</mo>
                <mn>2</mn>
            </mrow>
        </math>
        """
    body = f'ページの説明。{mathml}は数式です。'
    snippet = Snippet(body)
    cleaned_mathml = Snippet.remove_spaces(mathml)
    actual_pos = snippet.search_expr_start_pos(cleaned_mathml)
    expected_pos = [7]
    assert actual_pos == expected_pos


def test_search_expr_start_pos_2():
    """Snippet.search_expr_start_pos()のテスト。
    複数箇所に対象の数式がある場合。
    """
    mathml = '<math>a</math>'
    body = f'ページの説明。{mathml}は数式です。{mathml}は基本的な式です。'
    snippet = Snippet(body)
    cleaned_mathml = Snippet.remove_spaces(mathml)
    actual_pos = snippet.search_expr_start_pos(cleaned_mathml)
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
    body = """
        <math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
            <mrow>
                <mn>1</mn>
                <mo>+</mo>
                <mn>2</mn>
            </mrow>
        </math>は数式です。
        """
    snippet = Snippet(body)
    cleaned_mathml = Snippet.remove_spaces(mathml)
    actual_pos = snippet.search_expr_start_pos(cleaned_mathml)
    expected_pos = [0]
    assert actual_pos == expected_pos


def test_remove_spaces_1():
    """Snippet.remove_spaces()のテスト。
    """
    text = '<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">1</math>'
    actual = Snippet.remove_spaces(text)
    assert actual == '<math>1</math>'


def test_remove_spaces_2():
    """Snippet.remove_spaces()のテスト。
    """
    text = """
        <math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
            <mrow>
                <mn>1</mn>
                <mo>+</mo>
                <mn>2</mn>
            </mrow>
        </math>
        """
    actual = Snippet.remove_spaces(text)
    expected = '<math><mrow><mn>1</mn><mo>+</mo><mn>2</mn></mrow></math>'
    assert actual == expected
