# -*- coding: utf-8 -*-
"""module description
"""

from lark import Transformer, Tree, Token

from twels.expr.parser_const import ParserConst
from twels.normalizer.normalizer import Normalizer


class MathMLTree(Transformer):
    """MathMLのいらないノードや葉を削除するためのクラス．"""

    # functions
    def frac(self, nodes: list):
        return Tree('frac', _insert_pseudo_num(nodes))

    def sup(self, nodes: list):
        return Tree('sup', _insert_pseudo_num(nodes))

    def sub(self, nodes: list):
        return Tree('sub', _insert_pseudo_num(nodes))

    def subsup(self, nodes: list):
        return Tree('subsup', _insert_pseudo_num(nodes))

    def root(self, nodes: list):
        return Tree('root', _insert_pseudo_num(nodes))

    def over(self, nodes: list):
        return Tree('over', _insert_pseudo_num(nodes))

    def under(self, nodes: list):
        return Tree('under', _insert_pseudo_num(nodes))

    def underover(self, nodes: list):
        return Tree('underover', _insert_pseudo_num(nodes))

    def slash(self, nodes: list):
        return Token(ParserConst.token_type, ParserConst.slash_data)

    # do more complicated tasks
    def start(self, nodes: list):
        """root直下のchild nodeがexprだったときにexprのノードを削除する関数．"""
        if len(nodes) == 1 and type(nodes[0]) is Tree and nodes[0].data == ParserConst.expr_data:
            return Tree(ParserConst.root_data, nodes[0].children)
        return Tree(ParserConst.root_data, nodes)

    def sum(self, nodes: list):
        """sumの子ノードを整理する関数．
        subtractを見つけたら，次のノードの符号を逆にする．
        """
        return _get_tree_of(ParserConst.sum_data, nodes, 'subtract', _get_negative)

    def product(self, nodes: list):
        """productの子ノードを整理する関数．
        divを見つけたら，次のノードの数を逆数にする．
        cdotsを見つけたら，正規化する．
        """
        return _get_tree_of(ParserConst.product_data, nodes, 'div', _get_reciprocal)

    def table(self, nodes: list[Tree]):
        """tableの要素に引数の順番の情報を付与してtr,tdを削除する関数。
        Args:
        ex.
        [
            Tree('tr', [
                Tree('td', [Token('TOKEN', 'A')]),
                Tree('td', [Token('TOKEN', 'B')])
            ]),
            Tree('tr', [
                Tree('td', [Token('TOKEN', 'C')]),
                Tree('td', [Token('TOKEN', 'D')])
            ]),
            Tree('tr', [
                Tree('td', [Token('TOKEN', 'E')]),
                Tree('td', [Token('TOKEN', 'F')])
            ])
        ]

        Returns:
        ex.
        [
            Tree('#0', [
                Tree('#0', [Token('TOKEN', 'A')]),
                Tree('#1', [Token('TOKEN', 'B')])
            ]),
            Tree('#1', [
                Tree('#0', [Token('TOKEN', 'C')]),
                Tree('#1', [Token('TOKEN', 'D')])
            ]),
            Tree('#2', [
                Tree('#0', [Token('TOKEN', 'E')]),
                Tree('#1', [Token('TOKEN', 'F')])
            ])
        ]
        """
        table: list[Tree] = []
        tr_num = len(nodes)
        for i in range(tr_num):
            table.append(_get_tr(nodes[i], i))
        return Tree(ParserConst.table_data, table)

    def expr(self, children: list):
        """
        Tree(ParserConst.expr_data, [
            Token(ParserConst.token_type, 'i'),
            Tree(ParserConst.equal_data, []),
            Token(ParserConst.token_type, '1')
        ])
        を
        Tree(ParserConst.equal_data, [
                Token(ParserConst.token_type, 'i'),
                Token(ParserConst.token_type, '1')
            ])
        に変形する。
        """
        ro_index_list = get_ro_index(children)

        if len(ro_index_list) == 1 and ro_index_list[0] == 1 and len(children) == 3:
            # ROが1つのとき，ROのchildrenに左辺と右辺を入れる．
            # remove ParserConst.root_data
            ro_tree = children[ro_index_list[0]]
            if ro_tree.data in ParserConst.ro_commutative:
                return Tree(ro_tree.data, [
                    children[0],
                    children[2]
                ])
            elif ro_tree.data in ParserConst.ro_non_commutative:
                return Tree(ro_tree.data, [
                    Tree('#0', [children[0]]),
                    Tree('#1', [children[2]])
                ])
            else:
                return Tree(ParserConst.expr_data, children)
        else:
            return Tree(ParserConst.expr_data, children)

    def __default__(self, data, children, meta):
        """Default funciton that is called if there is no attribute matching 'data'."""
        return Tree(data, children, meta)


