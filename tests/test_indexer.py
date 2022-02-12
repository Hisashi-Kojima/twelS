# -*- coding: utf-8 -*-
"""module description
made by Hisashi
"""

import json

from itemadapter import ItemAdapter

from wiki_crawler.wiki_crawler.items import Page
from twels.database.cursor import Cursor
from twels.indexer.indexer import Indexer
from twels.expr.parser import Parser

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


def test_check_expr_id_1():
    """Indexer._check_expr_id()のテスト．
    未登録の数式の場合にはinverted_indexに登録する．
    """
    try:
        mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                        <mrow>
                            <mn>1</mn>
                            <mo>&#x0002B;</mo>
                            <mn>2</mn>
                        </mrow>
                    </math>"""
        query = 'SELECT * FROM inverted_index'
        uri_id = 1
        lang = 'ja'

        with Cursor.connect(test=True) as cnx:
            with Cursor.cursor(cnx) as cursor:
                cursor.execute(query)
                first = cursor.fetchone()
        assert first is None

        expr_id_1, was_registered = Indexer._check_expr_id(mathml, uri_id, lang, test=True)
        assert was_registered is False

        with Cursor.connect(test=True) as cnx:
            with Cursor.cursor(cnx) as cursor:
                cursor.execute(query)
                expr_id_2, result_expr, info_str = cursor.fetchone()

        assert result_expr == mathml
        assert json.loads(info_str) == {'uri_id': ['1'], 'lang': ['ja']}
        assert expr_id_1 == expr_id_2

    finally:
        reset_tables()


def test_check_expr_id_2():
    """Indexer._check_expr_id()のテスト．
    登録済みの数式の場合にはinverted_indexを更新．
    """
    try:
        mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                        <mrow>
                            <mn>1</mn>
                            <mo>&#x0002B;</mo>
                            <mn>2</mn>
                        </mrow>
                    </math>"""
        query = 'SELECT * FROM inverted_index'
        uri_id = 1
        lang = 'ja'

        with Cursor.connect(test=True) as cnx:
            with Cursor.cursor(cnx) as cursor:
                cursor.execute(query)
                first = cursor.fetchone()
        assert first is None

        expr_id_1, was_registered = Indexer._check_expr_id(mathml, uri_id, lang, test=True)
        assert was_registered is False

        expr_id_2, was_registered = Indexer._check_expr_id(mathml, uri_id, 'en', test=True)
        assert expr_id_1 == expr_id_2
        assert was_registered is True

        with Cursor.connect(test=True) as cnx:
            with Cursor.cursor(cnx) as cursor:
                cursor.execute(query)
                expr_id_3, result_expr, info_str = cursor.fetchone()

        assert json.loads(info_str) == {'uri_id': ['1'], 'lang': ['en']}

    finally:
        reset_tables()


def test_update_index_table_1():
    """Indexer._update_index_table()のテスト．
    """
    try:
        uri_id = 2
        expr =   """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                        <mrow>
                            <mn>1</mn>
                            <mo>&#x0002B;</mo>
                            <mn>2</mn>
                        </mrow>
                    </math>"""
        with Cursor.connect(test=True) as cnx:
            with Cursor.cursor(cnx) as cursor:
                cursor.execute(
                    'INSERT INTO inverted_index (expr, info) VALUES (%s, JSON_OBJECT("uri_id", JSON_ARRAY(%s, %s, %s), "lang", JSON_ARRAY(%s, %s, %s)))',
                    (expr, "1", str(uri_id), "7", "ja", "ja", "ja")
                    )
                expr_id = Cursor.select_expr_id_from_inverted_index_where_expr_1(cursor, expr)
            cnx.commit()

        assert expr_id is not None

        lang = 'en'
        # Indexer._update_index_table()のテスト．
        with Cursor.connect(test=True) as cnx:
            with Cursor.cursor(cnx) as cursor:
                Indexer._update_index_table(cursor, uri_id, lang, expr_id)
                actual = Cursor.select_all_from_index_where_expr_id_1(cursor, expr_id)

        actual_expr_id = actual[0]
        actual_expr = actual[1]
        actual_info = json.loads(actual[2])

        expected_info = {'uri_id': ['1', str(uri_id), '7'], 'lang': ['ja', lang, 'ja']}

        assert actual_expr == expr
        assert actual_info == expected_info

    finally:
        reset_tables()


