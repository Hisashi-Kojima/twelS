# -*- coding: utf-8 -*-
"""module description
made by Hisashi
"""

from typing import Tuple

from lark import Token, Tree

from constant.const import Const


# 2/negのとき，2で止まったら困る．
# 1/#1/fracのとき，1/#1で止まったら困る．
skip_list = ['neg']
skip_list.extend(Const.need_args)


def get_path_set(tree: Tree) -> set:
    """Path Setを取得する関数．
    Returns:
        fix: Path Set.
    """
    tmp, fix = _collect_path_set(tree)
    fix.extend(tmp)
    return set(fix)


def _collect_path_set(node) -> Tuple[list[str], list[str]]:
    """子ノードを調べてPath Setを集める関数．
    Args:
        node: 木のノード．Tree型，Token型，list型のどれかをとる．
    Returns:
        tmp: まだ確定していないPath Set．いずれfixに移動する．これから新たなPathが生まれることがある．
        fix: 確定したPath Set．
    """
    if type(node) is Tree:
        return _collect_path_set_from_tree(node)
    elif type(node) is Token:
        return [node.value], []  # tmp, fix
    else:
        # listであれば，要素ごとに_collect_path_set()を実行して，tmpとfixに統合する
        tmp = []
        fix = []
        for nd in node:
            t, f = _collect_path_set(nd)
            tmp.extend(t)
            fix.extend(f)
        return tmp, fix


def _collect_path_set_from_tree(node: Tree) -> Tuple[list[str], list[str]]:
    """引数のノードの子ノードそれぞれで_collect_path_set()を実行し，
    それぞれのfixとtmpをまとめる関数．
    Returns:
        (tmp, fix):
            tmp: まだ確定していないPath Set．いずれfixに移動する．これから新たなPathが生まれることがある．
            fix: 確定したPath Set．
    """
    tmp = []
    fix = []
    for child in node.children:
        child_tmp, child_fix = _collect_path_set(child)

        fix.extend(child_fix)
        _skip_some_paths(node.data, fix, child_tmp)

        for child_data in child_tmp:
            tmp.append(f'{child_data}/{node.data}')
    return tmp, fix


def _skip_some_paths(node_data: str, fix: list[str], child_tmp: list[str]):
    """登録したくないpathをスキップする関数
    Args:
        node_data: そのノードが保持する演算子等のデータ．
        fix: 確定したPath Set．
        child_tmp: 子ノードから得られたPath Set．登録したければfixに追加する．
    """
    if node_data not in skip_list:
        fix.extend(child_tmp)
