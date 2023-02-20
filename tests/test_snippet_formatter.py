# -*- coding: utf-8 -*-
"""module description
"""

from twels.snippet.formatter import Formatter
from twels.snippet.snippet import Snippet


def test_format_1():
    """Formatter.format()のテスト．
    ハイライトのタグが挿入されていることを確認。
    """
    # 2*5
    expr = """
    <math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
        <mrow>
            <mn>2</mn>
            <mo>&#x0002A;</mo>
            <mn>5</mn>
        </mrow>
    </math>
    """
    cleaned_expr = Snippet.clean(expr)

    body = f"""数式{cleaned_expr}は、乗算と呼ばれています。"""
    snippet = Snippet(body)
    expr_start_pos = [2]
    expr_len = len(cleaned_expr)

    actual = Formatter.format(snippet, expr_start_pos, expr_len)
    expected = f"""数式<span class="hl">{cleaned_expr}</span>は、乗算と呼ばれています。"""
    assert expected == actual
