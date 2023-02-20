# -*- coding: utf-8 -*-
"""module description
"""

import os

from lark import Lark, exceptions, Tree

from twels.expr.pathset import PathSet
from twels.expr.parser_const import ParserConst
from twels.expr.tree import MathMLTree
from twels.utils.utils import print_in_red


def get_lark_parser() -> Lark | None:
    """Lark parserを返す関数．
    """
    base_path = os.path.abspath(__file__)  # parser.pyのpath
    path = os.path.normpath(os.path.join(base_path, '../mathml.lark'))
    try:
        with open(path, encoding='utf-8') as _grammar:
            return Lark(_grammar, parser='earley')
    except exceptions.GrammarError as e:
        print_in_red(e)
    except FileNotFoundError as e:
        print_in_red(e)


class Parser:
    """MathMLを解析するためのクラス．"""
    _lark = get_lark_parser()

    @staticmethod
    def parse(mathml: str) -> set[str]:
        """MathMLを解析する関数．
        Returns:
            PathSet: mathmlを解析して得られたPath Set.
        """
        tree = __class__.get_parsed_tree(mathml)
        if tree.data == 'error':
            # 他のexceptionにしたほうがいいかも．
            raise exceptions.LarkError('parse中にエラーが発生しました．')

        # relational operatorを複数含む式を分割
        tree_list = __class__._make_new_trees(tree)
        # TODO: 1つの式を複数の式に分割したときに，それぞれにexpr_idを割り当てなくてよいのか考える．
        result = set()
        for t in tree_list:
            result = result.union(PathSet(t))
        return result

    @staticmethod
    def get_parsed_tree(mathml: str) -> Tree:
        """MathMLを分析してTreeを作成する関数．
        例外が発生した場合はTree('error', [])を返す．
        """
        try:
            parsed_tree = __class__._lark.parse(mathml)
            cleaned_tree = MathMLTree().transform(parsed_tree)
            return cleaned_tree
        except AttributeError as e:
            print_in_red('AttributeError')
            print_in_red(e)
            print_in_red('grammarファイルを正しく読み込めていない，もしくはgrammarに間違いがあります．')
            return Tree('error', [])
        except exceptions.LarkError as e:
            print_in_red('LarkError')
            print_in_red(e)
            # logger.exception(e)
            return Tree('error', [])

    @staticmethod
    def _make_new_trees(tree: Tree) -> list[Tree]:
        """relational operatorを複数含む式を分割して返す関数．
        relational operatorを含まない場合は，ParserConst.root_dataを削除して返す．
        TODO:
            equal以外のrelational operatorにも対応する．
            rootの孫以降にrelational operatorがある場合はどうなるのか確かめる．
        Returns:
            tree_list
        Note:
            ParserConst.root_dataはpath_setには入れたくないので、
            ParserConst.root_dataを含まないTreeを返す。
        """
        ro_index_list = __class__._get_ro_index(tree)
        if len(ro_index_list) == 0:
            # remove ParserConst.root_data
            return [tree.children[0]]

        tree_list = []

        if len(ro_index_list) == 1 and ro_index_list[0] == 1 and len(tree.children) == 3:
            # ROが1つのとき，ROのchildrenに左辺と右辺を入れる．
            # remove ParserConst.root_data
            ro_tree = tree.children[ro_index_list[0]]
            if ro_tree.data in ParserConst.ro_commutative:
                new_tree = Tree(ro_tree.data, [
                    tree.children[0],
                    tree.children[2]
                ])
                tree_list.append(new_tree)
            elif ro_tree.data in ParserConst.ro_non_commutative:
                new_tree = Tree(ro_tree.data, [
                    Tree('#0', [tree.children[0]]),
                    Tree('#1', [tree.children[2]])
                ])
                tree_list.append(new_tree)
        else:
            # TODO: ここの実装．
            # TODO: remove ParserConst.root_data
            tree_list.append(tree)
        return tree_list

    @staticmethod
    def _get_ro_index(tree: Tree) -> list[int]:
        """tree.childrenに含まれるrelational operatorのindexのリストを返す関数．
        """
        result = []
        for i, child in enumerate(tree.children):
            if (isinstance(child, Tree)) and (child.data in ParserConst.relational_operators):
                result.append(i)
        return result