def test_update_page_table_1():
    """Indexer._update_page_table()のテスト．
    新規登録の場合．
    """
    try:
        uri_1 = 'uri_1'
        title = 'title'
        snippet = 'snippet'
        lang = 'ja'
        expr =   """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                        <mrow>
                            <mn>1</mn>
                            <mo>&#x0002B;</mo>
                            <mn>2</mn>
                        </mrow>
                    </math>"""
        exprs = [expr]

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
        old_snippet = 'snippet'
        old_expr =   """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                        <mrow>
                            <mn>1</mn>
                            <mo>&#x0002B;</mo>
                            <mn>2</mn>
                        </mrow>
                    </math>"""
        old_exprs = [old_expr]

        with Cursor.connect(test=True) as cnx:
            with Cursor.cursor(cnx) as cursor:
                Cursor.insert_into_page_values_1_2_3_4(cursor, uri, old_exprs, old_title, old_snippet)
            cnx.commit()

        # new page info
        new_title = 'new title'
        new_snippet = 'new snippet'
        new_lang = 'en'  # lang is unnecessary for page table.
        new_expr =   """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                        <mrow>
                            <mn>5</mn>
                            <mo>&#x0002B;</mo>
                            <mn>8</mn>
                        </mrow>
                    </math>"""
        new_exprs = [new_expr]

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
        assert actual_snippet == new_snippet

    finally:
        reset_tables()


def test_update_index_and_path_table_1():
    """Indexer._update_index_and_path_table()のテスト．
    """
    try:
        uri_1 = 'uri_1'
        title = 'title'
        snippet = 'snippet'
        lang = 'ja'
        expr =   """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                        <mrow>
                            <mn>1</mn>
                            <mo>&#x0002B;</mo>
                            <mn>2</mn>
                        </mrow>
                    </math>"""
        exprs = [expr]

        page_item_1 = Page(uri=uri_1, title=title, snippet=snippet, lang=lang, exprs=exprs)
        page_info_1 = ItemAdapter(page_item_1)

        # page tableへの登録
        uri_id, registered_exprs = Indexer._update_page_table(page_info_1, test=True)
        assert registered_exprs == set()

        Indexer._update_index_and_path_table(uri_id, registered_exprs, page_info_1, test=True)

        with Cursor.connect(test=True) as cnx:
            with Cursor.cursor(cnx) as cursor:
                cursor.execute('SELECT * FROM inverted_index WHERE expr = %s', (expr,))
                inverted_index_result = cursor.fetchone()
                cursor.execute('SELECT expr_path FROM path_dictionary')
                path_dict_result = cursor.fetchall()
        expr_id = inverted_index_result[0]
        actual_expr = inverted_index_result[1]
        actual_info = json.loads(inverted_index_result[2])
        actual_paths = set([path_dict_result[i][0] for i in range(len(path_dict_result))])
        expected_info = {'uri_id': [str(uri_id)], 'lang': [lang]}
        expected_paths = Parser.parse(expr)
        assert type(expr_id) == int
        assert actual_expr == expr
        assert actual_info == expected_info
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
        snippet = 'snippet'
        lang = 'ja'
        expr =   """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                        <mrow>
                            <mn>1</mn>
                            <mo>&#x0002B;</mo>
                            <mn>2</mn>
                        </mrow>
                    </math>"""
        exprs = [expr]

        page_item_1 = Page(uri=uri_1, title=title, snippet=snippet, lang=lang, exprs=exprs)
        page_info_1 = ItemAdapter(page_item_1)
        assert Indexer.update_db(page_info_1, test=True) == True

        uri_2 = 'uri_2'
        page_item_2 = Page(uri=uri_2, title=title, snippet=snippet, lang=lang, exprs=exprs)
        page_info_2 = ItemAdapter(page_item_2)
        assert Indexer.update_db(page_info_2, test=True) == True

        with Cursor.connect(test=True) as cnx:
            with Cursor.cursor(cnx) as cursor:
                # uri_idの取得
                cursor.execute('SELECT uri_id FROM page WHERE uri = %s', (uri_1,))
                uri_id_1 = str(cursor.fetchone()[0])
                cursor.execute('SELECT uri_id FROM page WHERE uri = %s', (uri_2,))
                uri_id_2 = str(cursor.fetchone()[0])

                # infoの取得
                cursor.execute('SELECT info FROM inverted_index')  # どうせ1つしかないからWHEREは使わない．
                result = json.loads(cursor.fetchone()[0])

        assert result == {'uri_id': [uri_id_1, uri_id_2], 'lang': ['ja', 'ja']}
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
