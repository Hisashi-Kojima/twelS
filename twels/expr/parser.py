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
        Note:
            ParserConst.root_dataはpath_setには入れたくないので、
            ParserConst.root_dataを含まないTreeを返す。
        """
        if len(__class__._get_ro_index(tree)) == 0:
            # remove ParserConst.root_data
            return [tree.children[0]]

        result = []
        equal = Tree(ParserConst.equal_data, [])
        # 子にequalを1つ以上持つノードそれぞれを変形．
        for tree_having_ro in tree.find_pred(lambda t: equal in t.children):
            # ROの位置を得る
            index_list = __class__._get_ro_index(tree_having_ro)

            if len(index_list) == 1 and index_list[0] == 1 and len(tree_having_ro.children) == 3:
                # ROが1つのとき，ROのchildrenに左辺と右辺を入れる．
                # remove ParserConst.root_data
                new_tree = Tree(ParserConst.equal_data, [
                    tree_having_ro.children[0],
                    tree_having_ro.children[2],
                ])
                result.append(new_tree)
            else:
                # TODO: ここの実装．
                # TODO: remove ParserConst.root_data
                result.append(tree_having_ro)
        return result

    @staticmethod
    def _get_ro_index(tree: Tree) -> list[int]:
        """tree.childrenに含まれるrelational operatorのindexのリストを返す関数．
        TODO:
            equalをrelational operatorに拡張．
        """
        result = []
        for i, child in enumerate(tree.children):
            equal = Tree(ParserConst.equal_data, [])
            if child == equal:
                result.append(i)
        return result
