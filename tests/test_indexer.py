# -*- coding: utf-8 -*-
"""module description
"""

import json

from itemadapter import ItemAdapter

from twels.database.cursor import Cursor
from twels.expr.expression import Expression
from twels.expr.parser import Parser
from twels.indexer.indexer import Indexer
from twels.indexer.info import Info
from twels.snippet.snippet import Snippet
from web_crawler.web_crawler.items import Page

# Indexerのメソッド内のCursor.connect()と競合しないように，
# ここでは@pytest.fixtureではなくCursor.connect()を用いることで，
# connectした状態でIndexerのmethodを呼ばないようにする．


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


def test_update_page_table_1():
    """Indexer._update_page_table()のテスト．
    新規登録の場合．
    """
    try:
        uri_1 = 'uri_1'
        title = 'title'
        snippet = Snippet('snippet')
        lang = 'ja'
        mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                        <mrow>
                            <mn>1</mn>
                            <mo>+</mo>
                            <mn>2</mn>
                        </mrow>
                    </math>"""
        exprs = [Expression(mathml)]

        page_item_1 = Page(uri=uri_1, title=title, snippet=snippet, lang=lang, exprs=exprs)
        page_info_1 = ItemAdapter(page_item_1)

        actual_uri_id, actual_registered_exprs = Indexer._update_page_table(page_info_1, test=True)

        with Cursor.connect(test=True) as cnx:
            with Cursor.cursor(cnx) as cursor:
                cursor.execute('SELECT uri_id FROM page WHERE uri = %s', (uri_1,))
                expected_uri_id = cursor.fetchone()[0]

        assert actual_uri_id == expected_uri_id
        assert actual_registered_exprs == set()

    finally:
        reset_tables()


def test_update_page_table_2():
    """Indexer._update_page_table()のテスト．
    uriがすでに登録されている場合．
    """
    try:
        # register old page info
        uri = 'uri'
        old_title = 'title'
        old_snippet = Snippet('snippet')
        old_mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                            <mrow>
                                <mn>1</mn>
                                <mo>+</mo>
                                <mn>2</mn>
                            </mrow>
                        </math>"""
        old_exprs = [Expression(old_mathml)]

        with Cursor.connect(test=True) as cnx:
            with Cursor.cursor(cnx) as cursor:
                Cursor.insert_into_page_values_1_2_3_4(cursor, uri, old_exprs, old_title, old_snippet)
            cnx.commit()

        # new page info
        new_title = 'new title'
        new_snippet = Snippet('new snippet')
        new_lang = 'en'  # lang is unnecessary for page table.
        new_mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                            <mrow>
                                <mn>5</mn>
                                <mo>+</mo>
                                <mn>8</mn>
                            </mrow>
                        </math>"""
        new_exprs = [Expression(new_mathml)]

        page_new_item = Page(uri=uri, title=new_title, snippet=new_snippet, lang=new_lang, exprs=new_exprs)
        page_new_info = ItemAdapter(page_new_item)

        uri_id, registered_exprs = Indexer._update_page_table(page_new_info, test=True)
        with Cursor.connect(test=True) as cnx:
            with Cursor.cursor(cnx) as cursor:
                actual = Cursor.select_all_from_page_where_uri_id_1(cursor, uri_id)

        actual_title = actual[3]
        actual_snippet = actual[4]
        assert registered_exprs == set(old_exprs)
        assert actual_title == new_title
        assert actual_snippet == new_snippet.text

    finally:
        reset_tables()


def test_update_index_and_path_table_1():
    """Indexer._update_index_and_path_table()のテスト．
    """
    try:
        uri_1 = 'uri_1'
        title = 'title'
        body = """
        <math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
            <mrow>
                <mn>1</mn>
                <mo>+</mo>
                <mn>2</mn>
            </mrow>
        </math>は数式です。
        """
        snippet = Snippet(body)
        lang = 'ja'
        mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                        <mrow>
                            <mn>1</mn>
                            <mo>+</mo>
                            <mn>2</mn>
                        </mrow>
                    </math>"""
        expr = Expression(mathml)
        exprs = [expr]

        page_item_1 = Page(uri=uri_1, title=title, snippet=snippet, lang=lang, exprs=exprs)
        page_info_1 = ItemAdapter(page_item_1)

        # page tableへの登録
        uri_id, registered_exprs = Indexer._update_page_table(page_info_1, test=True)
        assert registered_exprs == set()

        Indexer._update_index_and_path_table(uri_id, registered_exprs, page_info_1, test=True)

        with Cursor.connect(test=True) as cnx:
            with Cursor.cursor(cnx) as cursor:
                cursor.execute('SELECT * FROM inverted_index WHERE expr = %s', (expr.mathml,))
                inverted_index_result = cursor.fetchone()
                cursor.execute('SELECT expr_path FROM path_dictionary')
                path_dict_result = cursor.fetchall()

        expr_id = inverted_index_result[0]
        actual_expr = inverted_index_result[1]
        actual_expr_len = inverted_index_result[2]
        actual_info = Info(json.loads(inverted_index_result[4]))
        actual_paths = set([path_dict_result[i][0] for i in range(len(path_dict_result))])

        expr_start_pos_list = [
            [0]
        ]
        expected_info = Info({
            'uri_id': [str(uri_id)],
            'lang': [lang],
            'expr_start_pos': expr_start_pos_list
        })
        expected_paths = Parser.parse(expr)

        assert type(expr_id) == int
        assert actual_expr == expr.mathml
        assert actual_expr_len == len(expr.mathml)
        assert str(actual_info) == str(expected_info)
        assert actual_paths == expected_paths

    finally:
        reset_tables()