# ************** functions ******************
def get_ro_index(children: list) -> list[int]:
    """Treeのchildrenに含まれるrelational operatorのindexのリストを返す関数．
    """
    result = []
    for i, child in enumerate(children):
        if (isinstance(child, Tree)) and (child.data in ParserConst.relational_operators):
            result.append(i)
    return result


def _insert_pseudo_num(nodes: list) -> list:
    """引数の順番の情報を追加する関数"""
    return [_get_pseudo_tree(i, node) for i, node in enumerate(nodes)]


def _get_tree_of(operator: str, nodes: list, sign: str, get_func) -> Tree:
    """sum()やproduct()で使う関数．
    Args:
        operator: sumやproductなど．
        nodes: ノードのリスト．要素はTreeまたはToken.
        sign: subtractやdivなど．
        get_func: 途中で呼び出す関数．
    """
    new_nodes = []
    i = iter(nodes)
    try:
        while True:
            node = next(i)
            if type(node) is Tree:
                if node.data == sign:
                    new_nodes.append(get_func(next(i)))
                elif node.data == ParserConst.cdots_data and operator == ParserConst.product_data:
                    # 直前の値を取り出して正規化
                    num_token = new_nodes.pop()
                    result = Normalizer.normalize_num(num_token)
                    new_nodes.append(Tree(ParserConst.omit_data, [result]))
                else:
                    new_nodes.append(node)
            else:
                new_nodes.append(node)
    except StopIteration:
        # tryの処理で子ノードが1つになったらスキップする
        node = _skip_this_node(new_nodes)
        if node:
            return node
        else:
            return Tree(operator, new_nodes)


def _get_negative(node):
    """符号を逆にして返す関数．
    Args:
        node:
            Tree('neg', [a Tree or a Token])
            or Tree('foo', [foo])
            or Token('foo', 'foo')
    """
    if type(node) is Tree and node.data == ParserConst.neg_data:
        # negを外して返す．
        return node.children[0]
    else:
        return Tree(ParserConst.neg_data, [node])


def _get_reciprocal(node) -> Tree:
    """逆数を返す関数．
    Args:
        node: Tree or Token.
    """
    if type(node) is Tree and node.data == ParserConst.frac_data:
        # 入れ替える．
        tmp: list = node.children[0].children
        node.children[0].children = node.children[1].children
        node.children[1].children = tmp
        return node
    else:
        # 3 -> frac{1}{3}のパターン．
        return _get_fraction(1, node)


def _get_pseudo_tree(pseudo_num: int, node: Tree | Token) -> Tree:
    """引数の順番の情報を追加する関数．"""
    return Tree(f'#{pseudo_num}', [node])


def _get_pseudo_tree_wrapper(pseudo_num: int, arg) -> Tree:
    """引数がintのときにはToken()でwrapして_get_pseudo_tree()を呼ぶ関数．"""
    if type(arg) is int:
        return _get_pseudo_tree(pseudo_num, Token(ParserConst.token_type, str(arg)))
    elif type(arg) is Tree or type(arg) is Token:
        return _get_pseudo_tree(pseudo_num, arg)
    else:
        raise ValueError('引数には，int型, Tree型, Token型のいずれかを渡してください．')


def _get_fraction(numerator, denominator) -> Tree:
    """分数を作成して返す関数．
    Args:
        numerator(int or Tree or Token): 分子．
        denominator(int or Tree or Token): 分母．
    """
    nodes = []
    nodes.append(_get_pseudo_tree_wrapper(0, numerator))
    nodes.append(_get_pseudo_tree_wrapper(1, denominator))
    return Tree(ParserConst.frac_data, nodes)


def _get_tr(tr: Tree, pseudo_num: int) -> Tree:
    """引数の順番の情報を追加したtrを返す関数。
    Args:
        ex.
        Tree('tr', [
            Tree('td', [Token('TOKEN', 'A')]),
            Tree('td', [Token('TOKEN', 'B')])
        ])

    Returns:
        ex.
        Tree('#0', [
            Tree('#0', [Token('TOKEN', 'A')]),
            Tree('#1', [Token('TOKEN', 'B')])
        ])
    """
    children: list[Tree] = []
    td_num = len(tr.children)
    for i in range(td_num):
        td: Tree = tr.children[i]
        token: Token = td.children[0]
        children.append(_get_pseudo_tree(i, token))
    return Tree(f'#{pseudo_num}', children)


def _skip_this_node(nodes: list):
    if len(nodes) == 1:
        # skip this element.
        # just return child Token or Tree.
        return nodes[0]
    else:
        return False
