# -*- coding: utf-8 -*-
"""module description
"""

from itemadapter import ItemAdapter
import pytest

from tests.functions import reset_tables
from twels.expr.expression import Expression
from twels.indexer.indexer import Indexer
from twels.searcher.searcher import Searcher
from twels.snippet.snippet import Snippet
from web_crawler.web_crawler.items import Page


def test_search_1():
    """ギリシャ文字θが検索できることを確認するテスト。
    &#x03B8;と&#x003B8;を同じものとして扱えないとこのテストは通らない。
    """
    try:
        uri_1 = 'uri_1'
        title = 'title'
        mathml = r"""<math xmlns="http://www.w3.org/1998/Math/MathML"  alttext="{\displaystyle \theta }">
                        <semantics>
                            <mrow class="MJX-TeXAtom-ORD">
                            <mstyle displaystyle="true" scriptlevel="0">
                                <mi>&#x03B8;<!-- θ --></mi>
                            </mstyle>
                            </mrow>
                            <annotation encoding="application/x-tex">{\displaystyle \theta }</annotation>
                        </semantics>
                    </math>"""
        body = f'{mathml}はギリシャ文字の1つです。'
        snippet1 = Snippet(body)
        lang = 'ja'

        exprs = [Expression(mathml)]

        page_item_1 = Page(uri=uri_1, title=title, snippet=snippet1, lang=lang, exprs=exprs)
        page_info_1 = ItemAdapter(page_item_1)
        assert Indexer.update_db(page_info_1, test=True)

        lr_list = ['ja']
        search_result = Searcher.search("\\theta ", 0, lr_list, test=True)['search_result']
        assert len(search_result) == 1

    finally:
        reset_tables()


