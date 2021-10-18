# -*- coding: utf-8 -*-
"""module description
made by Hisashi
"""

from add_path import add_path
add_path()

from lark import Tree, Token
import latex2mathml.converter

from constant.const import Const

from expr.tree import MathMLTree
from expr.parser import get_lark_parser


def test_mathmlTree_1():
    """cdotsのテスト"""
    parser = get_lark_parser()
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML">
                    <semantics>
                        <mrow class="MJX-TeXAtom-ORD">
                        <mstyle displaystyle="true" scriptlevel="0">
                            <mn>0.999</mn>
                            <mo>&#x22EF;<!-- ⋯ --></mo>
                        </mstyle>
                        </mrow>
                    </semantics>
                </math>"""
    parsed_tree = parser.parse(mathml)
    cleaned_tree = MathMLTree().transform(parsed_tree)
    expected = Tree(Const.root_data, [
        Tree(Const.omit_data, [Token(Const.token_type, '0.9')])
        ])
    assert expected == cleaned_tree


def test_mathmlTree_2():
    """cdotsのテスト"""
    parser = get_lark_parser()
    mathml = latex2mathml.converter.convert('0.999\cdots ')
    parsed_tree = parser.parse(mathml)
    cleaned_tree = MathMLTree().transform(parsed_tree)
    expected = Tree(Const.root_data, [
        Tree(Const.omit_data, [Token(Const.token_type, '0.9')])
        ])
    assert expected == cleaned_tree
