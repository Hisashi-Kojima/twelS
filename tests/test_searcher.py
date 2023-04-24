# -*- coding: utf-8 -*-
"""module description
"""

from itemadapter import ItemAdapter

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
