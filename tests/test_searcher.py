# -*- coding: utf-8 -*-
"""module description
"""

from itemadapter import ItemAdapter

from twels.database.cursor import Cursor
from twels.expr.expression import Expression
from twels.indexer.indexer import Indexer
from twels.searcher.searcher import Searcher
from twels.snippet.snippet import Snippet
from web_crawler.web_crawler.items import Page


def reset_tables():
    """tableのレコードをすべて削除する関数．
    try-finallyを使って，必ずtestの最後に呼び出すことでtableを常に同じ状態に保つ．
    このファイルのテストはデータベースの中にレコードがない状態で開始．
    """
    with Cursor.connect(test=True) as cnx:
        with Cursor.cursor(cnx) as cursor:
            cursor.execute('TRUNCATE TABLE inverted_index')
            cursor.execute('TRUNCATE TABLE page')
            cursor.execute('TRUNCATE TABLE path_dictionary')


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