def test_update_index_and_path_table_2():
    """Indexer._update_index_and_path_table()のテスト．
    数式を2種類登録する場合。
    """
    try:
        uri_1 = 'uri_1'
        title = 'title'
        body = """
        <math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
            <mrow>
                <mn>1</mn>
                <mo>+</mo>
                <mn>2</mn>
            </mrow>
        </math>は数式です。
        """
        snippet = Snippet(body)
        lang = 'ja'
        mathml1 = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                        <mrow>
                            <mn>1</mn>
                            <mo>+</mo>
                            <mn>2</mn>
                        </mrow>
                    </math>"""
        expr1 = Expression(mathml1)
        exprs1 = [expr1]

        page_item_1 = Page(uri=uri_1, title=title, snippet=snippet, lang=lang, exprs=exprs1)
        page_info_1 = ItemAdapter(page_item_1)

        # page tableへの登録
        uri_id, registered_exprs = Indexer._update_page_table(page_info_1, test=True)
        assert registered_exprs == set()

        Indexer._update_index_and_path_table(uri_id, registered_exprs, page_info_1, test=True)

        uri_2 = 'uri_2'
        mathml2 = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                        <mrow>
                            <mn>8</mn>
                            <mo>-</mo>
                            <mn>5</mn>
                        </mrow>
                    </math>"""
        expr2 = Expression(mathml2)
        exprs2 = [expr2]
        page_item_2 = Page(uri=uri_2, title=title, snippet=snippet, lang=lang, exprs=exprs2)
        page_info_2 = ItemAdapter(page_item_2)

        # page tableへの登録
        uri_id, registered_exprs = Indexer._update_page_table(page_info_2, test=True)
        assert registered_exprs == set()

        Indexer._update_index_and_path_table(uri_id, registered_exprs, page_info_2, test=True)

        with Cursor.connect(test=True) as cnx:
            with Cursor.cursor(cnx) as cursor:
                cursor.execute(
                    'SELECT expr_path, expr_size FROM path_dictionary',
                    )
                path_dict_result = cursor.fetchall()

        expected = [
            ('1', 4), ('1/sum', 4),
            ('2', 4), ('2/sum', 4),
            ('5/neg', 4), ('5/neg/sum', 4),
            ('8', 4), ('8/sum', 4)
            ]

        assert path_dict_result == expected

    finally:
        reset_tables()


