# -*- coding: utf-8 -*-
"""module description
"""

from lark import Tree, Token
import latex2mathml.converter

from twels.expr.expression import Expression
from twels.expr.tree import MathMLTree
from twels.expr.parser import get_lark_parser
from twels.expr.parser_const import ParserConst


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
    expr = Expression(mathml)
    parsed_tree = parser.parse(expr.mathml)
    cleaned_tree = MathMLTree().transform(parsed_tree)
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.omit_data, [Token(ParserConst.token_type, '0.9')])
        ])
    assert expected == cleaned_tree


def test_mathmlTree_2():
    """cdotsのテスト"""
    parser = get_lark_parser()
    mathml = latex2mathml.converter.convert(r'0.999\cdots ')
    expr = Expression(mathml)
    parsed_tree = parser.parse(expr.mathml)
    cleaned_tree = MathMLTree().transform(parsed_tree)
    expected = Tree(ParserConst.root_data, [
        Tree(ParserConst.omit_data, [Token(ParserConst.token_type, '0.9')])
        ])
    assert expected == cleaned_tree
