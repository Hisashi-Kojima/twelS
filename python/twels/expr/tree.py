# -*- coding: utf-8 -*-
"""module description
"""

from lark import Transformer, Tree, Token, Discard

from twels.expr.parser_const import ParserConst
from twels.normalizer.normalizer import Normalizer


class MathMLTree(Transformer):
    """MathMLのいらないノードや葉を削除するためのクラス。"""

    # functions
    def frac(self, children: list[Tree | Token]):
        return Tree('frac', _insert_pseudo_num(children))

    def sup(self, children: list[Tree | Token]):
        return Tree('sup', _insert_pseudo_num(children))

    def sub(self, children: list[Tree | Token]):
        return Tree('sub', _insert_pseudo_num(children))

    def subsup(self, children: list[Tree | Token]):
        return Tree('subsup', _insert_pseudo_num(children))

    def root(self, children: list[Tree | Token]):
        return Tree('root', _insert_pseudo_num(children))

    def over(self, children: list[Tree | Token]):
        return Tree('over', _insert_pseudo_num(children))

    def under(self, children: list[Tree | Token]):
        return Tree('under', _insert_pseudo_num(children))

    def underover(self, children: list[Tree | Token]):
        return Tree('underover', _insert_pseudo_num(children))

    def slash(self, children: list[Tree | Token]):
        return Token(ParserConst.token_type, ParserConst.slash_data)

    def summation(self, children: list[Tree | Token]):
        return Tree('summation', _insert_pseudo_num(children))

    def product_of_seq(self, children: list[Tree | Token]):
        return Tree('product_of_seq', _insert_pseudo_num(children))

    def integral(self, children: list[Tree | Token]):
        return Tree('integral', _insert_pseudo_num(children))

    def lim(self, children: list[Tree | Token]):
        return Tree('lim', _insert_pseudo_num(children))

    def log(self, children: list[Tree | Token]):
        return Tree('log', _insert_pseudo_num(children))

    def log_less(self, children: list[Tree | Token]):
        # len(children) == 1
        # '#0'ではなく'#1'にしたかったので_insert_pseudo_num()を使っていない。
        return Tree('log', [Tree('#1', children)])

    def ln(self, children: list[Tree | Token]):
        return Tree('log', [
            Tree('#0', [Token(ParserConst.token_type, 'e')]),
            Tree('#1', children)
        ])

    def atom(self, children: list[Tree | Token]):
        # len(children) is 0 or more than 1.
        if len(children) == 0:
            raise Discard
        else:
            return Tree(ParserConst.atom_data, children)

    def matrix(self, children: list[Tree | Token]):
        """
        Args:
        e.g.
        Tree('matrix', [Tree('table', table_children)])

        Returns:
        e.g.
        Tree('matrix', table_children)
        """
        table_children = children[0].children
        return Tree(ParserConst.matrix_data, table_children)

    def lsup(self, children: list[Tree | Token]):
        return Tree(ParserConst.lsup_data, _insert_pseudo_num([children[1], children[0]]))

    def lsub(self, children: list[Tree | Token]):
        return Tree(ParserConst.lsub_data, _insert_pseudo_num([children[1], children[0]]))

    def abbr_add(self, children: list[Tree | Token]):
        return _parse_abbr(ParserConst.abbr_add_data, children)

    def abbr_mul(self, children: list[Tree | Token]):
        return _parse_abbr(ParserConst.abbr_mul_data, children)

    # do more complicated tasks
    def start(self, children: list[Tree | Token]):
        """root直下のchild nodeがexprだったときにexprのノードを削除する関数。"""
        if len(children) == 1 and type(children[0]) is Tree and children[0].data == ParserConst.expr_data:
            return Tree(ParserConst.root_data, children[0].children)
        return Tree(ParserConst.root_data, children)

    def sum(self, children: list[Tree | Token]):
        """sumの子ノードを整理する関数。
        subtractを見つけたら、次のノードの符号を逆にする。
        """
        return _get_tree_of(ParserConst.sum_data, children, 'subtract', _get_negative)

    def product(self, children: list[Tree | Token]):
        """productの子ノードを整理する関数。
        divを見つけたら、次のノードの数を逆数にする。
        cdotsを見つけたら、正規化する。
        """
        return _get_tree_of(ParserConst.product_data, children, 'div', _get_reciprocal)

    def table(self, children: list[Tree]):
        """tableの要素に引数の順番の情報を付与してtr,tdを削除する関数。
        Args:
        e.g.
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
        e.g.
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
        tr_num = len(children)
        for i in range(tr_num):
            table.append(_get_tr(children[i], i))
        return Tree(ParserConst.table_data, table)

    def expr(self, children: list[Tree | Token]):
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
        ro_index_list = find_index(children, ParserConst.relational_operators)

        if len(ro_index_list) == 1 and ro_index_list[0] == 1 and len(children) == 3:
            # ROが1つのとき，ROのchildrenに左辺と右辺を入れる．
            # remove ParserConst.root_data
            ro_tree = children[1]
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
        elif len(ro_index_list) == 1 and ro_index_list[0] == 0 and len(children) == 2:
            # equalの要素が1つしかないときなど
            ro_tree = children[0]
            return Tree(ro_tree.data, [children[1]])
        else:
            return Tree(ParserConst.expr_data, children)

    def __default__(self, data, children: list[Tree | Token], meta):
        """Default funciton that is called if there is no attribute matching 'data'."""
        return Tree(data, children, meta)


# ************** functions ******************
def find_index(children: list[Tree | Token], conditions: list[str]) -> list[int]:
    """childrenに含まれるconditionsのindexのリストを返す関数。
    """
    result = []
    for i, child in enumerate(children):
        if (isinstance(child, Tree)) and (child.data in conditions):
            result.append(i)
    return result


def _insert_pseudo_num(children: list[Tree | Token]) -> list:
    """引数の順番の情報を追加する関数"""
    return [_get_pseudo_tree(i, node) for i, node in enumerate(children)]


def _get_tree_of(operator: str, children: list[Tree | Token], sign: str, get_func) -> Tree:
    """sum()やproduct()で使う関数。
    Args:
        operator: sumやproductなど。
        children: ノードのリスト。要素はTreeまたはToken.
        sign: subtractやdivなど。
        get_func: 途中で呼び出す関数。
    """
    new_children = []
    i = iter(children)
    try:
        while True:
            node = next(i)
            if type(node) is Tree:
                if node.data == sign:
                    new_children.append(get_func(next(i)))
                elif node.data == ParserConst.cdots_data and operator == ParserConst.product_data:
                    # 直前の値を取り出して正規化
                    num_token = new_children.pop()
                    result = Normalizer.normalize_num(num_token)
                    new_children.append(Tree(ParserConst.omit_data, [result]))
                else:
                    new_children.append(node)
            else:
                new_children.append(node)
    except StopIteration:
        # tryの処理で子ノードが1つになったらスキップする
        node = _skip_this_node(new_children)
        if node:
            return node
        else:
            return Tree(operator, new_children)


def _get_negative(node: Tree | Token):
    """符号を逆にして返す関数。
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


