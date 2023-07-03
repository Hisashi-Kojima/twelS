# -*- coding: utf-8 -*-
"""this file has tests for functions not implemented.
"""

from lark import Tree, Token

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
    assert expected == False
