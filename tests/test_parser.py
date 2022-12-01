# -*- coding: utf-8 -*-
"""module description
"""

import latex2mathml.converter
from lark import Tree, Token

from twels.expr.parser import Parser
from twels.expr.parser_const import ParserConst


def test_get_parsed_tree_add_1():
    """加算のparse
    1+2
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                    <mrow>
                        <mn>1</mn>
                        <mo>&#x0002B;</mo>
                        <mn>2</mn>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.sum_data, [
            Token(ParserConst.token_type, '1'), Token(ParserConst.token_type, '2')
            ])
        ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_add_2():
    """加算のparse
    1+2+a
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                    <mrow>
                        <mn>1</mn>
                        <mo>&#x0002B;</mo>
                        <mn>2</mn>
                        <mo>&#x0002B;</mo>
                        <mi>a</mi>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.sum_data, [
            Token(ParserConst.token_type, '1'), Token(ParserConst.token_type, '2'), Token(ParserConst.token_type, 'a')
            ])
        ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_add_3():
    """加算のparse
    +7
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                    <mrow>
                        <mo>&#x0002B;</mo>
                        <mn>7</mn>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Token(ParserConst.token_type, '7')
    ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_subtract_1():
    """減算のparse
    3-2
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                    <mrow>
                        <mn>3</mn>
                        <mo>&#x02212;</mo>
                        <mn>2</mn>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.sum_data, [
            Token(ParserConst.token_type, '3'), Tree(ParserConst.neg_data, [Token(ParserConst.token_type, '2')])
            ])
        ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_subtract_2():
    """減算のparse
    -5
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                    <mrow>
                        <mo>&#x02212;</mo>
                        <mn>5</mn>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.neg_data, [Token(ParserConst.token_type, '5')])
    ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_mul_1():
    """乗算のparse
    2*5
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                    <mrow>
                        <mn>2</mn>
                        <mo>&#x0002A;</mo>
                        <mn>5</mn>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.product_data, [
            Token(ParserConst.token_type, '2'), Token(ParserConst.token_type, '5')
            ])
        ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_mul_2():
    """乗算のparse
    abc
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                    <mrow>
                        <mi>a</mi>
                        <mi>b</mi>
                        <mi>c</mi>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.product_data, [
            Token(ParserConst.token_type, 'a'), Token(ParserConst.token_type, 'b'), Token(ParserConst.token_type, 'c')
            ])
        ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_frac_1():
    """分数のparse
    frac{2}{3}
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                    <mrow>
                        <mfrac>
                            <mrow>
                                <mn>2</mn>
                            </mrow>
                            <mrow>
                                <mn>3</mn>
                            </mrow>
                        </mfrac>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.frac_data, [
            Tree('#0', [Token(ParserConst.token_type, '2')]),
            Tree('#1', [Token(ParserConst.token_type, '3')])
        ])
    ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_frac_2():
    """分数のparse
    frac{d}{dx}e^{x}
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML"  alttext="{\displaystyle {\frac {d}{dx}}e^{x}=e^{x},}">
                    <mrow class="MJX-TeXAtom-ORD">
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
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.product_data, [
            Tree(ParserConst.frac_data, [
                Tree('#0', [Token(ParserConst.token_type, 'd')]),
                Tree('#1', [
                    Tree(ParserConst.product_data, [
                        Token(ParserConst.token_type, 'd'),
                        Token(ParserConst.token_type, 'x')
                    ])
                ])
            ]),
            Tree(ParserConst.sup_data, [
                Tree('#0', [Token(ParserConst.token_type, 'e')]),
                Tree('#1', [Token(ParserConst.token_type, 'x')])
            ])
        ])
    ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_frac_3():
    """分数のparse
    frac{d}{dx}e^{x}=e^{x}
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
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.product_data, [
            Tree(ParserConst.frac_data, [
                Tree('#0', [Token(ParserConst.token_type, 'd')]),
                Tree('#1', [
                    Tree(ParserConst.product_data, [
                        Token(ParserConst.token_type, 'd'),
                        Token(ParserConst.token_type, 'x')
                    ])
                ])
            ]),
            Tree(ParserConst.sup_data, [
                Tree('#0', [Token(ParserConst.token_type, 'e')]),
                Tree('#1', [Token(ParserConst.token_type, 'x')])
            ])
        ]),
        Tree(ParserConst.equal_data, []),
        Tree(ParserConst.product_data, [
            Tree(ParserConst.sup_data, [
                Tree('#0', [Token(ParserConst.token_type, 'e')]),
                Tree('#1', [Token(ParserConst.token_type, 'x')])
            ]),
            # TODO: 式の最後にある','は無視するように修正
            Token(ParserConst.token_type, ',')
        ])
    ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_frac_4():
    """
    分数の入れ子。frac {frac{a}{b}}{frac{c}{d}}
    参考ページ：分数
    https://ja.wikipedia.org/wiki/%E5%88%86%E6%95%B0
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML"  alttext="{\displaystyle {\frac {\;{\dfrac {a}{b}}\;}{\;{\dfrac {c}{d}}\;}}}">
                    <semantics>
                        <mrow class="MJX-TeXAtom-ORD">
                        <mstyle displaystyle="true" scriptlevel="0">
                            <mrow class="MJX-TeXAtom-ORD">
                            <mfrac>
                                <mrow>
                                <mrow class="MJX-TeXAtom-ORD">
                                    <mstyle displaystyle="true" scriptlevel="0">
                                    <mfrac>
                                        <mi>a</mi>
                                        <mi>b</mi>
                                    </mfrac>
                                    </mstyle>
                                </mrow>
                                </mrow>
                                <mrow>
                                <mrow class="MJX-TeXAtom-ORD">
                                    <mstyle displaystyle="true" scriptlevel="0">
                                    <mfrac>
                                        <mi>c</mi>
                                        <mi>d</mi>
                                    </mfrac>
                                    </mstyle>
                                </mrow>
                                </mrow>
                            </mfrac>
                            </mrow>
                        </mstyle>
                        </mrow>
                        <annotation encoding="application/x-tex">{\displaystyle {\frac {\;{\dfrac {a}{b}}\;}{\;{\dfrac {c}{d}}\;}}}</annotation>
                    </semantics>
                </math>"""

    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.frac_data, [
            Tree('#0', [
                Tree(ParserConst.frac_data, [
                    Tree('#0', [
                        Token(ParserConst.token_type, 'a')
                    ]),
                    Tree('#1', [
                        Token(ParserConst.token_type, 'b')
                    ])
                ])
            ]),
            Tree('#1', [
                Tree(ParserConst.frac_data, [
                    Tree('#0', [
                        Token(ParserConst.token_type, 'c')
                    ]),
                    Tree('#1', [
                        Token(ParserConst.token_type, 'd')
                    ])
                ])
            ]),
        ])
    ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_div_1():
    """除算のparse
    3/4
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                    <mrow>
                        <mn>3</mn>
                        <mo>&#x0002F;</mo>
                        <mn>4</mn>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.product_data, [
            Token(ParserConst.token_type, '3'), Tree(ParserConst.frac_data, [
                Tree('#0', [Token(ParserConst.token_type, '1')]),
                Tree('#1', [Token(ParserConst.token_type, '4')])
            ])
        ])
    ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_eq_1():
    """等号を含む式のparse
    y=ax
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                    <mrow>
                        <mi>y</mi>
                        <mo>&#x0003D;</mo>
                        <mi>a</mi>
                        <mi>x</mi>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Token(ParserConst.token_type, 'y'),
        Tree(ParserConst.equal_data, []),
        Tree(ParserConst.product_data, [
            Token(ParserConst.token_type, 'a'), Token(ParserConst.token_type, 'x')
            ])
        ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_eq_2():
    """等号を2つ含む式のparse
    a=b=c
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                    <mrow>
                        <mi>a</mi>
                        <mo>&#x0003D;</mo>
                        <mi>b</mi>
                        <mo>&#x0003D;</mo>
                        <mi>c</mi>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Token(ParserConst.token_type, 'a'),
        Tree(ParserConst.equal_data, []),
        Token(ParserConst.token_type, 'b'),
        Tree(ParserConst.equal_data, []),
        Token(ParserConst.token_type, 'c')
    ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_paren_1():
    """かっこを含む式のparse
    3*(4+5)
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                    <mrow>
                        <mn>3</mn>
                        <mo>&#x0002A;</mo>
                        <mo stretchy="false">&#x00028;</mo>
                        <mn>4</mn>
                        <mo>&#x0002B;</mo>
                        <mn>5</mn>
                        <mo stretchy="false">&#x00029;</mo>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.product_data, [
            Token(ParserConst.token_type, '3'), Tree(ParserConst.paren_data, [
                Tree(ParserConst.sum_data, [
                    Token(ParserConst.token_type, '4'), Token(ParserConst.token_type, '5')
                ])
            ])
        ])
    ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_sup_1():
    """上付き文字のparse
    e^{x}
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                    <mrow>
                        <msup>
                            <mi>e</mi>
                            <mrow>
                                <mi>x</mi>
                            </mrow>
                        </msup>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.sup_data, [
            Tree('#0', [Token(ParserConst.token_type, 'e')]),
            Tree('#1', [Token(ParserConst.token_type, 'x')])
        ])
    ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_sub_1():
    """下付き文字のparse
    x_{i}
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                    <mrow>
                        <msub>
                            <mi>x</mi>
                            <mrow>
                                <mi>i</mi>
                            </mrow>
                        </msub>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.sub_data, [
            Tree('#0', [Token(ParserConst.token_type, 'x')]),
            Tree('#1', [Token(ParserConst.token_type, 'i')])
        ])
    ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_subsup_1():
    """下付き上付き文字のparse
    x_{i}^{2}
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                    <mrow>
                        <msubsup>
                            <mi>x</mi>
                            <mrow>
                                <mi>i</mi>
                            </mrow>
                            <mrow>
                                <mn>2</mn>
                            </mrow>
                        </msubsup>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.subsup_data, [
            Tree('#0', [Token(ParserConst.token_type, 'x')]),
            Tree('#1', [Token(ParserConst.token_type, 'i')]),
            Tree('#2', [Token(ParserConst.token_type, '2')])
        ])
    ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_sqrt_1():
    """平方根のparse
    sqrt{3}
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                    <mrow>
                        <msqrt>
                            <mrow>
                                <mn>3</mn>
                            </mrow>
                        </msqrt>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.sqrt_data, [
            Token(ParserConst.token_type, '3')
        ])
    ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_root_1():
    """n乗根のparse
    sqrt[3]{5}
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                    <mrow>
                        <mroot>
                            <mrow>
                                <mn>5</mn>
                            </mrow>
                            <mrow>
                                <mn>3</mn>
                            </mrow>
                        </mroot>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.func_root_data, [
            Tree('#0', [Token(ParserConst.token_type, '5')]),
            Tree('#1', [Token(ParserConst.token_type, '3')])
        ])
    ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_over_1():
    """上にアクセントがある式のparse
    bar{x+y+z}
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
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.over_data, [
            Tree('#0', [
                Tree(ParserConst.sum_data, [
                    Token(ParserConst.token_type, 'x'), Token(ParserConst.token_type, 'y'), Token(ParserConst.token_type, 'z')
                ])
            ]),
            Tree('#1', [Token(ParserConst.token_type, '&#x23DE;')])
        ])
    ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_under_1():
    """下にアクセントがある式のparse
    https://developer.mozilla.org/ja/docs/Web/MathML/Element/munder
    """
    mathml = """<math>
                    <munder accentunder="true">
                        <mrow>
                            <mi> x </mi>
                            <mo> + </mo>
                            <mi> y </mi>
                            <mo> + </mo>
                            <mi> z </mi>
                        </mrow>
                        <mo> &#x23DF; <!--BOTTOM CURLY BRACKET--> </mo>
                    </munder>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.under_data, [
            Tree('#0', [
                Tree(ParserConst.sum_data, [
                    Token(ParserConst.token_type, 'x'), Token(ParserConst.token_type, 'y'), Token(ParserConst.token_type, 'z')
                ])
            ]),
            Tree('#1', [Token(ParserConst.token_type, '&#x23DF;')])
        ])
    ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_underover_1():
    """上下にアクセントがある式のparse
    https://developer.mozilla.org/en-US/docs/Web/MathML/Element/munderover
    """
    mathml = """<math displaystyle="true">
                    <munderover>
                        <mo> &#x222B; <!--INTEGRAL--> </mo>
                        <mn> 0 </mn>
                        <mi> &#x221E; <!--INFINITY--> </mi>
                    </munderover>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.underover_data, [
            Tree('#0', [Token(ParserConst.token_type, '&#x222B;')]),
            Tree('#1', [Token(ParserConst.token_type, '0')]),
            Tree('#2', [Token(ParserConst.token_type, '&#x221E;')])
        ])
    ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_summation_1():
    r"""基本的な総和の式のparse
    \sum_{i=1}^{n} x_{i}
    """
    mathml = """<math displaystyle="true">
                    <munderover>
                        <mo>&#x2211;<!-- ∑ --></mo>
                        <mrow class="MJX-TeXAtom-ORD">
                            <mi>i</mi>
                            <mo>=</mo>
                            <mn>1</mn>
                        </mrow>
                        <mrow class="MJX-TeXAtom-ORD">
                            <mi>n</mi>
                        </mrow>
                    </munderover>
                    <msub>
                        <mi>x</mi>
                        <mrow class="MJX-TeXAtom-ORD">
                            <mi>i</mi>
                        </mrow>
                    </msub>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.product_data, [
            Tree(ParserConst.underover_data, [
                Tree('#0', [Token(ParserConst.token_type, '&#x2211;')]),
                Tree('#1', [Tree(ParserConst.expr_data, [
                    Token(ParserConst.token_type, 'i'),
                    Tree(ParserConst.equal_data, []),
                    Token(ParserConst.token_type, '1')
                ])]),
                Tree('#2', [Token(ParserConst.token_type, 'n')])
            ]),
            Tree(ParserConst.sub_data, [
                Tree('#0', [Token(ParserConst.token_type, 'x')]),
                Tree('#1', [Token(ParserConst.token_type, 'i')])
            ])
        ])
    ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_summation_2():
    r"""上と下がない総和の式のparse
    \sum R
    """
    mathml = """<math displaystyle="true">
                    <mo>&#x2211;<!-- ∑ --></mo>
                    <mi>R</mi>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.product_data, [
            Token(ParserConst.token_type, '&#x2211;'),
            Token(ParserConst.token_type, 'R')
        ])
    ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_summation_3():
    r"""上がない総和の式のparse
    \sum_{x\in R} x
    """
    mathml = """<math displaystyle="true">
                    <munder>
                        <mo>&#x2211;<!-- ∑ --></mo>
                        <mrow class="MJX-TeXAtom-ORD">
                            <mi>x</mi>
                            <mo>&#x2208;<!-- ∈ --></mo>
                            <mi>R</mi>
                        </mrow>
                    </munder>
                    <mi>x</mi>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.product_data, [
            Tree(ParserConst.under_data, [
                Tree('#0', [Token(ParserConst.token_type, '&#x2211;')]),
                Tree('#1', [
                    Tree(ParserConst.expr_data, [
                        Token(ParserConst.token_type, 'x'),
                        Tree(ParserConst.in_data, []),
                        Token(ParserConst.token_type, 'R')
                    ])
                ])
            ]),
            Token(ParserConst.token_type, 'x')
        ])
    ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_annotation_1():
    """annotationを含むMathMLのparse
    出典: 方程式 - Wikipedia
    https://ja.wikipedia.org/wiki/%E6%96%B9%E7%A8%8B%E5%BC%8F
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML"  alttext="{\displaystyle \left(x+1\right)^{2}=x^{2}+2x+1}">
                    <semantics>
                        <mrow class="MJX-TeXAtom-ORD">
                            <mstyle displaystyle="true" scriptlevel="0">
                                <msup>
                                <mrow>
                                    <mo>(</mo>
                                    <mrow>
                                    <mi>x</mi>
                                    <mo>+</mo>
                                    <mn>1</mn>
                                    </mrow>
                                    <mo>)</mo>
                                </mrow>
                                <mrow class="MJX-TeXAtom-ORD">
                                    <mn>2</mn>
                                </mrow>
                                </msup>
                                <mo>=</mo>
                                <msup>
                                <mi>x</mi>
                                <mrow class="MJX-TeXAtom-ORD">
                                    <mn>2</mn>
                                </mrow>
                                </msup>
                                <mo>+</mo>
                                <mn>2</mn>
                                <mi>x</mi>
                                <mo>+</mo>
                                <mn>1</mn>
                            </mstyle>
                        </mrow>
                        <annotation encoding="application/x-tex">{\displaystyle \left(x+1\right)^{2}=x^{2}+2x+1}</annotation>
                    </semantics>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.sup_data, [
            Tree('#0', [
                Tree(ParserConst.paren_data, [
                    Tree(ParserConst.sum_data, [
                        Token(ParserConst.token_type, 'x'), Token(ParserConst.token_type, '1')
                    ])
                ])
            ]),
            Tree('#1', [Token(ParserConst.token_type, '2')])
        ]),
        Tree(ParserConst.equal_data, []),
        Tree(ParserConst.sum_data, [
            Tree(ParserConst.sup_data, [
                Tree('#0', [Token(ParserConst.token_type, 'x')]),
                Tree('#1', [Token(ParserConst.token_type, '2')])
            ]),
            Tree(ParserConst.product_data, [
                Token(ParserConst.token_type, '2'),
                Token(ParserConst.token_type, 'x')
            ]),
            Token(ParserConst.token_type, '1')
        ])
    ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_table_1():
    """mtableのparse
    https://developer.mozilla.org/ja/docs/Web/MathML/Element/mtable
    """
    mathml = """<math>
                    <mi>X</mi>
                    <mo>=</mo>
                    <mtable frame="solid" rowlines="solid" align="axis 3">
                        <mtr>
                            <mtd><mi>A</mi></mtd>
                            <mtd><mi>B</mi></mtd>
                        </mtr>
                        <mtr>
                            <mtd><mi>C</mi></mtd>
                            <mtd><mi>D</mi></mtd>
                        </mtr>
                        <mtr>
                            <mtd><mi>E</mi></mtd>
                            <mtd><mi>F</mi></mtd>
                        </mtr>
                    </mtable>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Token(ParserConst.token_type, 'X'),
        Tree(ParserConst.equal_data, []),
        Tree(ParserConst.table_data, [
            Tree('#0', [
                Tree('#0', [Token(ParserConst.token_type, 'A')]),
                Tree('#1', [Token(ParserConst.token_type, 'B')])
            ]),
            Tree('#1', [
                Tree('#0', [Token(ParserConst.token_type, 'C')]),
                Tree('#1', [Token(ParserConst.token_type, 'D')])
            ]),
            Tree('#2', [
                Tree('#0', [Token(ParserConst.token_type, 'E')]),
                Tree('#1', [Token(ParserConst.token_type, 'F')])
            ])
        ])
    ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_table_2():
    """行列のparse
    [  1 9 -13]
    [ 20 5  -6]
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML"  alttext="{\displaystyle {\begin{bmatrix}1&amp;9&amp;-13\\20&amp;5&amp;-6\end{bmatrix}}}">
                    <semantics>
                        <mrow class="MJX-TeXAtom-ORD">
                            <mstyle displaystyle="true" scriptlevel="0">
                                <mrow class="MJX-TeXAtom-ORD">
                                <mrow>
                                    <mo>[</mo>
                                    <mtable rowspacing="4pt" columnspacing="1em">
                                        <mtr>
                                            <mtd>
                                            <mn>1</mn>
                                            </mtd>
                                            <mtd>
                                            <mn>9</mn>
                                            </mtd>
                                            <mtd>
                                            <mo>&#x2212;<!-- − --></mo>
                                            <mn>13</mn>
                                            </mtd>
                                        </mtr>
                                        <mtr>
                                            <mtd>
                                            <mn>20</mn>
                                            </mtd>
                                            <mtd>
                                            <mn>5</mn>
                                            </mtd>
                                            <mtd>
                                            <mo>&#x2212;<!-- − --></mo>
                                            <mn>6</mn>
                                            </mtd>
                                        </mtr>
                                    </mtable>
                                    <mo>]</mo>
                                </mrow>
                                </mrow>
                            </mstyle>
                        </mrow>
                        <annotation encoding="application/x-tex">{\displaystyle {\begin{bmatrix}1&amp;9&amp;-13\\20&amp;5&amp;-6\end{bmatrix}}}</annotation>
                    </semantics>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.product_data, [
            Token(ParserConst.token_type, '['),
            Tree(ParserConst.table_data, [
                Tree('#0', [
                    Tree('#0', [Token(ParserConst.token_type, '1')]),
                    Tree('#1', [Token(ParserConst.token_type, '9')]),
                    Tree('#2', [
                        Tree(ParserConst.neg_data, [
                            Token(ParserConst.token_type, '13')
                        ])
                    ])
                ]),
                Tree('#1', [
                    Tree('#0', [Token(ParserConst.token_type, '20')]),
                    Tree('#1', [Token(ParserConst.token_type, '5')]),
                    Tree('#2', [
                        Tree(ParserConst.neg_data, [
                            Token(ParserConst.token_type, '6')
                        ])
                    ])
                ])
            ]),
            Token(ParserConst.token_type, ']')
        ])
    ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_table_3():
    """mtableのparse．<mi>タグの中が空．
    https://ja.wikipedia.org/wiki/0.999...
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML"  alttext="{\displaystyle {\begin{aligned}c&amp;=0.999\cdots \\10c&amp;=9.999\cdots \\10c-c&amp;=9.999\cdots -0.999\cdots \\9c&amp;=9\\c&amp;=1\end{aligned}}}">
                    <semantics>
                        <mrow class="MJX-TeXAtom-ORD">
                        <mstyle displaystyle="true" scriptlevel="0">
                            <mrow class="MJX-TeXAtom-ORD">
                            <mtable columnalign="right left right left right left right left right left right left" rowspacing="3pt" columnspacing="0em 2em 0em 2em 0em 2em 0em 2em 0em 2em 0em" displaystyle="true">
                                <mtr>
                                <mtd>
                                    <mi>c</mi>
                                </mtd>
                                <mtd>
                                    <mi></mi>
                                    <mo>=</mo>
                                    <mn>0.999</mn>
                                    <mo>&#x22EF;<!-- ⋯ --></mo>
                                </mtd>
                                </mtr>
                            </mtable>
                            </mrow>
                        </mstyle>
                        </mrow>
                        <annotation encoding="application/x-tex">{\displaystyle {\begin{aligned}c&amp;=0.999\cdots \\10c&amp;=9.999\cdots \\10c-c&amp;=9.999\cdots -0.999\cdots \\9c&amp;=9\\c&amp;=1\end{aligned}}}</annotation>
                    </semantics>
                </math>"""
    expected = Tree(ParserConst.root_data, [
            Tree(ParserConst.table_data, [
                Tree('#0', [
                    Tree('#0', [Token(ParserConst.token_type, 'c')]),
                    Tree('#1', [
                        Tree(ParserConst.expr_data, [
                            Tree(ParserConst.atom_data, []),
                            Tree(ParserConst.equal_data, []),
                            Tree(ParserConst.omit_data, [Token(ParserConst.token_type, '0.9')])
                        ])
                    ])
                ])
            ])
        ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_mtext_1():
    """
    mtextを含む式
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML"  alttext="{\displaystyle {\text{inv}}(A)=\#\{(A_{i},A_{j})\mid i&lt;j{\text{ and }}A_{i}&gt;A_{j}\}}">
                    <semantics>
                        <mrow class="MJX-TeXAtom-ORD">
                            <mstyle displaystyle="true" scriptlevel="0">
                                <mrow class="MJX-TeXAtom-ORD">
                                    <mtext>inv</mtext>
                                </mrow>
                                <mo stretchy="false">(</mo>
                                <mi>A</mi>
                                <mo stretchy="false">)</mo>
                            </mstyle>
                        </mrow>
                        <annotation encoding="application/x-tex">{\displaystyle {\text{inv}}(A)=\#\{(A_{i},A_{j})\mid i&lt;j{\text{ and }}A_{i}&gt;A_{j}\}}</annotation>
                    </semantics>
                </math>"""
    expected = Tree(ParserConst.root_data, [
            Tree(ParserConst.product_data, [
                Token(ParserConst.token_type, 'inv'),
                Tree(ParserConst.paren_data, [
                    Token(ParserConst.token_type, 'A')
                ])
            ])
        ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_cdots_1():
    """0.999...のparse
    https://ja.wikipedia.org/wiki/%E7%B4%9A%E6%95%B0
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML">
                    <semantics>
                        <mrow class="MJX-TeXAtom-ORD">
                        <mstyle displaystyle="true" scriptlevel="0">
                            <mn>0.999</mn>
                            <mo>&#x22EF;<!-- ⋯ --></mo>
                        </mstyle>
                        </mrow>
                    </semantics>
                </math>"""
    expected = Tree(ParserConst.root_data, [
            Tree(ParserConst.omit_data, [Token(ParserConst.token_type, '0.9')]),
        ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_cdots_2():
    """0.999...のparse
    https://ja.wikipedia.org/wiki/%E7%B4%9A%E6%95%B0
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML"  alttext="{\displaystyle 0.999\cdots =0.9+0.09+\cdots +9\cdot 10^{-n}+\cdots }">
                    <semantics>
                        <mrow class="MJX-TeXAtom-ORD">
                        <mstyle displaystyle="true" scriptlevel="0">
                            <mn>0.999</mn>
                            <mo>&#x22EF;<!-- ⋯ --></mo>
                            <mo>=</mo>
                            <mn>0.9</mn>
                            <mo>+</mo>
                            <mn>0.09</mn>
                            <mo>+</mo>
                            <mo>&#x22EF;<!-- ⋯ --></mo>
                            <mo>+</mo>
                            <mn>9</mn>
                            <mo>&#x22C5;<!-- ⋅ --></mo>
                            <msup>
                            <mn>10</mn>
                            <mrow class="MJX-TeXAtom-ORD">
                                <mo>&#x2212;<!-- − --></mo>
                                <mi>n</mi>
                            </mrow>
                            </msup>
                            <mo>+</mo>
                            <mo>&#x22EF;<!-- ⋯ --></mo>
                        </mstyle>
                        </mrow>
                        <annotation encoding="application/x-tex">{\displaystyle 0.999\cdots =0.9+0.09+\cdots +9\cdot 10^{-n}+\cdots }</annotation>
                    </semantics>
                </math>"""
    expected = Tree(ParserConst.root_data, [
            Tree(ParserConst.omit_data, [Token(ParserConst.token_type, '0.9')]),
            Tree(ParserConst.equal_data, []),
            Tree(ParserConst.sum_data, [
                Token(ParserConst.token_type, '0.9'),
                Token(ParserConst.token_type, '0.09'),
                Tree(ParserConst.cdots_data, []),
                Tree(ParserConst.product_data, [
                    Token(ParserConst.token_type, '9'),
                    Tree(ParserConst.sup_data, [
                        Tree('#0', [Token(ParserConst.token_type, '10')]),
                        Tree('#1', [Tree(ParserConst.neg_data, [Token(ParserConst.token_type, 'n')])])
                    ])
                ]),
                Tree(ParserConst.cdots_data, []),
            ])
        ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_cdots_3():
    """0.999...のparse
    https://ja.wikipedia.org/wiki/0.999...
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML"  alttext="{\displaystyle {\begin{aligned}c&amp;=0.999\cdots \\10c&amp;=9.999\cdots \\10c-c&amp;=9.999\cdots -0.999\cdots \\9c&amp;=9\\c&amp;=1\end{aligned}}}">
                    <semantics>
                        <mrow class="MJX-TeXAtom-ORD">
                        <mstyle displaystyle="true" scriptlevel="0">
                            <mrow class="MJX-TeXAtom-ORD">
                            <mtable columnalign="right left right left right left right left right left right left" rowspacing="3pt" columnspacing="0em 2em 0em 2em 0em 2em 0em 2em 0em 2em 0em" displaystyle="true">
                                <mtr>
                                    <mtd>
                                        <mi>c</mi>
                                    </mtd>
                                    <mtd>
                                        <mi></mi>
                                        <mo>=</mo>
                                        <mn>0.999</mn>
                                        <mo>&#x22EF;<!-- ⋯ --></mo>
                                    </mtd>
                                </mtr>
                                <mtr>
                                    <mtd>
                                        <mn>10</mn>
                                        <mi>c</mi>
                                    </mtd>
                                    <mtd>
                                        <mi></mi>
                                        <mo>=</mo>
                                        <mn>9.999</mn>
                                        <mo>&#x22EF;<!-- ⋯ --></mo>
                                    </mtd>
                                </mtr>
                                <mtr>
                                    <mtd>
                                        <mn>10</mn>
                                        <mi>c</mi>
                                        <mo>&#x2212;<!-- − --></mo>
                                        <mi>c</mi>
                                    </mtd>
                                    <mtd>
                                        <mi></mi>
                                        <mo>=</mo>
                                        <mn>9.999</mn>
                                        <mo>&#x22EF;<!-- ⋯ --></mo>
                                        <mo>&#x2212;<!-- − --></mo>
                                        <mn>0.999</mn>
                                        <mo>&#x22EF;<!-- ⋯ --></mo>
                                    </mtd>
                                </mtr>
                                <mtr>
                                    <mtd>
                                        <mn>9</mn>
                                        <mi>c</mi>
                                    </mtd>
                                    <mtd>
                                        <mi></mi>
                                        <mo>=</mo>
                                        <mn>9</mn>
                                    </mtd>
                                </mtr>
                                <mtr>
                                    <mtd>
                                        <mi>c</mi>
                                    </mtd>
                                    <mtd>
                                        <mi></mi>
                                        <mo>=</mo>
                                        <mn>1</mn>
                                    </mtd>
                                </mtr>
                            </mtable>
                            </mrow>
                        </mstyle>
                        </mrow>
                        <annotation encoding="application/x-tex">{\displaystyle {\begin{aligned}c&amp;=0.999\cdots \\10c&amp;=9.999\cdots \\10c-c&amp;=9.999\cdots -0.999\cdots \\9c&amp;=9\\c&amp;=1\end{aligned}}}</annotation>
                    </semantics>
                </math>"""
    expected = Tree(ParserConst.root_data, [
            Tree(ParserConst.table_data, [
                Tree('#0', [
                    Tree('#0', [Token(ParserConst.token_type, 'c')]),
                    Tree('#1', [
                        Tree(ParserConst.expr_data, [
                            Tree(ParserConst.atom_data, []),
                            Tree(ParserConst.equal_data, []),
                            Tree(ParserConst.omit_data, [Token(ParserConst.token_type, '0.9')])
                        ])
                    ])
                ]),
                Tree('#1', [
                    Tree('#0', [Tree(ParserConst.product_data, [
                        Token(ParserConst.token_type, '10'),
                        Token(ParserConst.token_type, 'c')
                    ])]),
                    Tree('#1', [
                        Tree(ParserConst.expr_data, [
                            Tree(ParserConst.atom_data, []),
                            Tree(ParserConst.equal_data, []),
                            Tree(ParserConst.omit_data, [Token(ParserConst.token_type, '9.9')])
                        ])
                    ])
                ]),
                Tree('#2', [
                    Tree('#0', [Tree(ParserConst.sum_data, [
                        Tree(ParserConst.product_data, [
                            Token(ParserConst.token_type, '10'),
                            Token(ParserConst.token_type, 'c')
                        ]),
                        Tree(ParserConst.neg_data, [Token(ParserConst.token_type, 'c')])
                    ])]),
                    Tree('#1', [
                        Tree(ParserConst.expr_data, [
                            Tree(ParserConst.atom_data, []),
                            Tree(ParserConst.equal_data, []),
                            Tree(ParserConst.sum_data, [
                                Tree(ParserConst.omit_data, [Token(ParserConst.token_type, '9.9')]),
                                Tree(ParserConst.neg_data, [
                                    Tree(ParserConst.omit_data, [Token(ParserConst.token_type, '0.9')])
                                ])
                            ])
                        ])
                    ])
                ]),
                Tree('#3', [
                    Tree('#0', [
                        Tree(ParserConst.product_data, [
                            Token(ParserConst.token_type, '9'),
                            Token(ParserConst.token_type, 'c')
                        ])]),
                    Tree('#1', [
                        Tree(ParserConst.expr_data, [
                            Tree(ParserConst.atom_data, []),
                            Tree(ParserConst.equal_data, []),
                            Token(ParserConst.token_type, '9')
                        ])
                    ])
                ]),
                Tree('#4', [
                    Tree('#0', [Token(ParserConst.token_type, 'c')]),
                    Tree('#1', [
                        Tree(ParserConst.expr_data, [
                            Tree(ParserConst.atom_data, []),
                            Tree(ParserConst.equal_data, []),
                            Token(ParserConst.token_type, '1')
                        ])
                    ])
                ])
            ])
        ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_mspace_1():
    """
    mspaceを含む式。frac {frac{a}{b}}{frac{c}{d}}
    参考ページ：分数
    https://ja.wikipedia.org/wiki/%E5%88%86%E6%95%B0
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML"  alttext="{\displaystyle {\frac {\;{\dfrac {a}{b}}\;}{\;{\dfrac {c}{d}}\;}}}">
                    <semantics>
                        <mrow class="MJX-TeXAtom-ORD">
                        <mstyle displaystyle="true" scriptlevel="0">
                            <mrow class="MJX-TeXAtom-ORD">
                            <mfrac>
                                <mrow>
                                <mspace width="thickmathspace" />
                                <mrow class="MJX-TeXAtom-ORD">
                                    <mstyle displaystyle="true" scriptlevel="0">
                                    <mfrac>
                                        <mi>a</mi>
                                        <mi>b</mi>
                                    </mfrac>
                                    </mstyle>
                                </mrow>
                                <mspace width="thickmathspace" />
                                </mrow>
                                <mrow>
                                <mspace width="thickmathspace" />
                                <mrow class="MJX-TeXAtom-ORD">
                                    <mstyle displaystyle="true" scriptlevel="0">
                                    <mfrac>
                                        <mi>c</mi>
                                        <mi>d</mi>
                                    </mfrac>
                                    </mstyle>
                                </mrow>
                                <mspace width="thickmathspace" />
                                </mrow>
                            </mfrac>
                            </mrow>
                        </mstyle>
                        </mrow>
                        <annotation encoding="application/x-tex">{\displaystyle {\frac {\;{\dfrac {a}{b}}\;}{\;{\dfrac {c}{d}}\;}}}</annotation>
                    </semantics>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.frac_data, [
            Tree('#0', [
                Tree(ParserConst.frac_data, [
                    Tree('#0', [
                        Token(ParserConst.token_type, 'a')
                    ]),
                    Tree('#1', [
                        Token(ParserConst.token_type, 'b')
                    ])
                ])
            ]),
            Tree('#1', [
                Tree(ParserConst.frac_data, [
                    Tree('#0', [
                        Token(ParserConst.token_type, 'c')
                    ]),
                    Tree('#1', [
                        Token(ParserConst.token_type, 'd')
                    ])
                ])
            ]),
        ])
    ])
    assert expected == Parser.get_parsed_tree(mathml)


def test_parse_num_1():
    """数値のparse
    7
    """
    actual = Parser.parse(latex2mathml.converter.convert('7'))
    root = ParserConst.root_data
    expected = {'7', f'7/{root}'}
    assert actual == expected


def test_parse_add_1():
    """加算のparse
    1+2
    """
    actual = Parser.parse(latex2mathml.converter.convert('1+2'))
    sum_ = ParserConst.sum_data
    root = ParserConst.root_data
    expected = {
        '1', f'1/{sum_}', f'1/{sum_}/{root}',
        '2', f'2/{sum_}', f'2/{sum_}/{root}'
        }
    assert actual == expected


def test_parse_subtract_1():
    """減算のparse
    3-2
    """
    actual = Parser.parse(latex2mathml.converter.convert('3-2'))
    sum_ = ParserConst.sum_data
    root = ParserConst.root_data
    neg = ParserConst.neg_data
    expected = {
        '3', f'3/{sum_}', f'3/{sum_}/{root}',
        f'2/{neg}', f'2/{neg}/{sum_}', f'2/{neg}/{sum_}/{root}'
        }
    assert actual == expected


def test_parse_product_1():
    """乗算のparse
    4*5
    """
    actual = Parser.parse(latex2mathml.converter.convert('4*5'))
    product = ParserConst.product_data
    root = ParserConst.root_data
    expected = {
        '4', f'4/{product}', f'4/{product}/{root}',
        '5', f'5/{product}', f'5/{product}/{root}'
        }
    assert actual == expected


def test_parse_div_1():
    """除算のparse
    3/2
    これは3*(1/2)として処理する．
    """
    actual = Parser.parse(latex2mathml.converter.convert('3/2'))
    product = ParserConst.product_data
    root = ParserConst.root_data
    frac = ParserConst.frac_data
    expected = {
        '3', f'3/{product}', f'3/{product}/{root}',
        '1', f'1/#0/{frac}', f'1/#0/{frac}/{product}', f'1/#0/{frac}/{product}/{root}',
        '2', f'2/#1/{frac}', f'2/#1/{frac}/{product}', f'2/#1/{frac}/{product}/{root}'
    }
    assert actual == expected


def test_parse_eq_1():
    """等式のparse
    a=b
    """
    actual = Parser.parse(latex2mathml.converter.convert('a=b'))
    root = ParserConst.root_data
    equal = ParserConst.equal_data
    expected = {
        'a', f'a/{equal}', f'a/{equal}/{root}',
        'b', f'b/{equal}', f'b/{equal}/{root}'
        }
    assert actual == expected


def test_parse_eq_2():
    """y=0
    Wikipediaのシグモイド関数のページに含まれる数式．
    https://ja.wikipedia.org/wiki/%E3%82%B7%E3%82%B0%E3%83%A2%E3%82%A4%E3%83%89%E9%96%A2%E6%95%B0
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML"  alttext="{\displaystyle y=0}">
                    <semantics>
                        <mrow class="MJX-TeXAtom-ORD">
                            <mstyle displaystyle="true" scriptlevel="0">
                                <mi>y</mi>
                                <mo>=</mo>
                                <mn>0</mn>
                            </mstyle>
                        </mrow>
                        <annotation encoding="application/x-tex">{\displaystyle y=0}</annotation>
                    </semantics>
                </math>"""
    actual = Parser.parse(mathml)
    root = ParserConst.root_data
    equal = ParserConst.equal_data
    expected = {
        'y', f'y/{equal}', f'y/{equal}/{root}',
        '0', f'0/{equal}', f'0/{equal}/{root}'
    }
    assert actual == expected


def test_parse_table_1():
    """行列のparse
    [  1 9 -13]
    [ 20 5  -6]
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML"  alttext="{\displaystyle {\begin{bmatrix}1&amp;9&amp;-13\\20&amp;5&amp;-6\end{bmatrix}}}">
                    <semantics>
                        <mrow class="MJX-TeXAtom-ORD">
                            <mstyle displaystyle="true" scriptlevel="0">
                                <mrow class="MJX-TeXAtom-ORD">
                                <mrow>
                                    <mo>[</mo>
                                    <mtable rowspacing="4pt" columnspacing="1em">
                                        <mtr>
                                            <mtd>
                                            <mn>1</mn>
                                            </mtd>
                                            <mtd>
                                            <mn>9</mn>
                                            </mtd>
                                            <mtd>
                                            <mo>&#x2212;<!-- − --></mo>
                                            <mn>13</mn>
                                            </mtd>
                                        </mtr>
                                        <mtr>
                                            <mtd>
                                            <mn>20</mn>
                                            </mtd>
                                            <mtd>
                                            <mn>5</mn>
                                            </mtd>
                                            <mtd>
                                            <mo>&#x2212;<!-- − --></mo>
                                            <mn>6</mn>
                                            </mtd>
                                        </mtr>
                                    </mtable>
                                    <mo>]</mo>
                                </mrow>
                                </mrow>
                            </mstyle>
                        </mrow>
                        <annotation encoding="application/x-tex">{\displaystyle {\begin{bmatrix}1&amp;9&amp;-13\\20&amp;5&amp;-6\end{bmatrix}}}</annotation>
                    </semantics>
                </math>"""
    actual = Parser.parse(mathml)
    table = ParserConst.table_data
    product = ParserConst.product_data
    neg = ParserConst.neg_data
    root = ParserConst.root_data
    expected = {
        '[', f'[/{product}', f'[/{product}/{root}',
        '1', f'1/#0/#0/{table}', f'1/#0/#0/{table}/{product}', f'1/#0/#0/{table}/{product}/{root}',
        '9', f'9/#1/#0/{table}', f'9/#1/#0/{table}/{product}', f'9/#1/#0/{table}/{product}/{root}',
        f'13/{neg}', f'13/{neg}/#2/#0/{table}', f'13/{neg}/#2/#0/{table}/{product}', f'13/{neg}/#2/#0/{table}/{product}/{root}',
        '20', f'20/#0/#1/{table}', f'20/#0/#1/{table}/{product}', f'20/#0/#1/{table}/{product}/{root}',
        '5', f'5/#1/#1/{table}', f'5/#1/#1/{table}/{product}', f'5/#1/#1/{table}/{product}/{root}',
        f'6/{neg}', f'6/{neg}/#2/#1/{table}', f'6/{neg}/#2/#1/{table}/{product}', f'6/{neg}/#2/#1/{table}/{product}/{root}',
        ']', f']/{product}', f']/{product}/{root}'
    }
    assert actual == expected


def test_make_new_trees_1():
    tree = Tree(ParserConst.root_data, [
        Token(ParserConst.token_type, 'y'),
        Tree(ParserConst.equal_data, []),
        Tree(ParserConst.product_data, [
            Token(ParserConst.token_type, 'a'),
            Token(ParserConst.token_type, 'x')
            ])
        ])
    actual = Parser._make_new_trees(tree)
    expected = [
        Tree(ParserConst.root_data, [
            Tree(ParserConst.equal_data, [
                Token(ParserConst.token_type, 'y'),
                Tree(ParserConst.product_data, [
                    Token(ParserConst.token_type, 'a'),
                    Token(ParserConst.token_type, 'x')
                ])
            ])
        ])
    ]
    assert actual == expected
