# -*- coding: utf-8 -*-
"""module description
"""
import html

import latex2mathml.converter
from lark import Tree, Token

from twels.expr.expression import Expression
from twels.expr.parser import Parser
from twels.expr.parser_const import ParserConst


def test_get_parsed_tree_atom_1():
    """演算子を含まないparse。
    a
    """
    mathml = '<math><mi>a</mi></math>'
    expected = Tree(ParserConst.root_data, [
        Token(ParserConst.token_type, 'a')
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_add_1():
    """加算のparse。
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
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_add_2():
    """加算のparse。
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
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_add_3():
    """加算のparse。
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
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_subtract_1():
    """減算のparse。
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
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_subtract_2():
    """減算のparse。
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
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_mul_1():
    """乗算のparse。
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
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_mul_2():
    """乗算のparse。
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
            Token(ParserConst.token_type, 'a'),
            Token(ParserConst.token_type, 'b'),
            Token(ParserConst.token_type, 'c')
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_mul_3():
    """乗算のparse。
    2 ⋅ ab
    """
    mathml = """<math>
                    <mn>2</mn>
                    <mo>⋅</mo>
                    <mi>a</mi>
                    <mi>b</mi>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.product_data, [
            Token(ParserConst.token_type, '2'),
            Token(ParserConst.token_type, 'a'),
            Token(ParserConst.token_type, 'b')
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_frac_1():
    """分数のparse。
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
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_frac_2():
    """分数のparse。
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
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_frac_3():
    """分数のparse。
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
        Tree(ParserConst.equal_data, [
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
            Tree(ParserConst.product_data, [
                Tree(ParserConst.sup_data, [
                    Tree('#0', [Token(ParserConst.token_type, 'e')]),
                    Tree('#1', [Token(ParserConst.token_type, 'x')])
                ]),
                # TODO: 式の最後にある','は無視するように修正
                Token(ParserConst.token_type, ',')
            ])
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


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
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_div_1():
    """除算のparse。
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
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_div_2():
    """変数として'/'が使われている場合。
    A/~
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML">
                    <mrow>
                        <mi>A</mi>
                        <mi mathvariant="normal">/</mi>
                        <mo lspace="0em" rspace="0em">∼</mo>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.product_data, [
            Token(ParserConst.token_type, 'A'),
            Token(ParserConst.token_type, ParserConst.slash_data),
            Token(ParserConst.token_type, '∼')
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_eq_1():
    """等号を含む式のparse。
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
        Tree(ParserConst.equal_data, [
            Token(ParserConst.token_type, 'y'),
            Tree(ParserConst.product_data, [
                Token(ParserConst.token_type, 'a'),
                Token(ParserConst.token_type, 'x')
                ])
            ])
        ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_eq_2():
    """等号を2つ含む式のparse。
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
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_lt_1():
    """不等号（&lt; <）を含む式のparse。
    2<3
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML"  alttext="{\displaystyle 2&lt;3}">
                    <semantics>
                        <mrow class="MJX-TeXAtom-ORD">
                            <mn>2</mn>
                            <mo>&lt;</mo>
                            <mn>3</mn>
                        </mrow>
                    </semantics>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.less_data, [
            Tree('#0', [Token(ParserConst.token_type, '2')]),
            Tree('#1', [Token(ParserConst.token_type, '3')])
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_parse_subset_1():
    """parse subset.
    A ⊂ B
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML">
                    <mi>A</mi>
                    <mo>⊂</mo>
                    <mi>B</mi>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.subset_data, [
            Tree('#0', [Token(ParserConst.token_type, 'A')]),
            Tree('#1', [Token(ParserConst.token_type, 'B')])
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_parse_supset_1():
    """parse supset.
    A ⊃ B
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML">
                    <mi>A</mi>
                    <mo>⊃</mo>
                    <mi>B</mi>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.supset_data, [
            Tree('#0', [Token(ParserConst.token_type, 'A')]),
            Tree('#1', [Token(ParserConst.token_type, 'B')])
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_parse_subseteq_1():
    """parse subseteq.
    A ⊆ B
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML">
                    <mi>A</mi>
                    <mo>&#x2286;<!-- ⊆ --></mo>
                    <mi>B</mi>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.subseteq_data, [
            Tree('#0', [Token(ParserConst.token_type, 'A')]),
            Tree('#1', [Token(ParserConst.token_type, 'B')])
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_parse_supseteq_1():
    """parse supseteq.
    A ⊇ B
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML">
                    <mi>A</mi>
                    <mo>⊇</mo>
                    <mi>B</mi>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.supseteq_data, [
            Tree('#0', [Token(ParserConst.token_type, 'A')]),
            Tree('#1', [Token(ParserConst.token_type, 'B')])
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_parse_in_1():
    """parse in.
    a ∈ A
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML">
                    <mi>a</mi>
                    <mo>∈</mo>
                    <mi>A</mi>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.in_data, [
            Tree('#0', [Token(ParserConst.token_type, 'a')]),
            Tree('#1', [Token(ParserConst.token_type, 'A')])
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_parse_ni_1():
    """parse ni.
    A ∋ a
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML">
                    <mi>A</mi>
                    <mo>∋</mo>
                    <mi>a</mi>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.ni_data, [
            Tree('#0', [Token(ParserConst.token_type, 'A')]),
            Tree('#1', [Token(ParserConst.token_type, 'a')])
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_gt_1():
    """不等号（&gt; >）を含む式のparse。
    3>2
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML"  alttext="{\displaystyle 2&lt;3}">
                    <semantics>
                        <mrow class="MJX-TeXAtom-ORD">
                            <mn>3</mn>
                            <mo>&gt;</mo>
                            <mn>2</mn>
                        </mrow>
                    </semantics>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.greater_data, [
            Tree('#0', [Token(ParserConst.token_type, '3')]),
            Tree('#1', [Token(ParserConst.token_type, '2')])
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_neq_1():
    """parse not equal.
    x≠0
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML">
                    <mrow>
                        <mi>x</mi>
                        <mo>&#x02260;</mo>
                        <mn>0</mn>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.neq_data, [
            Token(ParserConst.token_type, 'x'),
            Token(ParserConst.token_type, '0')
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_equiv_1():
    """congruenceのparse。
    a ≡ b (mod n)
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML"  alttext="{\displaystyle a\equiv b{\pmod {n}}}">
                    <mrow class="MJX-TeXAtom-ORD">
                        <mstyle displaystyle="true" scriptlevel="0">
                            <mi>a</mi>
                            <mo>&#x2261;<!-- ≡ --></mo>
                            <mi>b</mi>
                            <mrow class="MJX-TeXAtom-ORD">
                                <mspace width="1em" />
                                <mo stretchy="false">(</mo>
                                <mi>mod</mi>
                                <mspace width="0.333em" />
                                <mi>n</mi>
                                <mo stretchy="false">)</mo>
                            </mrow>
                        </mstyle>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.equiv_data, [
            Token(ParserConst.token_type, 'a'),
            Token(ParserConst.token_type, 'b'),
            Tree(ParserConst.mod_data, [
                Token(ParserConst.token_type, 'n')
            ])
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_equiv_2():
    """congruenceのparse。modのところにmrowがない場合。
    a ≡ b (mod p)
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                    <mrow>
                        <mi>a</mi>
                        <mo>&#x02261;</mo>
                        <mi>b</mi>
                        <mspace width="1em" />
                        <mo>&#x00028;</mo>
                        <mi>mod</mi>
                        <mspace width="0.333em" />
                        <mi>p</mi>
                        <mo>&#x00029;</mo>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.equiv_data, [
            Token(ParserConst.token_type, 'a'),
            Token(ParserConst.token_type, 'b'),
            Tree(ParserConst.mod_data, [
                Token(ParserConst.token_type, 'p')
            ])
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_equiv_3():
    """modが省略されているcongruenceのparse。
    ac ≡ bc
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML">
                    <mrow>
                        <mi>a</mi>
                        <mi>c</mi>
                        <mo>≡</mo>
                        <mi>b</mi>
                        <mi>c</mi>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.equiv_data, [
            Tree(ParserConst.product_data, [
                Token(ParserConst.token_type, 'a'),
                Token(ParserConst.token_type, 'c')
            ]),
            Tree(ParserConst.product_data, [
                Token(ParserConst.token_type, 'b'),
                Token(ParserConst.token_type, 'c')
            ])
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_paren_1():
    """かっこを含む式のparse。
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
            Token(ParserConst.token_type, '3'),
            Tree(ParserConst.paren_data, [
                Tree(ParserConst.sum_data, [
                    Token(ParserConst.token_type, '4'),
                    Token(ParserConst.token_type, '5')
                ])
            ])
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_paren_2():
    """parse () and [].
    [(1+2)-3]-(4-5)=1
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML">
                    <mrow class="MJX-TeXAtom-ORD">
                        <mstyle displaystyle="true" scriptlevel="0">
                            <mo stretchy="false">[</mo>
                            <mo stretchy="false">(</mo>
                            <mn>1</mn>
                            <mo>+</mo>
                            <mn>2</mn>
                            <mo stretchy="false">)</mo>
                            <mo>−</mo>
                            <mn>3</mn>
                            <mo stretchy="false">]</mo>
                            <mo>−</mo>
                            <mo stretchy="false">(</mo>
                            <mn>4</mn>
                            <mo>−</mo>
                            <mn>5</mn>
                            <mo stretchy="false">)</mo>
                            <mo>=</mo>
                            <mn>1</mn>
                        </mstyle>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.equal_data, [
            Tree(ParserConst.sum_data, [
                Tree(ParserConst.paren_data, [
                    Tree(ParserConst.sum_data, [
                        Tree(ParserConst.paren_data, [
                            Tree(ParserConst.sum_data, [
                                Token('TOKEN', '1'),
                                Token('TOKEN', '2')
                            ])
                        ]),
                        Tree('neg', [Token('TOKEN', '3')])
                    ])
                ]),
                Tree('neg', [
                    Tree('paren', [
                        Tree('sum', [
                            Token('TOKEN', '4'),
                            Tree('neg', [Token('TOKEN', '5')])
                        ])
                    ])
                ])
            ]),
            Token('TOKEN', '1')])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_paren_3():
    """parse () and {}.
    {(1+2)-3}-(4-5)
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML">
                    <mrow class="MJX-TeXAtom-ORD">
                        <mstyle displaystyle="true" scriptlevel="0">
                            <mo stretchy="false">{</mo>
                            <mo stretchy="false">(</mo>
                            <mn>1</mn>
                            <mo>+</mo>
                            <mn>2</mn>
                            <mo stretchy="false">)</mo>
                            <mo>−</mo>
                            <mn>3</mn>
                            <mo stretchy="false">}</mo>
                            <mo>−</mo>
                            <mo stretchy="false">(</mo>
                            <mn>4</mn>
                            <mo>−</mo>
                            <mn>5</mn>
                            <mo stretchy="false">)</mo>
                        </mstyle>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.sum_data, [
            Tree(ParserConst.paren_data, [
                Tree(ParserConst.sum_data, [
                    Tree(ParserConst.paren_data, [
                        Tree(ParserConst.sum_data, [
                            Token('TOKEN', '1'),
                            Token('TOKEN', '2')
                        ])
                    ]),
                    Tree('neg', [Token('TOKEN', '3')])
                ])
            ]),
            Tree('neg', [
                Tree('paren', [
                    Tree('sum', [
                        Token('TOKEN', '4'),
                        Tree('neg', [Token('TOKEN', '5')])
                    ])
                ])
            ])
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_abs_1():
    """絶対値のparse。
    |x|
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                    <mrow class="MJX-TeXAtom-ORD">
                        <mo stretchy="false">|</mo>
                    </mrow>
                    <mi>x</mi>
                    <mrow class="MJX-TeXAtom-ORD">
                        <mo stretchy="false">|</mo>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.abs_data, [
            Token(ParserConst.token_type, 'x')
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_sup_1():
    """上付き文字のparse。
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
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_sub_1():
    """下付き文字のparse。
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
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_subsup_1():
    """下付き上付き文字のparse。
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
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_lsup_1():
    r"""parse *R.
    超実数体*Rのように、文字の左上にアスタリスク等を表示したい場合があるようだ。
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML">
                    <mrow class="MJX-TeXAtom-ORD">
                        <msup>
                            <mrow class="MJX-TeXAtom-ORD">
                            </mrow>
                            <mrow class="MJX-TeXAtom-ORD">
                                <mo>&#x2217;<!-- ∗ --></mo>
                            </mrow>
                        </msup>
                        <mrow class="MJX-TeXAtom-ORD">
                            <mi>R</mi>
                        </mrow>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.lsup_data, [
            Tree('#0', [Token(ParserConst.token_type, 'R')]),
            Tree('#1', [Token(ParserConst.token_type, '∗')]),
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_lsup_2():
    r"""parse {}^{t}AA.
    転置行列{}^{t}Aと行列Aの積。
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML">
                    <mrow class="MJX-TeXAtom-ORD">
                        <msup>
                            <mrow class="MJX-TeXAtom-ORD">
                            </mrow>
                            <mrow class="MJX-TeXAtom-ORD">
                                <mi>t</mi>
                            </mrow>
                        </msup>
                        <mi>A</mi>
                        <mi>A</mi>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.product_data, [
            Tree(ParserConst.lsup_data, [
                Tree('#0', [Token(ParserConst.token_type, 'A')]),
                Tree('#1', [Token(ParserConst.token_type, 't')]),
            ]),
            Token(ParserConst.token_type, 'A')
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_lsub_1():
    """parse combination.
    nCr
    """
    mathml = """<math>
                    <mrow>
                        <msub>
                            <mrow></mrow>
                            <mi>n</mi>
                        </msub>
                        <msub>
                            <mi>C</mi>
                            <mi>r</mi>
                        </msub>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.lsub_data, [
            Tree('#0', [
                Tree(ParserConst.sub_data, [
                    Tree('#0', [Token(ParserConst.token_type, 'C')]),
                    Tree('#1', [Token(ParserConst.token_type, 'r')]),
                ])
            ]),
            Tree('#1', [Token(ParserConst.token_type, 'n')])
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_sqrt_1():
    """平方根のparse。
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
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_root_1():
    """n乗根のparse。
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
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_over_1():
    """上にアクセントがある式のparse。
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
            Tree('#1', [Token(ParserConst.token_type, html.unescape('&#x23DE;'))])
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_under_1():
    """下にアクセントがある式のparse。
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
            Tree('#1', [Token(ParserConst.token_type, html.unescape('&#x23DF;'))])
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_underover_1():
    """上下にアクセントがある式のparse。
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
            Tree('#0', [Token(ParserConst.token_type, html.unescape('&#x222B;'))]),
            Tree('#1', [Token(ParserConst.token_type, '0')]),
            Tree('#2', [Token(ParserConst.token_type, html.unescape('&#x221E;'))])
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_summation_1():
    r"""基本的な総和の式のparse。
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
        Tree(ParserConst.summation_data, [
            Tree('#0', [Tree(ParserConst.equal_data, [
                Token(ParserConst.token_type, 'i'),
                Token(ParserConst.token_type, '1')
            ])]),
            Tree('#1', [Token(ParserConst.token_type, 'n')]),
            Tree('#2', [
                Tree(ParserConst.sub_data, [
                    Tree('#0', [Token(ParserConst.token_type, 'x')]),
                    Tree('#1', [Token(ParserConst.token_type, 'i')])
                ])
            ]),
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_summation_2():
    r"""上と下がない総和の式のparse。
    \sum R
    """
    mathml = """<math displaystyle="true">
                    <mo>&#x2211;<!-- ∑ --></mo>
                    <mi>R</mi>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.product_data, [
            Token(ParserConst.token_type, html.unescape('&#x2211;')),
            Token(ParserConst.token_type, 'R')
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_summation_3():
    r"""上がない総和の式のparse。
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
                Tree('#0', [Token(ParserConst.token_type, html.unescape('&#x2211;'))]),
                Tree('#1', [
                    Tree(ParserConst.in_data, [
                        Tree('#0', [Token(ParserConst.token_type, 'x')]),
                        Tree('#1', [Token(ParserConst.token_type, 'R')])
                    ])
                ])
            ]),
            Token(ParserConst.token_type, 'x')
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_summation_4():
    r"""Σの左に定数がある場合。
    λ\sum_{i=a}^{b} x_{i}
    """
    mathml = """<math displaystyle="true">
                    <mi>&#x03BB;<!-- λ --></mi>
                    <munderover>
                        <mo>&#x2211;<!-- ∑ --></mo>
                        <mrow class="MJX-TeXAtom-ORD">
                            <mi>i</mi>
                            <mo>=</mo>
                            <mi>a</mi>
                        </mrow>
                        <mrow class="MJX-TeXAtom-ORD">
                            <mi>b</mi>
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
            Token(ParserConst.token_type, 'λ'),
            Tree(ParserConst.summation_data, [
                Tree('#0', [Tree(ParserConst.equal_data, [
                    Token(ParserConst.token_type, 'i'),
                    Token(ParserConst.token_type, 'a')
                ])]),
                Tree('#1', [Token(ParserConst.token_type, 'b')]),
                Tree('#2', [
                    Tree(ParserConst.sub_data, [
                        Tree('#0', [Token(ParserConst.token_type, 'x')]),
                        Tree('#1', [Token(ParserConst.token_type, 'i')])
                    ])
                ]),
            ])
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_summation_5():
    r"""Σの要素が複数の変数の積の場合。
    \sum_{i=a}^{b} λx_{i}
    """
    mathml = """<math displaystyle="true">
                    <munderover>
                        <mo>&#x2211;<!-- ∑ --></mo>
                        <mrow class="MJX-TeXAtom-ORD">
                            <mi>i</mi>
                            <mo>=</mo>
                            <mi>a</mi>
                        </mrow>
                        <mrow class="MJX-TeXAtom-ORD">
                            <mi>b</mi>
                        </mrow>
                    </munderover>
                    <mi>&#x03BB;<!-- λ --></mi>
                    <msub>
                        <mi>x</mi>
                        <mrow class="MJX-TeXAtom-ORD">
                            <mi>i</mi>
                        </mrow>
                    </msub>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.summation_data, [
            Tree('#0', [Tree(ParserConst.equal_data, [
                Token(ParserConst.token_type, 'i'),
                Token(ParserConst.token_type, 'a')
            ])]),
            Tree('#1', [Token(ParserConst.token_type, 'b')]),
            Tree('#2', [
                Tree(ParserConst.product_data, [
                    Token(ParserConst.token_type, 'λ'),
                    Tree(ParserConst.sub_data, [
                        Tree('#0', [Token(ParserConst.token_type, 'x')]),
                        Tree('#1', [Token(ParserConst.token_type, 'i')])
                    ])
                ])
            ]),
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_summation_6():
    r"""総和を含む式。
    g(b) + \sum_{i=a}^{b-1} g(i)
    """
    mathml = """<math displaystyle="true">
                    <mi>g</mi>
                    <mo stretchy="false">(</mo>
                    <mi>b</mi>
                    <mo stretchy="false">)</mo>
                    <mo>+</mo>
                    <munderover>
                        <mo>&#x2211;<!-- ∑ --></mo>
                        <mrow class="MJX-TeXAtom-ORD">
                            <mi>i</mi>
                            <mo>=</mo>
                            <mi>a</mi>
                        </mrow>
                        <mrow class="MJX-TeXAtom-ORD">
                            <mi>b</mi>
                            <mo>&#x2212;<!-- − --></mo>
                            <mn>1</mn>
                        </mrow>
                    </munderover>
                    <mi>g</mi>
                    <mo stretchy="false">(</mo>
                    <mi>i</mi>
                    <mo stretchy="false">)</mo>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.sum_data, [
            Tree(ParserConst.product_data, [
                Token(ParserConst.token_type, 'g'),
                Tree(ParserConst.paren_data, [
                    Token(ParserConst.token_type, 'b')
                ])
            ]),
            Tree(ParserConst.summation_data, [
                Tree('#0', [Tree(ParserConst.equal_data, [
                    Token(ParserConst.token_type, 'i'),
                    Token(ParserConst.token_type, 'a')
                ])]),
                Tree('#1', [
                    Tree(ParserConst.sum_data, [
                        Token(ParserConst.token_type, 'b'),
                        Tree(ParserConst.neg_data, [Token(ParserConst.token_type, '1')])
                    ])
                ]),
                Tree('#2', [
                    Tree(ParserConst.product_data, [
                        Token(ParserConst.token_type, 'g'),
                        Tree(ParserConst.paren_data, [
                            Token(ParserConst.token_type, 'i')
                        ])
                    ])
                ]),
            ])
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_prod_of_a_seq_1():
    r"""parse product of a sequence.
    \prod _{i=1}^{6}i^{2}
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML"  alttext="{\displaystyle \textstyle \prod _{i=1}^{6}i^{2}}">
                    <mrow class="MJX-TeXAtom-ORD">
                        <munderover>
                            <mo>&#x220F;<!-- ∏ --></mo>
                            <mrow class="MJX-TeXAtom-ORD">
                                <mi>i</mi>
                                <mo>=</mo>
                                <mn>1</mn>
                            </mrow>
                                <mrow class="MJX-TeXAtom-ORD">
                                <mn>6</mn>
                            </mrow>
                        </munderover>
                        <msup>
                            <mi>i</mi>
                            <mrow class="MJX-TeXAtom-ORD">
                                <mn>2</mn>
                            </mrow>
                        </msup>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.product_of_seq_data, [
            Tree('#0', [Tree(ParserConst.equal_data, [
                Token(ParserConst.token_type, 'i'),
                Token(ParserConst.token_type, '1')
            ])]),
            Tree('#1', [Token(ParserConst.token_type, '6')]),
            Tree('#2', [
                Tree(ParserConst.sup_data, [
                    Tree('#0', [Token(ParserConst.token_type, 'i')]),
                    Tree('#1', [Token(ParserConst.token_type, '2')])
                ])
            ]),
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_integral_1():
    r"""parse integral.
    \int _{a}^{b}f(x) dx
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML">
                    <mrow class="MJX-TeXAtom-ORD">
                        <msubsup>
                            <mo>&#x222B;<!-- ∫ --></mo>
                            <mrow class="MJX-TeXAtom-ORD">
                                <mi>a</mi>
                            </mrow>
                            <mrow class="MJX-TeXAtom-ORD">
                                <mi>b</mi>
                            </mrow>
                        </msubsup>
                        <mi>f</mi>
                        <mo stretchy="false">(</mo>
                        <mi>x</mi>
                        <mo stretchy="false">)</mo>
                        <mspace width="thinmathspace" />
                        <mrow class="MJX-TeXAtom-ORD">
                        <mi mathvariant="normal">d</mi>
                        </mrow>
                        <mi>x</mi>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.integral_data, [
            Tree('#0', [Token(ParserConst.token_type, 'a')]),
            Tree('#1', [Token(ParserConst.token_type, 'b')]),
            Tree('#2', [
                Tree(ParserConst.product_data, [
                    Token(ParserConst.token_type, 'f'),
                    Tree(ParserConst.paren_data, [
                        Token(ParserConst.token_type, 'x')
                    ])
                ])
            ]),
            Tree('#3', [Token(ParserConst.token_type, 'x')])
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_lim_1():
    r"""parse limit.
    \lim _{n\to \infty }x_{n}
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML">
                    <mrow class="MJX-TeXAtom-ORD">
                        <munder>
                            <mo movablelimits="true" form="prefix">lim</mo>
                            <mrow class="MJX-TeXAtom-ORD">
                                <mi>n</mi>
                                <mo stretchy="false">&#x2192;<!-- → --></mo>
                                <mi mathvariant="normal">&#x221E;<!-- ∞ --></mi>
                            </mrow>
                        </munder>
                        <msub>
                            <mi>x</mi>
                            <mrow class="MJX-TeXAtom-ORD">
                                <mi>n</mi>
                            </mrow>
                        </msub>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.lim_data, [
            Tree('#0', [Token(ParserConst.token_type, 'n')]),
            Tree('#1', [Token(ParserConst.token_type, '∞')]),
            Tree('#2', [
                Tree(ParserConst.sub_data, [
                    Tree('#0', [Token(ParserConst.token_type, 'x')]),
                    Tree('#1', [Token(ParserConst.token_type, 'n')])
                ])
            ]),
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_log_1():
    r"""logのparse。
    \log_{y}{x}
    """
    mathml = """<math>
                    <msub>
                        <mi>log</mi>
                        <mrow class="MJX-TeXAtom-ORD">
                            <mi>y</mi>
                        </mrow>
                    </msub>
                    <mi>x</mi>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.log_data, [
            Tree('#0', [Token(ParserConst.token_type, 'y')]),
            Tree('#1', [Token(ParserConst.token_type, 'x')])
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_log_2():
    r"""logのparse。
    \log x
    """
    mathml = """<math>
                    <mi>log</mi>
                    <mo></mo>
                    <mi>x</mi>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.log_data, [
            Tree('#1', [Token(ParserConst.token_type, 'x')])
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_log_3():
    r"""logのparse。
    \ln(1+x)
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML">
                    <mrow class="MJX-TeXAtom-ORD">
                    <mstyle displaystyle="true" scriptlevel="0">
                        <mi>ln</mi>
                        <mo>&#x2061;<!-- ⁡ --></mo>
                        <mo stretchy="false">(</mo>
                        <mn>1</mn>
                        <mo>+</mo>
                        <mi>x</mi>
                        <mo stretchy="false">)</mo>
                    </mstyle>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.log_data, [
            Tree('#0', [Token(ParserConst.token_type, 'e')]),
            Tree('#1', [
                Tree(ParserConst.paren_data, [
                    Tree(ParserConst.sum_data, [
                        Token(ParserConst.token_type, '1'),
                        Token(ParserConst.token_type, 'x')
                    ])
                ])
            ])
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_annotation_1():
    """annotationを含むMathMLのparse。
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
        Tree(ParserConst.equal_data, [
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
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_table_1():
    """mtableのparse。
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
        Tree(ParserConst.equal_data, [
            Token(ParserConst.token_type, 'X'),
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
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_table_2():
    """行列のparse。
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
        Tree(ParserConst.matrix_data, [
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
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_table_3():
    """parse parentheses matrix.
    (  1 9 -13)
    ( 20 5  -6)
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML"  alttext="{\displaystyle {\begin{bmatrix}1&amp;9&amp;-13\\20&amp;5&amp;-6\end{bmatrix}}}">
                    <semantics>
                        <mrow class="MJX-TeXAtom-ORD">
                            <mstyle displaystyle="true" scriptlevel="0">
                                <mrow class="MJX-TeXAtom-ORD">
                                <mrow>
                                    <mo>(</mo>
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
                                    <mo>)</mo>
                                </mrow>
                                </mrow>
                            </mstyle>
                        </mrow>
                        <annotation encoding="application/x-tex">{\displaystyle {\begin{bmatrix}1&amp;9&amp;-13\\20&amp;5&amp;-6\end{bmatrix}}}</annotation>
                    </semantics>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.matrix_data, [
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
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_table_4():
    """mtableのparse。<mi>タグの中が空。
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
        Tree(ParserConst.exprs_data, [
            Tree(ParserConst.equal_data, [
                Token(ParserConst.token_type, 'c'),
                Tree(ParserConst.omit_data, [Token(ParserConst.token_type, '0.9')])
            ])
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_table_5():
    """parse mtable.
    <mtr>1つに数式が1つある場合。表示をきれいにするためにmtableが使われている。
    """
    mathml = """<math>
                    <mrow>
                        <mtable>
                            <mtr>
                                <mtd>
                                    <mi>ζ</mi>
                                    <mo>(</mo>
                                    <mi>s</mi>
                                    <mo>)</mo>
                                </mtd>
                                <mtd>
                                    <mi></mi>
                                    <mrow></mrow>
                                    <mo>=</mo>
                                    <mrow></mrow>
                                </mtd>
                                <mtd>
                                    <msup>
                                        <mn>1</mn>
                                        <mrow>
                                            <mo>−</mo>
                                            <mi>s</mi>
                                        </mrow>
                                    </msup>
                                    <mo>+</mo>
                                    <msup>
                                        <mn>2</mn>
                                        <mrow>
                                            <mo>−</mo>
                                            <mi>s</mi>
                                        </mrow>
                                    </msup>
                                </mtd>
                                <mtd></mtd>
                                <mtd>
                                    <mrow></mrow>
                                    <mo>+</mo>
                                    <msup>
                                        <mn>3</mn>
                                        <mrow>
                                            <mo>−</mo>
                                            <mi>s</mi>
                                        </mrow>
                                    </msup>
                                    <mo>+</mo>
                                    <msup>
                                        <mn>4</mn>
                                        <mrow>
                                            <mo>−</mo>
                                            <mi>s</mi>
                                        </mrow>
                                    </msup>
                                </mtd>
                                <mtd></mtd>
                                <mtd>
                                    <mrow></mrow>
                                    <mo>+</mo>
                                    <msup>
                                        <mn>5</mn>
                                        <mrow>
                                            <mo>−</mo>
                                            <mi>s</mi>
                                        </mrow>
                                    </msup>
                                    <mo>+</mo>
                                    <msup>
                                        <mn>6</mn>
                                        <mrow>
                                            <mo>−</mo>
                                            <mi>s</mi>
                                        </mrow>
                                    </msup>
                                    <mo>+</mo>
                                    <mo>⋯</mo>
                                </mtd>
                                <mtd></mtd>
                            </mtr>
                            <mtr>
                                <mtd>
                                    <mn>2</mn>
                                    <mo>⋅</mo>
                                    <msup>
                                        <mn>2</mn>
                                        <mrow>
                                            <mo>−</mo>
                                            <mi>s</mi>
                                        </mrow>
                                    </msup>
                                    <mi>ζ</mi>
                                    <mo>(</mo>
                                    <mi>s</mi>
                                    <mo>)</mo>
                                </mtd>
                                <mtd>
                                    <mi></mi>
                                    <mrow></mrow>
                                    <mo>=</mo>
                                    <mrow></mrow>
                                </mtd>
                                <mtd>
                                    <mn>2</mn>
                                    <mo>⋅</mo>
                                    <msup>
                                        <mn>2</mn>
                                        <mrow>
                                            <mo>−</mo>
                                            <mi>s</mi>
                                        </mrow>
                                    </msup>
                                </mtd>
                                <mtd></mtd>
                                <mtd>
                                    <mrow></mrow>
                                    <mo>+</mo>
                                    <mn>2</mn>
                                    <mo>⋅</mo>
                                    <msup>
                                        <mn>4</mn>
                                        <mrow>
                                            <mo>−</mo>
                                            <mi>s</mi>
                                        </mrow>
                                    </msup>
                                </mtd>
                                <mtd></mtd>
                                <mtd>
                                    <mrow></mrow>
                                    <mo>+</mo>
                                    <mn>2</mn>
                                    <mo>⋅</mo>
                                    <msup>
                                        <mn>6</mn>
                                        <mrow>
                                            <mo>−</mo>
                                            <mi>s</mi>
                                        </mrow>
                                    </msup>
                                    <mo>+</mo>
                                    <mo>⋯</mo>
                                </mtd>
                                <mtd></mtd>
                            </mtr>
                            <mtr>
                                <mtd>
                                    <mrow>
                                        <mo>(</mo>
                                        <mrow>
                                            <mn>1</mn>
                                            <mo>−</mo>
                                            <msup>
                                                <mn>2</mn>
                                                <mrow>
                                                    <mn>1</mn>
                                                    <mo>−</mo>
                                                    <mi>s</mi>
                                                </mrow>
                                            </msup>
                                        </mrow>
                                        <mo>)</mo>
                                    </mrow>
                                    <mi>ζ</mi>
                                    <mo>(</mo>
                                    <mi>s</mi>
                                    <mo>)</mo>
                                </mtd>
                                <mtd>
                                    <mi></mi>
                                    <mrow></mrow>
                                    <mo>=</mo>
                                    <mrow></mrow>
                                </mtd>
                                <mtd>
                                    <msup>
                                        <mn>1</mn>
                                        <mrow>
                                            <mo>−</mo>
                                            <mi>s</mi>
                                        </mrow>
                                    </msup>
                                    <mo>−</mo>
                                    <msup>
                                        <mn>2</mn>
                                        <mrow>
                                            <mo>−</mo>
                                            <mi>s</mi>
                                        </mrow>
                                    </msup>
                                </mtd>
                                <mtd></mtd>
                                <mtd>
                                    <mrow></mrow>
                                    <mo>+</mo>
                                    <msup>
                                        <mn>3</mn>
                                        <mrow>
                                            <mo>−</mo>
                                            <mi>s</mi>
                                        </mrow>
                                    </msup>
                                    <mo>−</mo>
                                    <msup>
                                        <mn>4</mn>
                                        <mrow>
                                            <mo>−</mo>
                                            <mi>s</mi>
                                        </mrow>
                                    </msup>
                                </mtd>
                                <mtd></mtd>
                                <mtd>
                                    <mrow></mrow>
                                    <mo>+</mo>
                                    <msup>
                                        <mn>5</mn>
                                        <mrow>
                                            <mo>−</mo>
                                            <mi>s</mi>
                                        </mrow>
                                    </msup>
                                    <mo>−</mo>
                                    <msup>
                                        <mn>6</mn>
                                        <mrow>
                                            <mo>−</mo>
                                            <mi>s</mi>
                                        </mrow>
                                    </msup>
                                    <mo>+</mo>
                                    <mo>⋯</mo>
                                </mtd>
                                <mtd>
                                    <mi></mi>
                                    <mo>=</mo>
                                    <mi>η</mi>
                                    <mo>(</mo>
                                    <mi>s</mi>
                                    <mo>)</mo>
                                </mtd>
                            </mtr>
                        </mtable>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.exprs_data, [
            Tree(ParserConst.equal_data, [
                Tree(ParserConst.product_data, [
                    Token(ParserConst.token_type, 'ζ'),
                    Tree(ParserConst.paren_data, [Token(ParserConst.token_type, 's')])
                ]),
                Tree(ParserConst.sum_data, [
                    Tree(ParserConst.sup_data, [
                        Tree('#0', [Token(ParserConst.token_type, '1')]),
                        Tree('#1', [Tree(ParserConst.neg_data, [
                            Token(ParserConst.token_type, 's')
                        ])])
                    ]),
                    Tree(ParserConst.sup_data, [
                        Tree('#0', [Token(ParserConst.token_type, '2')]),
                        Tree('#1', [Tree(ParserConst.neg_data, [
                            Token(ParserConst.token_type, 's')
                        ])])
                    ]),
                    Tree(ParserConst.sup_data, [
                        Tree('#0', [Token(ParserConst.token_type, '3')]),
                        Tree('#1', [Tree(ParserConst.neg_data, [
                            Token(ParserConst.token_type, 's')
                        ])])
                    ]),
                    Tree(ParserConst.sup_data, [
                        Tree('#0', [Token(ParserConst.token_type, '4')]),
                        Tree('#1', [Tree(ParserConst.neg_data, [
                            Token(ParserConst.token_type, 's')
                        ])])
                    ]),
                    Tree(ParserConst.sup_data, [
                        Tree('#0', [Token(ParserConst.token_type, '5')]),
                        Tree('#1', [Tree(ParserConst.neg_data, [
                            Token(ParserConst.token_type, 's')
                        ])])
                    ]),
                    Tree(ParserConst.sup_data, [
                        Tree('#0', [Token(ParserConst.token_type, '6')]),
                        Tree('#1', [Tree(ParserConst.neg_data, [
                            Token(ParserConst.token_type, 's')
                        ])])
                    ]),
                    Tree(ParserConst.cdots_data, [])
                ])
            ]),
            Tree(ParserConst.equal_data, [
                Tree(ParserConst.product_data, [
                    Token(ParserConst.token_type, '2'),
                    Tree(ParserConst.sup_data, [
                        Tree('#0', [Token(ParserConst.token_type, '2')]),
                        Tree('#1', [Tree(ParserConst.neg_data, [
                            Token(ParserConst.token_type, 's')
                        ])])
                    ]),
                    Token(ParserConst.token_type, 'ζ'),
                    Tree(ParserConst.paren_data, [Token(ParserConst.token_type, 's')])
                ]),
                Tree(ParserConst.sum_data, [
                    Tree(ParserConst.product_data, [
                        Token(ParserConst.token_type, '2'),
                        Tree(ParserConst.sup_data, [
                            Tree('#0', [Token(ParserConst.token_type, '2')]),
                            Tree('#1', [Tree(ParserConst.neg_data, [
                                Token(ParserConst.token_type, 's')
                            ])])
                        ])
                    ]),
                    Tree(ParserConst.product_data, [
                        Token(ParserConst.token_type, '2'),
                        Tree(ParserConst.sup_data, [
                            Tree('#0', [Token(ParserConst.token_type, '4')]),
                            Tree('#1', [Tree(ParserConst.neg_data, [
                                Token(ParserConst.token_type, 's')
                            ])])
                        ])
                    ]),
                    Tree(ParserConst.product_data, [
                        Token(ParserConst.token_type, '2'),
                        Tree(ParserConst.sup_data, [
                            Tree('#0', [Token(ParserConst.token_type, '6')]),
                            Tree('#1', [Tree(ParserConst.neg_data, [
                                Token(ParserConst.token_type, 's')
                            ])])
                        ])
                    ]),
                    Tree(ParserConst.cdots_data, [])
                ])
            ]),
            Tree(ParserConst.expr_data, [
                Tree(ParserConst.product_data, [
                    Tree(ParserConst.paren_data, [
                        Tree(ParserConst.sum_data, [
                            Token(ParserConst.token_type, '1'),
                            Tree(ParserConst.neg_data, [
                                Tree(ParserConst.sup_data, [
                                    Tree('#0', [Token(ParserConst.token_type, '2')]),
                                    Tree('#1', [
                                        Tree(ParserConst.sum_data, [
                                            Token(ParserConst.token_type, '1'),
                                            Tree(ParserConst.neg_data, [
                                                Token(ParserConst.token_type, 's')
                                            ])
                                        ])
                                    ])
                                ])
                            ])
                        ])
                    ]),
                    Token(ParserConst.token_type, 'ζ'),
                    Tree(ParserConst.paren_data, [Token(ParserConst.token_type, 's')])
                ]),
                Tree(ParserConst.equal_data, []),
                Tree(ParserConst.sum_data, [
                    Tree(ParserConst.sup_data, [
                        Tree('#0', [Token(ParserConst.token_type, '1')]),
                        Tree('#1', [Tree(ParserConst.neg_data, [
                            Token(ParserConst.token_type, 's')
                        ])])
                    ]),
                    Tree(ParserConst.neg_data, [
                        Tree(ParserConst.sup_data, [
                            Tree('#0', [Token(ParserConst.token_type, '2')]),
                            Tree('#1', [Tree(ParserConst.neg_data, [
                                Token(ParserConst.token_type, 's')
                            ])])
                        ])
                    ]),
                    Tree(ParserConst.sup_data, [
                        Tree('#0', [Token(ParserConst.token_type, '3')]),
                        Tree('#1', [Tree(ParserConst.neg_data, [
                            Token(ParserConst.token_type, 's')
                        ])])
                    ]),
                    Tree(ParserConst.neg_data, [
                        Tree(ParserConst.sup_data, [
                            Tree('#0', [Token(ParserConst.token_type, '4')]),
                            Tree('#1', [Tree(ParserConst.neg_data, [
                                Token(ParserConst.token_type, 's')
                            ])])
                        ])
                    ]),
                    Tree(ParserConst.sup_data, [
                        Tree('#0', [Token(ParserConst.token_type, '5')]),
                        Tree('#1', [Tree(ParserConst.neg_data, [
                            Token(ParserConst.token_type, 's')
                        ])])
                    ]),
                    Tree(ParserConst.neg_data, [
                        Tree(ParserConst.sup_data, [
                            Tree('#0', [Token(ParserConst.token_type, '6')]),
                            Tree('#1', [Tree(ParserConst.neg_data, [
                                Token(ParserConst.token_type, 's')
                            ])])
                        ])
                    ]),
                    Tree(ParserConst.cdots_data, [])
                ]),
                Tree(ParserConst.equal_data, []),
                Tree(ParserConst.product_data, [
                    Token(ParserConst.token_type, 'η'),
                    Tree(ParserConst.paren_data, [Token(ParserConst.token_type, 's')])
                ])
            ])
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_mtext_1():
    """
    mtextを含む式。
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
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_cdots_1():
    """0.999...のparse。
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
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_cdots_2():
    """0.999...のparse。
    0.999... = 0.9 + 0.09 + ... + 9*10^{-n}
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
            Tree(ParserConst.equal_data, [
                Tree(ParserConst.omit_data, [Token(ParserConst.token_type, '0.9')]),
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
        ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_cdots_3():
    """0.999...のparse。
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
        Tree(ParserConst.exprs_data, [
            Tree(ParserConst.equal_data, [
                Token(ParserConst.token_type, 'c'),
                Tree(ParserConst.omit_data, [Token(ParserConst.token_type, '0.9')])
            ]),
            Tree(ParserConst.equal_data, [
                Tree(ParserConst.product_data, [
                    Token(ParserConst.token_type, '10'),
                    Token(ParserConst.token_type, 'c')
                ]),
                Tree(ParserConst.omit_data, [Token(ParserConst.token_type, '9.9')])
            ]),
            Tree(ParserConst.equal_data, [
                Tree(ParserConst.sum_data, [
                    Tree(ParserConst.product_data, [
                        Token(ParserConst.token_type, '10'),
                        Token(ParserConst.token_type, 'c')
                    ]),
                    Tree(ParserConst.neg_data, [Token(ParserConst.token_type, 'c')])
                ]),
                Tree(ParserConst.sum_data, [
                    Tree(ParserConst.omit_data, [Token(ParserConst.token_type, '9.9')]),
                    Tree(ParserConst.neg_data, [
                        Tree(ParserConst.omit_data, [Token(ParserConst.token_type, '0.9')])
                    ])
                ])
            ]),
            Tree(ParserConst.equal_data, [
                Tree(ParserConst.product_data, [
                    Token(ParserConst.token_type, '9'),
                    Token(ParserConst.token_type, 'c')
                ]),
                Token(ParserConst.token_type, '9')
            ]),
            Tree(ParserConst.equal_data, [
                Token(ParserConst.token_type, 'c'),
                Token(ParserConst.token_type, '1')
            ])
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_abbreviation_1():
    """parse abbreviation.
    frac{x_1 + x_2 + ... + x_n}{n}
    """
    mathml = """<math>
                    <mrow class="MJX-TeXAtom-ORD">
                        <mstyle displaystyle="true" scriptlevel="0">
                            <mfrac>
                                <mrow>
                                    <msub>
                                    <mi>x</mi>
                                    <mrow class="MJX-TeXAtom-ORD">
                                        <mn>1</mn>
                                    </mrow>
                                    </msub>
                                    <mo>+</mo>
                                    <msub>
                                    <mi>x</mi>
                                    <mrow class="MJX-TeXAtom-ORD">
                                        <mn>2</mn>
                                    </mrow>
                                    </msub>
                                    <mo>+</mo>
                                    <mo>&#x22EF;<!-- ⋯ --></mo>
                                    <mo>+</mo>
                                    <msub>
                                    <mi>x</mi>
                                    <mrow class="MJX-TeXAtom-ORD">
                                        <mi>n</mi>
                                    </mrow>
                                    </msub>
                                </mrow>
                                <mi>n</mi>
                            </mfrac>
                        </mstyle>
                    </mrow>
                </math>"""
    expected = Tree(ParserConst.root_data, [
            Tree(ParserConst.frac_data, [
                Tree('#0', [
                    Tree(ParserConst.abbr_add_data, [
                        Tree('#0', [
                            Tree(ParserConst.sub_data, [
                                Tree('#0', [Token(ParserConst.token_type, 'x')]),
                                Tree('#1', [Token(ParserConst.token_type, '1')])
                            ])
                        ]),
                        Tree('#1', [
                            Tree(ParserConst.sub_data, [
                                Tree('#0', [Token(ParserConst.token_type, 'x')]),
                                Tree('#1', [Token(ParserConst.token_type, 'n')])
                            ])
                        ]),
                        Tree('#2', [
                            Token(ParserConst.token_type, '1')
                        ])
                    ])
                ]),
                Tree('#1', [Token(ParserConst.token_type, 'n')])
            ])
        ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_abbreviation_2():
    """parse abbreviation.
    x_1 x_2 ... x_n
    """
    mathml = """<math>
                    <msub>
                        <mi>x</mi>
                        <mrow class="MJX-TeXAtom-ORD">
                            <mn>1</mn>
                        </mrow>
                    </msub>
                    <msub>
                        <mi>x</mi>
                        <mrow class="MJX-TeXAtom-ORD">
                            <mn>2</mn>
                        </mrow>
                    </msub>
                    <mo>&#x22EF;<!-- ⋯ --></mo>
                    <msub>
                        <mi>x</mi>
                        <mrow class="MJX-TeXAtom-ORD">
                            <mi>n</mi>
                        </mrow>
                    </msub>
                </math>"""
    expected = Tree(ParserConst.root_data, [
            Tree(ParserConst.abbr_mul_data, [
                Tree('#0', [
                    Tree(ParserConst.sub_data, [
                        Tree('#0', [Token(ParserConst.token_type, 'x')]),
                        Tree('#1', [Token(ParserConst.token_type, '1')])
                    ]),
                ]),
                Tree('#1', [
                    Tree(ParserConst.sub_data, [
                        Tree('#0', [Token(ParserConst.token_type, 'x')]),
                        Tree('#1', [Token(ParserConst.token_type, 'n')])
                    ])
                ]),
                Tree('#2', [
                    Token(ParserConst.token_type, '1')
                ])
            ])
        ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


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
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_get_parsed_tree_empty_mo_1():
    """parse empty mo.
    <mo>&#x2061;<!-- ⁡ --></mo>を含む場合。
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML"  alttext="{\displaystyle z-{\overline {z}}=2i\,\operatorname {Im} z}">
                    <semantics>
                        <mrow class="MJX-TeXAtom-ORD">
                        <mstyle displaystyle="true" scriptlevel="0">
                            <mi>z</mi>
                            <mo>&#x2212;<!-- − --></mo>
                            <mrow class="MJX-TeXAtom-ORD">
                                <mover>
                                    <mi>z</mi>
                                    <mo accent="false">&#x00AF;<!-- ¯ --></mo>
                                </mover>
                            </mrow>
                            <mo>=</mo>
                            <mn>2</mn>
                            <mi>i</mi>
                            <mspace width="thinmathspace" />
                            <mi>Im</mi>
                            <mo>&#x2061;<!-- ⁡ --></mo>
                            <mi>z</mi>
                        </mstyle>
                        </mrow>
                        <annotation encoding="application/x-tex">{\displaystyle z-{\overline {z}}=2i\,\operatorname {Im} z}</annotation>
                    </semantics>
                </math>"""
    expected = Tree(ParserConst.root_data, [
        Tree('equal', [
            Tree('sum', [
                Token('TOKEN', 'z'),
                Tree('neg', [
                    Tree('over', [
                        Tree('#0', [Token('TOKEN', 'z')]),
                        Tree('#1', [Token('TOKEN', '¯')])
                    ])
                ])
            ]),
            Tree('product', [
                Token('TOKEN', '2'),
                Token('TOKEN', 'i'),
                Token('TOKEN', 'Im'),
                Token('TOKEN', 'z')
            ])
        ])
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))


def test_parse_num_1():
    """数値のparse。
    7
    """
    mathml = latex2mathml.converter.convert('7')
    actual = Parser.parse(Expression(mathml))
    expected = {'7'}
    assert actual == expected


def test_parse_add_1():
    """加算のparse。
    1+2
    """
    mathml = latex2mathml.converter.convert('1+2')
    actual = Parser.parse(Expression(mathml))
    sum_ = ParserConst.sum_data
    expected = {
        '1', f'1/{sum_}',
        '2', f'2/{sum_}'
    }
    assert actual == expected


def test_parse_subtract_1():
    """減算のparse。
    3-2
    """
    mathml = latex2mathml.converter.convert('3-2')
    actual = Parser.parse(Expression(mathml))
    sum_ = ParserConst.sum_data
    neg = ParserConst.neg_data
    expected = {
        '3', f'3/{sum_}',
        f'2/{neg}', f'2/{neg}/{sum_}'
    }
    assert actual == expected


def test_parse_product_1():
    """乗算のparse。
    4*5
    """
    mathml = latex2mathml.converter.convert('4*5')
    actual = Parser.parse(Expression(mathml))
    product = ParserConst.product_data
    expected = {
        '4', f'4/{product}',
        '5', f'5/{product}'
    }
    assert actual == expected


def test_parse_div_1():
    """除算のparse。
    3/2
    これは3*(1/2)として処理する．
    """
    mathml = latex2mathml.converter.convert('3/2')
    actual = Parser.parse(Expression(mathml))
    product = ParserConst.product_data
    frac = ParserConst.frac_data
    expected = {
        '3', f'3/{product}',
        '1', f'1/#0/{frac}', f'1/#0/{frac}/{product}',
        '2', f'2/#1/{frac}', f'2/#1/{frac}/{product}'
    }
    assert actual == expected


def test_parse_eq_1():
    """等式のparse。
    a=b
    """
    mathml = latex2mathml.converter.convert('a=b')
    actual = Parser.parse(Expression(mathml))
    equal = ParserConst.equal_data
    expected = {
        'a', f'a/{equal}',
        'b', f'b/{equal}'
    }
    assert actual == expected


def test_parse_neq_1():
    """parse not equal.
    x≠0
    """
    mathml = latex2mathml.converter.convert(r'x \neq 0')
    actual = Parser.parse(Expression(mathml))
    neq = ParserConst.neq_data
    expected = {
        'x', f'x/{neq}',
        '0', f'0/{neq}'
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
    actual = Parser.parse(Expression(mathml))
    equal = ParserConst.equal_data
    expected = {
        'y', f'y/{equal}',
        '0', f'0/{equal}'
    }
    assert actual == expected


def test_parse_lt_1():
    """不等式のparse。
    a<b
    """
    mathml = latex2mathml.converter.convert('a<b')
    actual = Parser.parse(Expression(mathml))
    less = ParserConst.less_data
    expected = {
        'a', f'a/#0/{less}',
        'b', f'b/#1/{less}'
    }
    assert actual == expected


def test_parse_gt_1():
    """不等式のparse。
    a>b
    """
    mathml = latex2mathml.converter.convert('a>b')
    actual = Parser.parse(Expression(mathml))
    greater = ParserConst.greater_data
    expected = {
        'a', f'a/#0/{greater}',
        'b', f'b/#1/{greater}'
    }
    assert actual == expected


def test_parse_abs_1():
    """絶対値のparse。
    |x|
    """
    mathml = latex2mathml.converter.convert('|x|')
    actual = Parser.parse(Expression(mathml))
    abs = ParserConst.abs_data
    expected = {
        'x', f'x/{abs}'
    }
    assert actual == expected


def test_parse_equiv_1():
    """合同式のparse。
    a ≡ b (mod p)
    """
    mathml = latex2mathml.converter.convert('a \equiv b \pmod p')
    actual = Parser.parse(Expression(mathml))
    equiv = ParserConst.equiv_data
    mod = ParserConst.mod_data
    expected = {
        'a', f'a/{equiv}',
        'b', f'b/{equiv}',
        'p', f'p/{mod}', f'p/{mod}/{equiv}'
    }
    assert actual == expected


def test_parse_equiv_2():
    """合同式のparse。
    a ≡ b mod p
    """
    mathml = latex2mathml.converter.convert('a \equiv b \mod p')
    actual = Parser.parse(Expression(mathml))
    equiv = ParserConst.equiv_data
    mod = ParserConst.mod_data
    expected = {
        'a', f'a/{equiv}',
        'b', f'b/{equiv}',
        'p', f'p/{mod}', f'p/{mod}/{equiv}'
    }
    assert actual == expected


def test_parse_equiv_3():
    """合同式のparse。
    a ≡ b (p)
    """
    mathml = latex2mathml.converter.convert('a \equiv b \pod p')
    actual = Parser.parse(Expression(mathml))
    equiv = ParserConst.equiv_data
    mod = ParserConst.mod_data
    expected = {
        'a', f'a/{equiv}',
        'b', f'b/{equiv}',
        'p', f'p/{mod}', f'p/{mod}/{equiv}'
    }
    assert actual == expected


def test_parse_equiv_4():
    """modが省略されているcongruenceのparse。
    ac ≡ bc
    """
    mathml = latex2mathml.converter.convert('ac \equiv bc')
    actual = Parser.parse(Expression(mathml))
    equiv = ParserConst.equiv_data
    prod = ParserConst.product_data
    expected = {
        'a', f'a/{prod}', f'a/{prod}/{equiv}',
        'b', f'b/{prod}', f'b/{prod}/{equiv}',
        'c', f'c/{prod}', f'c/{prod}/{equiv}'
    }
    assert actual == expected


def test_parse_sum_1():
    r"""総和のparse。
    \sum_{i=1}^{n} x_{i}
    """
    mathml = latex2mathml.converter.convert(r'\sum_{i=1}^{n} x_{i}')
    actual = Parser.parse(Expression(mathml))
    equal = ParserConst.equal_data
    sub = ParserConst.sub_data
    s = ParserConst.summation_data
    expected = {
        'i', f'i/{equal}', f'i/{equal}/#0/{s}',
        '1', f'1/{equal}', f'1/{equal}/#0/{s}',
        'n', f'n/#1/{s}',
        'x', f'x/#0/{sub}', f'x/#0/{sub}/#2/{s}',
        f'i/#1/{sub}', f'i/#1/{sub}/#2/{s}'  # expectedは集合なので既に登場している'i'は書かない。
    }
    assert actual == expected


def test_parse_integral_1():
    r"""積分のparse。
    \int^{b}_{a} f(x) dx
    """
    mathml = latex2mathml.converter.convert(r'\int^{b}_{a} f(x) dx')
    actual = Parser.parse(Expression(mathml))
    integral = ParserConst.integral_data
    prod = ParserConst.product_data
    paren = ParserConst.paren_data
    expected = {
        'a', f'a/#0/{integral}',
        'b', f'b/#1/{integral}',
        'f', f'f/{prod}', f'f/{prod}/#2/{integral}',
        'x', f'x/{paren}', f'x/{paren}/{prod}', f'x/{paren}/{prod}/#2/{integral}',
        f'x/#3/{integral}'  # x of dx
    }
    assert actual == expected


def test_parse_lim_1():
    r"""parse limit.
    \lim _{n\to \infty }x_{n}
    """
    mathml = latex2mathml.converter.convert(r'\lim _{n\to \infty }x_{n}')
    actual = Parser.parse(Expression(mathml))
    lim = ParserConst.lim_data
    sub = ParserConst.sub_data
    expected = {
        'n', f'n/#0/{lim}',
        '∞', f'∞/#1/{lim}',
        'x', f'x/#0/{sub}', f'x/#0/{sub}/#2/{lim}',
        f'n/#1/{sub}', f'n/#1/{sub}/#2/{lim}',
    }
    assert actual == expected


def test_parse_log_1():
    r"""parse logarithm.
    \log_{y}{x}
    """
    mathml = latex2mathml.converter.convert(r'\log_{y}{x}')
    actual = Parser.parse(Expression(mathml))
    log = ParserConst.log_data
    expected = {
        'y', f'y/#0/{log}',
        'x', f'x/#1/{log}'
    }
    assert actual == expected


def test_parse_log_2():
    r"""parse logarithm.
    \log x
    """
    mathml = latex2mathml.converter.convert(r'\log x')
    actual = Parser.parse(Expression(mathml))
    log = ParserConst.log_data
    expected = {
        'x', f'x/#1/{log}'
    }
    assert actual == expected


def test_parse_log_3():
    r"""parse logarithm.
    \ln(1+x)
    """
    mathml = latex2mathml.converter.convert(r'\ln(1+x)')
    actual = Parser.parse(Expression(mathml))
    log = ParserConst.log_data
    sum = ParserConst.sum_data
    paren = ParserConst.paren_data
    expected = {
        'e', f'e/#0/{log}',
        '1', f'1/{sum}', f'1/{sum}/{paren}', f'1/{sum}/{paren}/#1/{log}',
        'x', f'x/{sum}', f'x/{sum}/{paren}', f'x/{sum}/{paren}/#1/{log}'
    }
    assert actual == expected


def test_parse_table_1():
    """行列のparse。
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
    actual = Parser.parse(Expression(mathml))
    matrix = ParserConst.matrix_data
    neg = ParserConst.neg_data
    expected = {
        '1', f'1/#0/#0/{matrix}',
        '9', f'9/#1/#0/{matrix}',
        f'13/{neg}', f'13/{neg}/#2/#0/{matrix}',
        '20', f'20/#0/#1/{matrix}',
        '5', f'5/#1/#1/{matrix}',
        f'6/{neg}', f'6/{neg}/#2/#1/{matrix}'
    }
    assert actual == expected


def test_make_new_trees_1():
    """ParserConst.root_dataが削除されていることを確認するテスト。
    """
    tree = Tree(ParserConst.root_data, [
        Tree(ParserConst.product_data, [
            Token(ParserConst.token_type, '2'), Token(ParserConst.token_type, '5')
            ])
        ])
    actual = Parser._make_new_trees(tree)

    expected = [
        Tree(ParserConst.product_data, [
            Token(ParserConst.token_type, '2'), Token(ParserConst.token_type, '5')
        ])
    ]
    assert actual == expected