def _get_reciprocal(node: Tree | Token) -> Tree:
    """逆数を返す関数。
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
    """引数の順番の情報を追加する関数。"""
    return Tree(f'#{pseudo_num}', [node])


def _get_pseudo_tree_wrapper(pseudo_num: int, arg) -> Tree:
    """引数がintのときにはToken()でwrapして_get_pseudo_tree()を呼ぶ関数。"""
    if type(arg) is int:
        return _get_pseudo_tree(pseudo_num, Token(ParserConst.token_type, str(arg)))
    elif type(arg) is Tree or type(arg) is Token:
        return _get_pseudo_tree(pseudo_num, arg)
    else:
        raise ValueError('引数には，int型, Tree型, Token型のいずれかを渡してください．')


def _get_fraction(numerator, denominator) -> Tree:
    """分数を作成して返す関数。
    Args:
        numerator(int or Tree or Token): 分子．
        denominator(int or Tree or Token): 分母．
    """
    children = []
    children.append(_get_pseudo_tree_wrapper(0, numerator))
    children.append(_get_pseudo_tree_wrapper(1, denominator))
    return Tree(ParserConst.frac_data, children)


def _get_tr(tr: Tree, pseudo_num: int) -> Tree:
    """引数の順番の情報を追加したtrを返す関数。
    Notes:
        td may be empty.
        e.g. Tree('td', [])
    Args:
        e.g.
        Tree('tr', [
            Tree('td', [Token('TOKEN', 'A')]),
            Tree('td', [Token('TOKEN', 'B')])
        ])

    Returns:
        e.g.
        Tree('#0', [
            Tree('#0', [Token('TOKEN', 'A')]),
            Tree('#1', [Token('TOKEN', 'B')])
        ])
    """
    children: list[Tree] = []
    td_num = len(tr.children)
    for i in range(td_num):
        td: Tree = tr.children[i]
        if len(td.children) == 0:
            continue
        token: Token = td.children[0]
        children.append(_get_pseudo_tree(i, token))
    return Tree(f'#{pseudo_num}', children)


def _parse_abbr(data: str, children: list[Tree | Token]):
    """
    Args:
        data: abbr_add_data or abbr_mul_data.
        children: see the below example.
    e.g.
    [
        Tree('sub', [
            Tree('#0', [Token('TOKEN', 'x')]),
            Tree('#1', [Token('TOKEN', '1')])
        ]),
        Tree('sub', [
            Tree('#0', [Token('TOKEN', 'x')]),
            Tree('#1', [Token('TOKEN', '2')])
        ]),
        Tree('cdots', []),
        Tree('sub', [
            Tree('#0', [Token('TOKEN', 'x')]),
            Tree('#1', [Token('TOKEN', 'n')])
        ])
    ]

    Returns:
        [from, to, step]
    e.g.
    [
        // from
        Tree('#0', [
            Tree('sub', [
                Tree('#0', [Token(ParserConst.token_type, 'x')]),
                Tree('#1', [Token(ParserConst.token_type, '1')])
            ])
        ]),
        // to
        Tree('#1', [
            Tree('sub', [
                Tree('#0', [Token(ParserConst.token_type, 'x')]),
                Tree('#1', [Token(ParserConst.token_type, 'n')])
            ])
        ]),
        // step
        Tree('#2', [
            Token(ParserConst.token_type, '1')
        ])
    ]
    """
    if type(children[0]) is Token or children[0].data != ParserConst.sub_data:
        return Tree(data, children)
    else:
        cdots_index = find_index(children, [ParserConst.cdots_data])

        sub_tree_0: Tree = children[0]
        default_step = 1  # default value is 1.
        sub_tree_last = children[-1]
        new_children = [sub_tree_0, sub_tree_last]

        if len(cdots_index) != 1:
            return Tree(data, children)
        for i in range(cdots_index[0]):
            if children[i].children[0].children[0].value != sub_tree_last.children[0].children[0].value:
                return Tree(data, children)
            elif i == 0:
                continue
            else:
                now_value = int(children[i].children[1].children[0].value)
                last_value = int(children[i-1].children[1].children[0].value)
                if (now_value - last_value) != default_step:
                    new_children.append('unknown')
                    break
        if len(new_children) == 2:
            new_children.append(str(default_step))
        return Tree(data, _insert_pseudo_num(new_children))


def _skip_this_node(nodes: list):
    if len(nodes) == 1:
        # skip this element.
        # just return child Token or Tree.
        return nodes[0]
    else:
        return False
