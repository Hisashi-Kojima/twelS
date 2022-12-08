# -*- coding: utf-8 -*-
"""this file has tests for functions not implemented.
"""

from lark import Tree, Token

from twels.expr.parser import Parser
from twels.expr.parser_const import ParserConst


def test_make_new_trees_2():
    """等号が2つ現れている場合、複数の等式に分割されることを確認するテスト。
    a=b=c
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
        Tree(ParserConst.root_data, [
            Tree(ParserConst.equal_data, [
                Token(ParserConst.token_type, 'a'),
                Token(ParserConst.token_type, 'b')
            ])
        ]),
        Tree(ParserConst.root_data, [
            Tree(ParserConst.equal_data, [
                Token(ParserConst.token_type, 'b'),
                Token(ParserConst.token_type, 'c')
            ])
        ]),
        Tree(ParserConst.root_data, [
            Tree(ParserConst.equal_data, [
                Token(ParserConst.token_type, 'c'),
                Token(ParserConst.token_type, 'a')
            ])
        ])
    ]
    assert actual == expected
