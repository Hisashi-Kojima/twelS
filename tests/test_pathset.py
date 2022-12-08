# -*- coding: utf-8 -*-
"""module description
"""

from lark import Tree, Token

from twels.expr.pathset import PathSet
from twels.expr.parser_const import ParserConst


def test_pathset_1():
    """正の数。
    """
    tree = Tree(ParserConst.root_data, [
        Token(ParserConst.token_type, '7')
    ])
    actual = PathSet(tree)

    root = ParserConst.root_data
    expected = {'7', f'7/{root}'}
    assert actual == expected


def test_pathset_2():
    """負の数。
    """
    tree = Tree(ParserConst.root_data, [
        Tree(ParserConst.neg_data, [Token(ParserConst.token_type, '5')])
    ])
    actual = PathSet(tree)

    root = ParserConst.root_data
    neg = ParserConst.neg_data
    expected = {f'5/{neg}', f'5/{neg}/{root}'}
    assert actual == expected


def test_pathset_frac_1():
    """分数。
    frac{2}{3}
    """
    tree = Tree(ParserConst.root_data, [
        Tree(ParserConst.frac_data, [
            Tree('#0', [Token(ParserConst.token_type, '2')]),
            Tree('#1', [Token(ParserConst.token_type, '3')])
        ])
    ])
    actual = PathSet(tree)

    root = ParserConst.root_data
    frac = ParserConst.frac_data
    expected = {
        '2', f'2/#0/{frac}', f'2/#0/{frac}/{root}',
        '3', f'3/#1/{frac}', f'3/#1/{frac}/{root}'
    }
    assert actual == expected


def test_pathset_sup_1():
    """上付き文字。
    e^{x}
    """
    tree = Tree(ParserConst.root_data, [
        Tree(ParserConst.sup_data, [
            Tree('#0', [Token(ParserConst.token_type, 'e')]),
            Tree('#1', [Token(ParserConst.token_type, 'x')])
        ])
    ])
    actual = PathSet(tree)

    root = ParserConst.root_data
    sup = ParserConst.sup_data
    expected = {
        'e', f'e/#0/{sup}', f'e/#0/{sup}/{root}',
        'x', f'x/#1/{sup}', f'x/#1/{sup}/{root}'
    }
    assert actual == expected


def test_pathset_eq_1():
    """等式。
    a=b

    Note:
        parser.get_parsed_tree()で作成した等式の木は、
        parser._make_new_trees()でparseしやすい形に変形してくれる。
    """
    tree = Tree(ParserConst.root_data, [
        Tree(ParserConst.equal_data, [
            Token(ParserConst.token_type, 'a'),
            Token(ParserConst.token_type, 'b')
        ]),
    ])
    actual = PathSet(tree)

    root = ParserConst.root_data
    equal = ParserConst.equal_data
    expected = {
        'a', f'a/{equal}', f'a/{equal}/{root}',
        'b', f'b/{equal}', f'b/{equal}/{root}'
        }
    assert actual == expected


def test_pathset_table_1():
    """行列。
    [  1 9 -13]
    [ 20 5  -6]
    """
    tree = Tree(ParserConst.root_data, [
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
    actual = PathSet(tree)

    root = ParserConst.root_data
    neg = ParserConst.neg_data
    product = ParserConst.product_data
    table = ParserConst.table_data

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
