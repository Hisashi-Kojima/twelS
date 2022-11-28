# -*- coding: utf-8 -*-
"""test modules of functions.py.
"""

import pytest
from scrapy.http.response.html import HtmlResponse

from web_crawler.web_crawler.spiders import functions


@pytest.fixture
def response():
    with open('test_data/方程式 - Wikipedia.html') as f:
        body = f.read().encode()
    return HtmlResponse(url='local', body=body)


# tests

def test_get_lang_1(response):
    actual = functions.get_lang(response)
    expected = 'ja'
    assert actual == expected


def test_get_title_1(response):
    actual = functions.get_title(response)
    expected = '方程式 - Wikipedia'
    assert actual == expected


def test_render_katex_1():
    """KaTeXで書かれた数式がMathMLに変換されているか確認するテスト。
    <span></span>で囲まれている。
    """
    expr_katex = 'a+b'
    actual = functions.render_katex(expr_katex)
    assert '<math' in actual


def test_render_katex_2():
    """変換後の数式がきれいなMathMLになっているか確認するテスト。
    """
    expr_katex = 'a-b'
    actual = functions.render_katex(expr_katex)
    assert actual[:5] == '<math'


def test_render_katex_3():
    """$を含む数式がrenderできないことを確認するテスト。
    """
    expr_katex = '$a+b$'
    actual = functions.render_katex(expr_katex)
    assert '<math' not in actual


def test_render_katex_4():
    """長い数式がrenderできることを確認するテスト。
    """
    expr_katex = """
    \n\\begin{aligned}\n(\\sin x)' &= \\cos x\\\\\n(\\cos x)' &= -\\sin x\\\\\n(\\tan x)' &= \\dfrac{1}{\\cos^2 x}\\\\\n(\\mathrm{Arcsin}~ x)' &= \\dfrac{1}{\\sqrt{1-x^2}}\\\\\n(\\mathrm{Arccos}~ x)' &= -\\dfrac{1}{\\sqrt{1-x^2}}\\\\\n(\\mathrm{Arctan}~ x)' &= \\dfrac{1}{1+x^2}\\\\\n\\end{aligned}\n
    """
    actual = functions.render_katex(expr_katex)
    assert '<math' in actual


def test_render_katex_5():
    """長い数式がrenderできることを確認するテスト。
    """
    expr_katex = 'a-b\n'
    actual = functions.render_katex(expr_katex)
    assert '<math' in actual


def test_render_katex_page_1():
    """katexで書かれた数式を抽出してrenderできることの確認。
    $$のバージョン。
    """
    text = """test$$y_{1}とy_{2}$$foo"""
    actual = functions.render_katex_page(text)
    assert '$' not in actual
    assert '<math' in actual


def test_render_katex_page_2():
    """katexで書かれた数式を抽出してrenderできることの確認。
    $のバージョン。
    """
    text = """test$y_{1}とy_{2}$foo"""
    actual = functions.render_katex_page(text)
    assert '$' not in actual
    assert '<math' in actual


def test_render_katex_page_3():
    """katexで書かれた数式を抽出してrenderできることの確認。
    $のバージョン。
    """
    text = """三角関数の微分公式は
    $$\n\\begin{aligned}\n(\\sin x)' &= \\cos x\\\\\n(\\cos x)' &= -\\sin x\\\\\n(\\tan x)' &= \\dfrac{1}{\\cos^2 x}\\\\\n(\\mathrm{Arcsin}~ x)' &= \\dfrac{1}{\\sqrt{1-x^2}}\\\\\n(\\mathrm{Arccos}~ x)' &= -\\dfrac{1}{\\sqrt{1-x^2}}\\\\\n(\\mathrm{Arctan}~ x)' &= \\dfrac{1}{1+x^2}\\\\\n\\end{aligned}\n$$
    です。"""
    actual = functions.render_katex_page(text)
    assert '$' not in actual
    assert '<math' in actual


def test_render_katex_page_4():
    """katexで書かれた数式を抽出してrenderできることの確認。
    """
    text = """$$a+b$$"""
    actual = functions.render_katex_page(text)
    assert '$' not in actual
    assert '<math' in actual


def test_render_katex_page_5():
    """katexで書かれた数式を抽出してrenderできることの確認。
    数式の末尾に\nがあると失敗する。
    """
    text = """$$a+b\n$$"""
    actual = functions.render_katex_page(text)
    assert '$' not in actual
    assert '<math' in actual


def test_render_katex_page_6():
    """katexで書かれた数式を抽出してrenderできることの確認。
    """
    text = """どうして$y_{1}とy_{2}$に分ける必要があるのですか。
    覚えておくと便利な三角比の値\n\n\n$15^{\\circ}$\n や\n$18^{\\circ}$\n の三角比は，値そのもの（または導出方法）を覚えておくとよいでしょう。
    三角関数の微分公式は
    $$\n\\begin{aligned}\n(\\sin x)' &= \\cos x\\\\\n(\\cos x)' &= -\\sin x\\\\\n(\\tan x)' &= \\dfrac{1}{\\cos^2 x}\\\\\n(\\mathrm{Arcsin}~ x)' &= \\dfrac{1}{\\sqrt{1-x^2}}\\\\\n(\\mathrm{Arccos}~ x)' &= -\\dfrac{1}{\\sqrt{1-x^2}}\\\\\n(\\mathrm{Arctan}~ x)' &= \\dfrac{1}{1+x^2}\\\\\n\\end{aligned}\n$$
    です。
    """
    actual = functions.render_katex_page(text)
    assert '$' not in actual
    assert '<math' in actual
