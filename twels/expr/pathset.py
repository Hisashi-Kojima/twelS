# -*- coding: utf-8 -*-
"""module description
"""

from lark import Token, Tree

from twels.expr.parser_const import ParserConst


class PathSet(set):
    """数式のpathの集合
    引数を2つ以上とる関数では引数の順番の情報を保持している。
    Path rules:
        1. 引数の順番（pseudo num: #1など）で終わらない。
        2. negがあるときにはnegなしのpathは記録しない。
    """

    def __init__(self, tree: Tree):
        fix, tmp = _visit_leaf(tree)
        fix.extend(tmp)
        super().__init__(_delete_invalid_paths(fix))


def _visit_leaf(node: Tree | Token) -> tuple[list[str], list[str]]:
    """rootからleafまで探索してpath_listを作成する関数。
    Returns:
        fix: 新たなpathの作成に使わないpath_list。
        tmp: 新たなpathの作成に使うかもしれないpath_list。いずれfix_listに移動する。
    """
    if type(node) is Tree:
        fix = []
        tmp = []
        for child in node.children:
            child_fix, child_tmp = _visit_leaf(child)
            if node.data in ParserConst.relational_operators:
                pass
            else:
                fix.extend(child_fix)
                for path in child_tmp:
                    tmp.append(f'{path}/{node.data}')
                    # Path rule 1.
                    if node.data != ParserConst.neg_data:
                        fix.append(path)
        return fix, tmp
    else:
        return [], [node.value]


def _delete_invalid_paths(path_list: list[str]) -> list[str]:
    """引数の順番（pseudo num: #1など）で終わるpathを削除する関数。
    ex.
    before
    [
        '2', '2/#0/', '2/#0/frac', '2/#0/frac/root',
        '3', '3/#1/', '3/#1/frac', '3/#1/frac/root'
    ]

    after
    [
        '2', '2/#0/frac', '2/#0/frac/root',
        '3', '3/#1/frac', '3/#1/frac/root'
    ]
    """
    result_list = []
    for path in path_list:
        value_list = path.split('/')
        # node.dataで'#'から始まる文字列はpseudo num。
        # Path rule 2.
        if value_list[-1][0] != '#':
            result_list.append(path)
    return result_list