def test_update_index_and_path_table_3():
    """Indexer._update_index_and_path_table()のテスト．
    <mspace>を含むMathMLがエラーにならないことを確認。
    """
    try:
        uri_1 = 'uri_1'
        title = 'title'
        lang = 'ja'
        mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML"  alttext="{\displaystyle {\frac {\;{\dfrac {a}{b}}\;}{\;{\dfrac {c}{d}}\;}}}">
                        <semantics>
                            <mrow class="MJX-TeXAtom-ORD">
                            <mstyle displaystyle="true" scriptlevel="0">
                                <mrow class="MJX-TeXAtom-ORD">
                                <mfrac>
                                    <mrow>
                                    <mspace width="thickmathspace" />
                                    <mrow class="MJX-TeXAtom-ORD">
                                        <mstyle displaystyle="true" scriptlevel="0">
                                        <mfrac>
                                            <mi>a</mi>
                                            <mi>b</mi>
                                        </mfrac>
                                        </mstyle>
                                    </mrow>
                                    <mspace width="thickmathspace" />
                                    </mrow>
                                    <mrow>
                                    <mspace width="thickmathspace" />
                                    <mrow class="MJX-TeXAtom-ORD">
                                        <mstyle displaystyle="true" scriptlevel="0">
                                        <mfrac>
                                            <mi>c</mi>
                                            <mi>d</mi>
                                        </mfrac>
                                        </mstyle>
                                    </mrow>
                                    <mspace width="thickmathspace" />
                                    </mrow>
                                </mfrac>
                                </mrow>
                            </mstyle>
                            </mrow>
                            <annotation encoding="application/x-tex">{\displaystyle {\frac {\;{\dfrac {a}{b}}\;}{\;{\dfrac {c}{d}}\;}}}</annotation>
                        </semantics>
                    </math>"""
        body = f"""
        {mathml}は数式です。
        """
        snippet = Snippet(body)
        expr = Expression(mathml)
        exprs = [expr]

        page_item_1 = Page(uri=uri_1, title=title, snippet=snippet, lang=lang, exprs=exprs)
        page_info_1 = ItemAdapter(page_item_1)

        # page tableへの登録
        uri_id, registered_exprs = Indexer._update_page_table(page_info_1, test=True)
        assert registered_exprs == set()

        Indexer._update_index_and_path_table(uri_id, registered_exprs, page_info_1, test=True)

        with Cursor.connect(test=True) as cnx:
            with Cursor.cursor(cnx) as cursor:
                cursor.execute('SELECT * FROM inverted_index WHERE expr = %s', (expr.mathml,))
                inverted_index_result = cursor.fetchone()
                cursor.execute('SELECT expr_path FROM path_dictionary')
                path_dict_result = cursor.fetchall()

        expr_id = inverted_index_result[0]
        actual_expr = inverted_index_result[1]
        actual_expr_len = inverted_index_result[2]
        actual_info = Info(json.loads(inverted_index_result[4]))
        actual_paths = set([path_dict_result[i][0] for i in range(len(path_dict_result))])

        expr_start_pos_list = [
            [0]
        ]
        expected_info = Info({
            'uri_id': [str(uri_id)],
            'lang': [lang],
            'expr_start_pos': expr_start_pos_list
        })
        expected_paths = Parser.parse(expr)

        assert type(expr_id) == int
        assert actual_expr == expr.mathml
        assert actual_expr_len == len(expr.mathml)
        assert str(actual_info) == str(expected_info)
        assert actual_paths == expected_paths

    finally:
        reset_tables()


def test_update_db_1():
    """Indexer.update_db()のテスト．
    inverted_index tableについて，あるexpr_idで複数のuri_idが登録されるか確認するテスト．
    """
    try:
        uri_1 = 'uri_1'
        title = 'title'
        body = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                        <mrow>
                            <mn>1</mn>
                            <mo>+</mo>
                            <mn>2</mn>
                        </mrow>
                    </math>は数式です。"""
        snippet1 = Snippet(body)
        lang = 'ja'
        mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                        <mrow>
                            <mn>1</mn>
                            <mo>+</mo>
                            <mn>2</mn>
                        </mrow>
                    </math>"""
        expr = Expression(mathml)
        exprs = [expr]

        page_item_1 = Page(uri=uri_1, title=title, snippet=snippet1, lang=lang, exprs=exprs)
        page_info_1 = ItemAdapter(page_item_1)
        assert Indexer.update_db(page_info_1, test=True)

        uri_2 = 'uri_2'
        snippet2 = Snippet(f'文章。{body}')
        page_item_2 = Page(uri=uri_2, title=title, snippet=snippet2, lang=lang, exprs=exprs)
        page_info_2 = ItemAdapter(page_item_2)
        assert Indexer.update_db(page_info_2, test=True)

        with Cursor.connect(test=True) as cnx:
            with Cursor.cursor(cnx) as cursor:
                # uri_idの取得
                cursor.execute('SELECT uri_id FROM page WHERE uri = %s', (uri_1,))
                uri_id_1 = str(cursor.fetchone()[0])
                cursor.execute('SELECT uri_id FROM page WHERE uri = %s', (uri_2,))
                uri_id_2 = str(cursor.fetchone()[0])

                # infoの取得
                cursor.execute('SELECT info FROM inverted_index')  # どうせ1つしかないからWHEREは使わない．
                actual_info = Info(json.loads(cursor.fetchone()[0]))

                cursor.execute('SELECT * from path_dictionary')
                actual_path_dict = cursor.fetchall()

        expr_start_pos_list = [
            [0],
            [3]
        ]

        expected_info = Info({
            'uri_id': [uri_id_1, uri_id_2],
            'lang': ['ja', 'ja'],
            'expr_start_pos': expr_start_pos_list
        })
        assert str(actual_info) == str(expected_info)
        assert len(actual_path_dict) == 4
    finally:
        reset_tables()


def test_update_db_2():
    """Indexer.update_db()のテスト．
    1回目の登録では数式が含まれていたが、2回目の登録では数式が含まれていない場合。
    そのページがデータベースから削除されていることを確認。
    """
    try:
        uri = 'https://example.com'
        title = 'title'
        body = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                        <mrow>
                            <mn>1</mn>
                            <mo>+</mo>
                            <mn>2</mn>
                        </mrow>
                    </math>は数式です。"""
        snippet1 = Snippet(body)
        lang = 'ja'
        mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                        <mrow>
                            <mn>1</mn>
                            <mo>+</mo>
                            <mn>2</mn>
                        </mrow>
                    </math>"""
        expr = Expression(mathml)
        exprs = [expr]

        page_item_1 = Page(uri=uri, title=title, snippet=snippet1, lang=lang, exprs=exprs)
        page_info_1 = ItemAdapter(page_item_1)
        assert Indexer.update_db(page_info_1, test=True)

        # ページが登録されていることの確認。
        query = 'SELECT uri_id FROM page WHERE uri = %s'
        with Cursor.connect(test=True) as cnx:
            with Cursor.cursor(cnx) as cursor:
                cursor.execute(query, (uri,))
                uri_id = cursor.fetchone()[0]
        assert isinstance(uri_id, int)

        new_exprs = []
        snippet2 = Snippet(f'文章。{body}')
        page_item_2 = Page(uri=uri, title=title, snippet=snippet2, lang=lang, exprs=new_exprs)
        page_info_2 = ItemAdapter(page_item_2)
        assert Indexer.update_db(page_info_2, test=True)

        # ページが削除されていることの確認。
        with Cursor.connect(test=True) as cnx:
            with Cursor.cursor(cnx) as cursor:
                cursor.execute('SELECT COUNT(*) FROM page')
                page_num = cursor.fetchone()[0]
        assert page_num == 0
    finally:
        reset_tables()


def test_get_insert_and_delete_set_1():
    """Indexer._get_insert_and_delete_set()のテスト．
    """
    new_exprs = {'expr1', 'expr2'}
    registered_exprs = set()
    insert_set, delete_set = Indexer._get_insert_and_delete_set(new_exprs, registered_exprs)
    assert insert_set == new_exprs
    assert delete_set == set()
