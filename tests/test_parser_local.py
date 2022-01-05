# -*- coding: utf-8 -*-
"""this file has tests for functions not implemented.
made by Hisashi
"""

import latex2mathml.converter
from lark import Tree, Token

from twels.expr.parser import Parser
from twels.constant.const import Const


def test_get_parsed_tree_mspace_1():
    """
    mspaceを含む式
    参考ページ：跡（線形代数学）
    https://ja.wikipedia.org/wiki/%E8%B7%A1_(%E7%B7%9A%E5%9E%8B%E4%BB%A3%E6%95%B0%E5%AD%A6)
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML"  alttext="{\displaystyle B(x,y)=\operatorname {tr} (\operatorname {ad} (x)\operatorname {ad} (y))\qquad (\operatorname {ad} (x)y:=[x,y]=xy-yx)}">
                    <semantics>
                        <mrow class="MJX-TeXAtom-ORD">
                        <mstyle displaystyle="true" scriptlevel="0">
                            <mi>B</mi>
                            <mo stretchy="false">(</mo>
                            <mi>x</mi>
                            <mo>,</mo>
                            <mi>y</mi>
                            <mo stretchy="false">)</mo>
                            <mo>=</mo>
                            <mi>tr</mi>
                            <mo>&#x2061;<!-- ⁡ --></mo>
                            <mo stretchy="false">(</mo>
                            <mi>ad</mi>
                            <mo>&#x2061;<!-- ⁡ --></mo>
                            <mo stretchy="false">(</mo>
                            <mi>x</mi>
                            <mo stretchy="false">)</mo>
                            <mi>ad</mi>
                            <mo>&#x2061;<!-- ⁡ --></mo>
                            <mo stretchy="false">(</mo>
                            <mi>y</mi>
                            <mo stretchy="false">)</mo>
                            <mo stretchy="false">)</mo>
                            <mspace width="2em" />
                            <mo stretchy="false">(</mo>
                            <mi>ad</mi>
                            <mo>&#x2061;<!-- ⁡ --></mo>
                            <mo stretchy="false">(</mo>
                            <mi>x</mi>
                            <mo stretchy="false">)</mo>
                            <mi>y</mi>
                            <mo>:=</mo>
                            <mo stretchy="false">[</mo>
                            <mi>x</mi>
                            <mo>,</mo>
                            <mi>y</mi>
                            <mo stretchy="false">]</mo>
                            <mo>=</mo>
                            <mi>x</mi>
                            <mi>y</mi>
                            <mo>&#x2212;<!-- − --></mo>
                            <mi>y</mi>
                            <mi>x</mi>
                            <mo stretchy="false">)</mo>
                        </mstyle>
                        </mrow>
                        <annotation encoding="application/x-tex">{\displaystyle B(x,y)=\operatorname {tr} (\operatorname {ad} (x)\operatorname {ad} (y))\qquad (\operatorname {ad} (x)y:=[x,y]=xy-yx)}</annotation>
                    </semantics>
                </math>"""
    # TODO: expectedの実装
    expected = False
    assert expected == Parser.get_parsed_tree(mathml)


def test_get_parsed_tree_table_2():
    """行列のparse
    [  1 9 -13]
    [ 20 5  -6]
    """
    mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML"  alttext="{\displaystyle {\begin{bmatrix}1&amp;9&amp;-13\\20&amp;5&amp;-6\end{bmatrix}}}">
                    <semantics>
                        <mrow class="MJX-TeXAtom-ORD">
                            <mstyle displaystyle="true" scriptlevel="0">
                                <mrow class="MJX-TeXAtom-ORD">
                                <mrow>
                                    <mo>[</mo>
                                    <mtable rowspacing="4pt" columnspacing="1em">
                                    <mtr>
                                        <mtd>
                                        <mn>1</mn>
                                        </mtd>
                                        <mtd>
                                        <mn>9</mn>
                                        </mtd>
                                        <mtd>
                                        <mo>&#x2212;<!-- − --></mo>
                                        <mn>13</mn>
                                        </mtd>
                                    </mtr>
                                    <mtr>
                                        <mtd>
                                        <mn>20</mn>
                                        </mtd>
                                        <mtd>
                                        <mn>5</mn>
                                        </mtd>
                                        <mtd>
                                        <mo>&#x2212;<!-- − --></mo>
                                        <mn>6</mn>
                                        </mtd>
                                    </mtr>
                                    </mtable>
                                    <mo>]</mo>
                                </mrow>
                                </mrow>
                            </mstyle>
                        </mrow>
                        <annotation encoding="application/x-tex">{\displaystyle {\begin{bmatrix}1&amp;9&amp;-13\\20&amp;5&amp;-6\end{bmatrix}}}</annotation>
                    </semantics>
                </math>"""
    # TODO: expectedの実装．
    expected = False
    assert expected == Parser.get_parsed_tree(mathml)
