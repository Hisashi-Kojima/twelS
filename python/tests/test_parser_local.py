# -*- coding: utf-8 -*-
"""this file has tests for functions not implemented.
"""

from lark import Tree, Token

from twels.expr.expression import Expression
from twels.expr.parser import Parser
from twels.expr.parser_const import ParserConst


def test_make_new_trees_01():
    """等号が2つ現れている場合、複数の等式に分割されることを確認するテスト。
    a=b=c -> a=b, b=c, a=c
    """
    tree = Tree(ParserConst.root_data, [
        Token(ParserConst.token_type, 'a'),
        Tree(ParserConst.equal_data, []),
        Token(ParserConst.token_type, 'b'),
        Tree(ParserConst.equal_data, []),
        Token(ParserConst.token_type, 'c')
    ])
    actual = Parser._make_new_trees(tree)

    expected = [
        Tree(ParserConst.equal_data, [
            Token(ParserConst.token_type, 'a'),
            Token(ParserConst.token_type, 'b')
        ]),
        Tree(ParserConst.equal_data, [
            Token(ParserConst.token_type, 'b'),
            Token(ParserConst.token_type, 'c')
        ]),
        Tree(ParserConst.equal_data, [
            Token(ParserConst.token_type, 'c'),
            Token(ParserConst.token_type, 'a')
        ])
    ]
    assert actual == expected


def test_make_new_trees_02():
    """等号と不等号が現れている場合、複数の等式に分割されることを確認するテスト。
    a<b=c -> a<b, a<c, b=c
    """
    tree = Tree(ParserConst.root_data, [
        Token(ParserConst.token_type, 'a'),
        Tree(ParserConst.less_data, []),
        Token(ParserConst.token_type, 'b'),
        Tree(ParserConst.equal_data, []),
        Token(ParserConst.token_type, 'c')
    ])
    actual = Parser._make_new_trees(tree)

    expected = [
        Tree(ParserConst.less_data, [
            Tree('#0', [Token(ParserConst.token_type, 'a')]),
            Tree('#1', [Token(ParserConst.token_type, 'b')])
        ]),
        Tree(ParserConst.less_data, [
            Tree('#0', [Token(ParserConst.token_type, 'a')]),
            Tree('#1', [Token(ParserConst.token_type, 'c')])
        ]),
        Tree(ParserConst.equal_data, [
            Token(ParserConst.token_type, 'b'),
            Token(ParserConst.token_type, 'c')
        ])
    ]
    assert actual == expected


def test_get_parsed_tree_log_1():
    """logのparse。
    log_{y}{x}
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
    # TODO: expectedの実装。
    expected = Tree(ParserConst.root_data, [
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
    # TODO: expectedの実装。
    expected = Tree(ParserConst.root_data, [
    ])
    assert expected == Parser.get_parsed_tree(Expression(mathml))
