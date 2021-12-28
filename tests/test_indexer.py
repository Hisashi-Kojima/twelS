# -*- coding: utf-8 -*-
"""module description
made by Hisashi
"""

import json

from itemadapter import ItemAdapter

from wiki_crawler.wiki_crawler.items import Page
from twelS.constant.const import Const
from twelS.database.cursor import Cursor
from twelS.indexer.indexer import Indexer
from twelS.expr.parser import Parser

# Indexerのメソッド内のCursor.connect()と競合しないように，
# ここでは@pytest.fixtureではなくCursor.connect()を用いることで，
# connectした状態でIndexerのmethodを呼ばないようにする．


def reset_tables():
    """tableのレコードをすべて削除する関数．
    try-finallyを使って，必ずtestの最後に呼び出すことでtableを常に同じ状態に保つ．
    """
    with Cursor.connect(test=True) as cnx:
        with Cursor.cursor(cnx) as cursor:
            cursor.execute('TRUNCATE TABLE expression')
            cursor.execute('TRUNCATE TABLE inverted_index')
            cursor.execute('TRUNCATE TABLE page')
            cursor.execute('TRUNCATE TABLE path_dictionary')


def test_get_expr_id_1():
    """Indexer._get_expr_id()のテスト．
    """
    try:
        mathml = """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                        <mrow>
                            <mn>1</mn>
                            <mo>&#x0002B;</mo>
                            <mn>2</mn>
                        </mrow>
                    </math>"""

        with Cursor.connect(test=True) as cnx:
            with Cursor.cursor(cnx) as cursor:
                cursor.execute('SELECT * FROM expression')
                first = cursor.fetchone()
        assert first is None

        expr_id = Indexer._get_expr_id(mathml, test=True)

        with Cursor.connect(test=True) as cnx:
            with Cursor.cursor(cnx) as cursor:
                cursor.execute('SELECT * FROM expression')
                result_expr, result_expr_id = cursor.fetchone()

        assert result_expr == mathml
        assert result_expr_id == expr_id

    finally:
        reset_tables()


def test_update_db_1():
    """Indexer.update_db()のテスト．
    inverted_index tableについて，あるexpr_idで複数のuri_idが登録されるか確認するテスト．
    """
    try:
        uri_1 = 'uri_1'
        title = 'title'
        descr = 'descr'
        lang = 'ja'
        expr =   """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                        <mrow>
                            <mn>1</mn>
                            <mo>&#x0002B;</mo>
                            <mn>2</mn>
                        </mrow>
                    </math>"""
        exprs = [expr]

        page_item_1 = Page(uri=uri_1, title=title, descr=descr, lang=lang, exprs=exprs)
        page_info_1 = ItemAdapter(page_item_1)
        assert Indexer.update_db(page_info_1, test=True) == True

        uri_2 = 'uri_2'
        page_item_2 = Page(uri=uri_2, title=title, descr=descr, lang=lang, exprs=exprs)
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


def test_update_index_and_path_table_1():
    """Indexer._get_insert_and_delete_set()のテスト．
    """
    new_exprs = {'expr1', 'expr2'}
    registered_exprs = set()
    insert_set, delete_set = Indexer._get_insert_and_delete_set(new_exprs, registered_exprs)
    assert insert_set == new_exprs
    assert delete_set == set()


def test_insert_expr_into_database_1():
    """Indexer._insert_expr_into_database()のテスト．
    同じ数式を違うuri_idで登録する．inverted_indexのinfoが正しいか確認．
    """
    try:
        expr_id = 1  # 任意の値
        uri_id_1 = 1  # 任意の値
        uri_id_2 = 2  # uri_id_1と被らない値
        lang = 'ja'
        expr =   """<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">
                        <mrow>
                            <mn>1</mn>
                            <mo>&#x0002B;</mo>
                            <mn>2</mn>
                        </mrow>
                    </math>"""
        expr_path_set = Parser.parse(expr)

        with Cursor.connect(test=True) as cnx:
            with Cursor.cursor(cnx) as cursor:
                Indexer._insert_expr_into_database(cursor, expr_path_set, expr_id, uri_id_1, lang)
                result_info = Indexer._insert_expr_into_database(cursor, expr_path_set, expr_id, uri_id_2, lang)

        assert result_info == {'uri_id': [str(uri_id_1), str(uri_id_2)], 'lang': ['ja', 'ja']}
    finally:
        reset_tables()
