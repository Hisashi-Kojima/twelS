# -*- coding: utf-8 -*-
"""module description
"""
from twels.expr.expression import Expression
from twels.snippet.formatter import Formatter
from twels.snippet.snippet import Snippet


def test_format_1():
    """Formatter.format()のテスト．
    ハイライトのタグが挿入されていることを確認。
    """
    # 2*5
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                    <mrow>
                        <mn>2</mn>
                        <mo>&#x0002A;</mo>
                        <mn>5</mn>
                    </mrow>
                </math>"""
    expr = Expression(mathml)

    body = f'数式{expr.mathml}は、乗算と呼ばれています。'
    snippet = Snippet(body)
    expr_start_pos = [2]
    expr_len = len(expr.mathml)

    actual = Formatter.format(snippet, expr_start_pos, expr_len)
    expected = f'数式<span class="hl">{expr.mathml}</span>は、乗算と呼ばれています。'
    assert expected == actual
