# -*- coding: utf-8 -*-
"""module description
made by Hisashi
"""

from lark import Lark

from expr.collector import get_path_set
from expr.tree import ChangeOperator, CheckEachNode


def parse(expr: str):
    """数式を解析する関数．
    Args:
        expr: 数式．
    """
    with open('expr/latex.lark', encoding='utf-8') as grammar:
        l = Lark(grammar)
        parse_tree = l.parse(expr)
        print(parse_tree.pretty())
        print(f'parse tree: {parse_tree}')
        print()

        tmp_tree = ChangeOperator().transform(parse_tree)
        new_tree = CheckEachNode().transform(tmp_tree)
        print('tree: ', new_tree)
        print(new_tree.pretty())
        print('path set: ', get_path_set(new_tree))