def test_search_2():
    """実際の記事で検索できることを確認。
    """
    try:
        with open('test_data/モジュラー曲線 - Wikipedia.html') as f:
            body = f.read()

        snippet = Snippet(body)
        uri = 'uri_1'
        title = 'title'
        lang = 'ja'
        mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML"  alttext="{\displaystyle {\begin{pmatrix}a&amp;-m\\c&amp;n\end{pmatrix}}}">
                        <semantics>
                            <mrow class="MJX-TeXAtom-ORD">
                            <mstyle displaystyle="true" scriptlevel="0">
                                <mrow class="MJX-TeXAtom-ORD">
                                <mrow>
                                    <mo>(</mo>
                                    <mtable rowspacing="4pt" columnspacing="1em">
                                    <mtr>
                                        <mtd>
                                        <mi>a</mi>
                                        </mtd>
                                        <mtd>
                                        <mo>&#x2212;<!-- − --></mo>
                                        <mi>m</mi>
                                        </mtd>
                                    </mtr>
                                    <mtr>
                                        <mtd>
                                        <mi>c</mi>
                                        </mtd>
                                        <mtd>
                                        <mi>n</mi>
                                        </mtd>
                                    </mtr>
                                    </mtable>
                                    <mo>)</mo>
                                </mrow>
                                </mrow>
                            </mstyle>
                            </mrow>
                            <annotation encoding="application/x-tex">{\displaystyle {\begin{pmatrix}a&amp;-m\\c&amp;n\end{pmatrix}}}</annotation>
                        </semantics>
                    </math>"""
        expr = Expression(mathml)
        exprs = [expr]

        page_item_1 = Page(uri=uri, title=title, snippet=snippet, lang=lang, exprs=exprs)
        page_info_1 = ItemAdapter(page_item_1)
        assert Indexer.update_db(page_info_1, test=True)

        lr_list = ['ja']
        actual = Searcher.search(r'\begin{pmatrix}a&-m\\c&n\end{pmatrix}', 0, lr_list, test=True)
        assert expr.mathml in actual['search_result'][0]['snippet']
    finally:
        reset_tables()


def test_search_3():
    """検索結果数が0件のときにFalseが帰ってくることを確認するテスト。
    """
    mathml = '<math><mn>1</mn></math>'
    expr = Expression(mathml)
    actual = Searcher.search(expr, 0, ['ja'], test=True)
    assert len(actual['search_result']) == 0
    assert actual['has_next'] is False


def test_search_4():
    """検索結果数が9件のときにhas_nextがFalseであることを確認するテスト。
    """
    try:
        page_num = Searcher.search_num - 1
        number = '1'
        mathml = f'<math><mn>{number}</mn></math>'
        body = f'{mathml}は数字の1つです。'
        snippet = Snippet(body)
        lang = 'ja'

        exprs = [Expression(mathml)]

        for i in range(page_num):
            uri = f'uri_{i}'
            title = f'title_{i}'
            page_item = Page(uri=uri, title=title, snippet=snippet, lang=lang, exprs=exprs)
            assert Indexer.update_db(ItemAdapter(page_item), test=True)

        lr_list = [lang]
        actual = Searcher.search(number, 0, lr_list, test=True)
        assert len(actual['search_result']) == page_num
        assert actual['has_next'] is False

    finally:
        reset_tables()


def test_search_5():
    """検索結果数が10件のときにhas_nextがFalseであることを確認するテスト。
    """
    try:
        page_num = Searcher.search_num
        number = '1'
        mathml = f'<math><mn>{number}</mn></math>'
        body = f'{mathml}は数字の1つです。'
        snippet = Snippet(body)
        lang = 'ja'

        exprs = [Expression(mathml)]

        for i in range(page_num):
            uri = f'uri_{i}'
            title = f'title_{i}'
            page_item = Page(uri=uri, title=title, snippet=snippet, lang=lang, exprs=exprs)
            assert Indexer.update_db(ItemAdapter(page_item), test=True)

        lr_list = [lang]
        actual = Searcher.search(number, 0, lr_list, test=True)
        assert len(actual['search_result']) == page_num
        assert actual['has_next'] is False

    finally:
        reset_tables()


def test_search_6():
    """検索結果数が11件のときにhas_nextがTrueであることを確認するテスト。
    """
    try:
        page_num = Searcher.search_num + 1
        number = '1'
        mathml = f'<math><mn>{number}</mn></math>'
        body = f'{mathml}は数字の1つです。'
        snippet = Snippet(body)
        lang = 'ja'

        exprs = [Expression(mathml)]

        for i in range(page_num):
            uri = f'uri_{i}'
            title = f'title_{i}'
            page_item = Page(uri=uri, title=title, snippet=snippet, lang=lang, exprs=exprs)
            assert Indexer.update_db(ItemAdapter(page_item), test=True)

        lr_list = [lang]
        actual = Searcher.search(number, 0, lr_list, test=True)
        assert len(actual['search_result']) == Searcher.search_num
        assert actual['has_next'] is True

    finally:
        reset_tables()


def test_search_7():
    """登録数が9件、start=9のときにhas_nextがFalseであることを確認するテスト。
    """
    try:
        page_num = 9
        number = '1'
        mathml = f'<math><mn>{number}</mn></math>'
        body = f'{mathml}は数字の1つです。'
        snippet = Snippet(body)
        lang = 'ja'

        exprs = [Expression(mathml)]

        for i in range(page_num):
            uri = f'uri_{i}'
            title = f'title_{i}'
            page_item = Page(uri=uri, title=title, snippet=snippet, lang=lang, exprs=exprs)
            assert Indexer.update_db(ItemAdapter(page_item), test=True)

        lr_list = [lang]
        actual = Searcher.search(number, page_num, lr_list, test=True)
        assert len(actual['search_result']) == 0
        assert actual['has_next'] is False

    finally:
        reset_tables()


def test_search_8():
    """同じ検索結果が2回以上表示されないことを確認するテスト。
    '1+2+3'がページ中の'1+2+3'と'1+2+4'のどちらにもヒットしたときに、
    同じページが2回表示されないことを確認する。
    """
    try:
        mathml_1 = """<math>
                        <mn>1</mn>
                        <mo>+</mo>
                        <mn>2</mn>
                        <mo>+</mo>
                        <mn>3</mn>
                      </math>"""
        mathml_2 = """<math>
                        <mn>1</mn>
                        <mo>+</mo>
                        <mn>2</mn>
                        <mo>+</mo>
                        <mn>4</mn>
                      </math>"""

        body = f'{mathml_1}や{mathml_2}は数式です。'
        snippet = Snippet(body)
        lang = 'ja'
        expr_1 = Expression(mathml_1)
        expr_2 = Expression(mathml_2)

        exprs = [expr_1, expr_2]

        uri = 'uri_1'
        title = 'title_1'
        page_item = Page(uri=uri, title=title, snippet=snippet, lang=lang, exprs=exprs)
        assert Indexer.update_db(ItemAdapter(page_item), test=True)

        lr_list = [lang]
        actual = Searcher.search('1+2+3', 0, lr_list, test=True)
        assert len(actual['search_result']) == 1

    finally:
        reset_tables()


@pytest.mark.parametrize('test_input, expected', [
    ("not expressions.", False),
    ('1+2', True),
    (r'\pi ', True),
    (r'\alpha + \beta', True),
    ('a-b', True),
    ('1', True),
    ('123456789', True),
    ('-77', True),
    ('8y', True),
    ('y=ax+b', True),
    ('a*b', True),
    ('1/2', True),
    ('1<b', True),
    ('10>d', True),
    ('方程式', False),
    ('e^x', True),
    ('Kubernetes', False)
])
def test_is_expr_1(test_input, expected):
    """入力が数式かどうかを判別する関数のテスト。"""
    assert Searcher._is_expr(test_input) == expected
