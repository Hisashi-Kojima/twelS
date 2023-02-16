# -*- coding: utf-8 -*-
"""module description
"""

import os

from lark import Lark, exceptions, Tree

from twels.expr.pathset import PathSet
from twels.expr.tree import MathMLTree, get_ro_index
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
        Returns:
            tree_list
        Note:
            ParserConst.root_dataはpath_setには入れたくないので、
            ParserConst.root_dataを含まないTreeを返す。
            root以外のノードに関係演算子が複数含まれる場合は分割の対象外としている。
            Transformerでの実装が難しそうなので、これを対象にすることは難しそう。
        """
        ro_index_list = get_ro_index(tree.children)
        ro_num = len(ro_index_list)
        if ro_num < 2:
            # remove ParserConst.root_data
            return [tree.children[0]]

        tree_list = []
        # TODO: ここの実装
        # 関係演算子が複数含まれるので、分割する。
        tree_list.append(tree)
        return tree_list
