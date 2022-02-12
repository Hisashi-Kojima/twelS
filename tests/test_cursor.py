import json
import traceback

import pytest
import mysql.connector

from twels.database.cursor import Cursor
from twels.utils.utils import print_in_red


@pytest.fixture
def cnx():
    """データベースに接続する関数．接続できたらちゃんとcloseしてくれる．
    """
    try:
        cnx = mysql.connector.connect(**Cursor.config_for_test)
        yield cnx
        # テスト後（成功時も失敗時も）にyield以降の処理が実行される
        cnx.rollback()  # テスト完了後にロールバックする．
        cnx.close()
    except mysql.connector.errors.InterfaceError:
        print(Cursor.config_for_test)
        print_in_red(traceback.format_exc())
        yield None


@pytest.fixture
def cursor(cnx):
    if cnx is not None:
        # TODO: 可能であればPrepared Statementにする．
        cursor = cnx.cursor()
        yield cursor
        cursor.close()
    else:
        yield None


# TODO: testをmulti processで実行したときにdeadlockになるので，それについて調べる．
# testでなくてもmulti processで実行すればdeadlockになると予想できる．
# multi process前提の処理にする必要があるだろう．


def test_connection_1(cursor):
    """データベースのテーブルにレコードがないことを確認．
    """
    query = "SELECT COUNT(*) FROM page"
    cursor.execute(query)
    assert cursor.fetchone()[0] == 0


def test_append_expr_id_if_not_registered_1(cursor):
    """Cursor.append_expr_id_if_not_registered()のテスト．
    path_dictionaryにexpr_pathがまだ登録されていない場合．
    """
    expr_id = 1
    expr_path = 'path1'

    select_query = 'SELECT expr_ids FROM path_dictionary WHERE expr_path = %s'

    cursor.execute(select_query, (expr_path,))
    assert cursor.fetchone() is None  # insert前

    Cursor.append_expr_id_if_not_registered(cursor, expr_id, expr_path)

    cursor.execute(select_query, (expr_path,))
    result = cursor.fetchone()
    result_expr_ids = json.loads(result[0])
    assert result_expr_ids == [str(expr_id)]


def test_append_expr_id_if_not_registered_2(cursor):
    """Cursor.append_expr_id_if_not_registered()のテスト．
    path_dictionaryにexpr_pathは登録されているが，expr_idが未登録の場合．
    """
    expr_id = 1
    other_expr_id = 2
    expr_path = 'path1'

    # expr_pathと他のexpr_idを登録．
    cursor.execute(
        'INSERT INTO path_dictionary (expr_path, expr_ids) VALUES (%s, %s)',
        (expr_path, json.dumps([str(other_expr_id)]))
        )

    select_query = 'SELECT expr_ids FROM path_dictionary WHERE expr_path = %s'

    cursor.execute(select_query, (expr_path,))
    assert cursor.fetchone() is not None  # expr_pathが登録されていることを確認

    Cursor.append_expr_id_if_not_registered(cursor, expr_id, expr_path)

    cursor.execute(select_query, (expr_path,))
    result_expr_ids = json.loads(cursor.fetchone()[0])
    assert result_expr_ids == [str(other_expr_id), str(expr_id)]


def test_append_expr_id_if_not_registered_3(cursor):
    """Cursor.append_expr_id_if_not_registered()のテスト．
    path_dictionaryにexpr_pathは登録されていて，expr_idも登録されている場合．
    重複して追加されていないことを確認．
    """
    expr_id = 1
    expr_path = 'path1'

    # expr_pathとexpr_idを登録．
    cursor.execute(
        'INSERT INTO path_dictionary (expr_path, expr_ids) VALUES (%s, %s)',
        (expr_path, json.dumps([str(expr_id)]))
        )

    select_query = 'SELECT expr_ids FROM path_dictionary WHERE expr_path = %s'

    cursor.execute(select_query, (expr_path,))
    assert cursor.fetchone() is not None  # expr_pathが登録されていることを確認

    Cursor.append_expr_id_if_not_registered(cursor, expr_id, expr_path)

    cursor.execute(select_query, (expr_path,))
    result = cursor.fetchone()
    result_expr_ids = json.loads(result[0])
    assert result_expr_ids == [str(expr_id)]


def test_delete_from_inverted_index_where_expr_1(cursor):
    """Cursor.delete_from_inverted_index_where_expr_1()のテスト．
    """
    expr = '<math>a</math>'
    cursor.execute(
        'INSERT INTO inverted_index (expr, info) VALUES (%s, JSON_OBJECT("uri_id", JSON_ARRAY(%s, %s), "lang", JSON_ARRAY(%s, %s)))',
        (expr, "1", "2", "ja", "ja")
        )

    select_query = 'SELECT * FROM inverted_index WHERE expr = %s'

    cursor.execute(select_query, (expr,))
    assert cursor.fetchone() is not None  # データが登録されていることを確認．

    Cursor.delete_from_inverted_index_where_expr_1(cursor, expr)

    cursor.execute(select_query, (expr,))
    assert cursor.fetchone() is None  # データが削除されていることを確認．


def test_delete_from_inverted_index_where_expr_id_1(cursor):
    """Cursor.delete_from_inverted_index_where_expr_id_1()のテスト．
    """
    expr = '<math>a</math>'
    cursor.execute(
        'INSERT INTO inverted_index (expr, info) VALUES (%s, JSON_OBJECT("uri_id", JSON_ARRAY(%s, %s), "lang", JSON_ARRAY(%s, %s)))',
        (expr, "1", "2", "ja", "ja")
        )

    select_query = 'SELECT * FROM inverted_index WHERE expr = %s'

    cursor.execute(select_query, (expr,))
    tpl = cursor.fetchone()
    # データが登録されていることを確認．
    expr_id: int = tpl[0]
    assert tpl[1] == expr

    Cursor.delete_from_inverted_index_where_expr_id_1(cursor, expr_id)

    cursor.execute(select_query, (expr,))
    assert cursor.fetchone() is None  # データが削除されていることを確認．


def test_delete_from_page_where_uri_id_1(cursor):
    """Cursor.delete_from_page_where_uri_id_1()のテスト．
    """
    uri = 'https://ja.wikipedia.org/wiki/%E7%B7%8F%E5%92%8C'
    exprs = ['expr1', 'expr2']
    title = '総和 - Wikipedia'
    descr = 'descr'

    cursor.execute(
        'INSERT INTO page (uri, exprs, title, descr) VALUES (%s, %s, %s, %s)', 
        (uri, json.dumps(exprs), title, descr)
        )

    select_query = 'SELECT * FROM page WHERE uri = %s'

    cursor.execute(select_query, (uri,))
    tpl = cursor.fetchone()
    assert tpl is not None  # データが登録されていることを確認．

    uri_id = tpl[1]
    Cursor.delete_from_page_where_uri_id_1(cursor, uri_id)

    cursor.execute(select_query, (uri,))
    assert cursor.fetchone() is None  # データが削除されていることを確認．


def test_delete_from_path_dictionary_where_expr_path_1(cursor):
    """Cursor.delete_from_path_dictionary_where_expr_path_1()のテスト．
    """
    expr_ids = ['1', '2', '3']
    expr_path = 'expr_path1'

    # expr_pathとexpr_idsを登録．
    cursor.execute(
        'INSERT INTO path_dictionary (expr_path, expr_ids) VALUES (%s, %s)',
        (expr_path, json.dumps(expr_ids))
        )

    select_query = 'SELECT * FROM path_dictionary WHERE expr_path = %s'

    cursor.execute(select_query, (expr_path,))
    assert cursor.fetchone() is not None  # データが登録されていることを確認．

    Cursor.delete_from_path_dictionary_where_expr_path_1(cursor, expr_path)

    cursor.execute(select_query, (expr_path,))
    assert cursor.fetchone() is None  # データが削除されていることを確認．


def test_insert_into_index_values_1(cursor):
    """Cursor.insert_into_index_values_1_2()のテスト．
    """
    expr = '<math>a</math>'
    uri_id = 1
    lang = 'ja'
    info = {"uri_id": [str(uri_id)], "lang": [lang]}

    select_query = 'SELECT * FROM inverted_index WHERE expr = %s'

    cursor.execute(select_query, (expr,))
    assert cursor.fetchone() is None  # insert前

    Cursor.insert_into_index_values_1_2(cursor, expr, uri_id, lang)
    cursor.execute(select_query, (expr,))
    # insert後
    result = cursor.fetchone()
    result_expr_id = result[0]
    result_expr = result[1]
    result_info = json.loads(result[2])
    assert type(result_expr_id) == int
    assert result_expr == expr
    assert result_info == info


def test_insert_into_uri_values_1(cursor):
    """Cursor.insert_into_page_values_1_2_3_4()のテスト．
    """
    uri = 'https://ja.wikipedia.org/wiki/%E7%B7%8F%E5%92%8C'
    exprs = ['expr1', 'expr2']
    title = '総和 - Wikipedia'
    descr = 'descr'

    select_query = 'SELECT * FROM page WHERE uri = %s'

    # insert前
    cursor.execute(select_query, (uri,))
    assert cursor.fetchone() is None
    Cursor.insert_into_page_values_1_2_3_4(cursor, uri, exprs, title, descr)
    # insert後
    cursor.execute(select_query, (uri,))
    result = cursor.fetchone()
    result_uri = result[0]
    result_uri_id = result[1]
    result_exprs = json.loads(result[2])
    result_title = result[3]
    result_descr = result[4]
    assert result_uri == uri
    assert type(result_uri_id) == int  # idの値は毎回異なるので，型の確認だけする
    assert result_exprs == exprs
    assert result_title == title
    assert result_descr == descr


def test_remove_expr_id_from_path_dictionary_1(cursor):
    """Cursor.remove_expr_id_from_path_dictionary()のテスト．
    """
    remove_expr_id = 2
    expr_ids = ['1', str(remove_expr_id), '3']
    expr_path = 'path1'

    # expr_pathとexpr_idsを登録．
    cursor.execute(
        'INSERT INTO path_dictionary (expr_path, expr_ids) VALUES (%s, %s)',
        (expr_path, json.dumps(expr_ids))
        )

    select_query = 'SELECT expr_ids FROM path_dictionary WHERE expr_path = %s'

    cursor.execute(select_query, (expr_path,))
    tmp = cursor.fetchone()
    tmp_expr_ids = json.loads(tmp[0])
    assert tmp_expr_ids == expr_ids  # expr_pathが登録されていることを確認

    Cursor.remove_expr_id_from_path_dictionary(cursor, remove_expr_id, expr_path)

    cursor.execute(select_query, (expr_path,))
    result_expr_ids = json.loads(cursor.fetchone()[0])
    assert result_expr_ids == ['1', '3']


def test_remove_info_from_inverted_index_1(cursor):
    """Cursor.remove_info_from_inverted_index()のテスト．
    """
    expr = '<math>a</math>'
    remove_uri_id = 2
    cursor.execute(
        'INSERT INTO inverted_index (expr, info) VALUES (%s, JSON_OBJECT("uri_id", JSON_ARRAY(%s, %s, %s), "lang", JSON_ARRAY(%s, %s, %s)))',
        (expr, "1", str(remove_uri_id), "3", "ja", "ja", "ja")
        )

    Cursor.remove_info_from_inverted_index(cursor, expr, remove_uri_id)

    cursor.execute('SELECT info FROM inverted_index WHERE expr = %s', (expr,))
    result_info = json.loads(cursor.fetchone()[0])

    expected_info = {
        "uri_id": ["1", "3"],
        "lang": ["ja", "ja"]
        }
    assert result_info == expected_info


def test_select_all_from_index_where_expr_id_1(cursor):
    """Cursor.select_all_from_index_where_expr_id_1()のテスト．
    """
    expr = '<math>a</math>'
    info = {
        "uri_id": ["1", "2"],
        "lang": ["ja", "ja"]
        }
    cursor.execute(
        'INSERT INTO inverted_index (expr, info) VALUES (%s, JSON_OBJECT("uri_id", JSON_ARRAY(%s, %s), "lang", JSON_ARRAY(%s, %s)))',
        (expr, "1", "2", "ja", "ja")
        )

    cursor.execute('SELECT expr_id FROM inverted_index WHERE expr = %s', (expr,))
    expr_id = cursor.fetchone()[0]

    result = Cursor.select_all_from_index_where_expr_id_1(cursor, expr_id)
    result_expr_id = result[0]
    result_info = json.loads(result[2])
    result_expr = result[1]
    assert expr_id == result_expr_id
    assert result_expr == expr
    assert result_info == info


def test_select_all_from_page_where_uri_id_1(cursor):
    """Cursor.select_all_from_page_where_uri_id_1()のテスト．
    """
    uri = 'https://ja.wikipedia.org/wiki/%E7%B7%8F%E5%92%8C'
    exprs = ['expr1', 'expr2']
    title = '総和 - Wikipedia'
    descr = 'descr'

    cursor.execute(
        'INSERT INTO page (uri, exprs, title, descr) VALUES (%s, %s, %s, %s)', 
        (uri, json.dumps(exprs), title, descr)
        )
    cursor.execute('SELECT uri_id FROM page WHERE title = %s', (title,))
    uri_id = cursor.fetchone()[0]
    assert type(uri_id) == int

    result = Cursor.select_all_from_page_where_uri_id_1(cursor, uri_id)
    result_uri = result[0]
    result_uri_id = result[1]
    result_exprs = json.loads(result[2])
    result_title = result[3]
    result_descr = result[4]
    assert result_uri == uri
    assert type(result_uri_id) == int  # idの値は毎回異なるので，型の確認だけする
    assert result_exprs == exprs
    assert result_title == title
    assert result_descr == descr


def test_select_all_from_path_dict_where_expr_path_1(cursor):
    """Cursor.select_all_from_path_dict_where_expr_path_1()のテスト．
    """
    expr_path = 'expr_path_1'
    expr_ids = ['1', '3']
    cursor.execute(
        'INSERT INTO path_dictionary (expr_path, expr_ids) VALUES (%s, %s)', 
        (expr_path, json.dumps(expr_ids))
        )

    result = Cursor.select_all_from_path_dict_where_expr_path_1(cursor, expr_path)
    result_expr_path = result[0]
    result_expr_ids = json.loads(result[1])
    assert result_expr_path == expr_path
    assert result_expr_ids == expr_ids


def test_select_expr_id_from_inverted_index_where_expr_1(cursor):
    """Cursor.select_expr_id_from_inverted_index_where_expr_1()のテスト．
    """
    expr = 'expr1'
    uri_id = 1
    lang = 'ja'
    Cursor.insert_into_index_values_1_2(cursor, expr, uri_id, lang)

    result = Cursor.select_expr_id_from_inverted_index_where_expr_1(cursor, expr)
    assert type(result) == int


def test_select_expr_ids_from_path_dictionary_where_expr_path_1(cursor):
    """Cursor.select_expr_ids_from_path_dictionary_where_expr_path_1()のテスト．
    """
    expr_path = 'path1'
    expr_ids = ['1', '2', '3', '5']
    cursor.execute(
        'INSERT INTO path_dictionary (expr_path, expr_ids) VALUES (%s, %s)',
        (expr_path, json.dumps(expr_ids))
        )
    result_expr_ids = Cursor.select_expr_ids_from_path_dictionary_where_expr_path_1(cursor, expr_path)
    assert result_expr_ids == expr_ids


def test_select_info_from_inverted_index_where_expr_id_1(cursor):
    """Cursor.select_info_from_inverted_index_where_expr_id_1()のテスト．
    """
    expr_id: int = 1
    info = {
        "uri_id": ["1", "2"],
        "lang": ["ja", "ja"]
        }
    cursor.execute(
        'INSERT INTO inverted_index (expr_id, info) VALUES (%s, JSON_OBJECT("uri_id", JSON_ARRAY(%s, %s), "lang", JSON_ARRAY(%s, %s)))', 
        (expr_id, "1", "2", "ja", "ja")
        )
    result_info = Cursor.select_info_from_inverted_index_where_expr_id_1(cursor, expr_id)
    assert result_info == info


def test_select_uri_id_and_exprs_from_page_where_uri_1(cursor):
    """Cursor.select_uri_id_and_exprs_from_page_where_uri_1()のテスト．
    """
    uri = 'https://ja.wikipedia.org/wiki/%E7%B7%8F%E5%92%8C'
    exprs = ['expr1', 'expr2']
    title = '総和 - Wikipedia'
    descr = 'descr'

    cursor.execute(
        'INSERT INTO page (uri, exprs, title, descr) VALUES (%s, %s, %s, %s)', 
        (uri, json.dumps(exprs), title, descr)
        )

    result = Cursor.select_uri_id_and_exprs_from_page_where_uri_1(cursor, uri)
    result_uri_id = result[0]
    result_exprs = result[1]
    assert type(result_uri_id) == int  # idの値は毎回異なるので，型の確認だけする
    assert result_exprs == set(exprs)


def test_select_uri_id_from_page_where_uri_1(cursor):
    """Cursor.select_uri_id_from_page_where_uri_1()のテスト．
    """
    uri = 'https://ja.wikipedia.org/wiki/%E7%B7%8F%E5%92%8C'
    exprs = ['expr1', 'expr2']
    title = '総和 - Wikipedia'
    descr = 'descr'

    cursor.execute(
        'INSERT INTO page (uri, exprs, title, descr) VALUES (%s, %s, %s, %s)', 
        (uri, json.dumps(exprs), title, descr)
        )

    result_uri_id = Cursor.select_uri_id_from_page_where_uri_1(cursor, uri)
    assert type(result_uri_id) == int  # idの値は毎回異なるので，型の確認だけする


def test_select_uri_id_from_page_where_uri_2(cursor):
    """Cursor.select_uri_id_from_page_where_uri_1()のテスト．
    """
    uri_1 = 'uri1'
    exprs = ['expr1', 'expr2']
    title = '総和 - Wikipedia'
    descr = 'descr'

    cursor.execute(
        'INSERT INTO page (uri, exprs, title, descr) VALUES (%s, %s, %s, %s)', 
        (uri_1, json.dumps(exprs), title, descr)
        )

    uri_2 = 'uri2'
    result_uri_id = Cursor.select_uri_id_from_page_where_uri_1(cursor, uri_2)
    assert result_uri_id == None  # idの値は毎回異なるので，型の確認だけする


def test_select_json_array_append_expr_ids_where_expr_path_2(cursor):
    """Cursor.select_json_array_append_expr_ids_where_expr_path_2()のテスト．
    """
    expr_path = 'path1'
    expr_ids = ['1', '2', '3', '5']
    cursor.execute(
        'INSERT INTO path_dictionary (expr_path, expr_ids) VALUES (%s, %s)',
        (expr_path, json.dumps(expr_ids))
        )

    expr_id = 10
    Cursor.select_json_array_append_expr_ids_where_expr_path_2(cursor, expr_id, expr_path)

    cursor.execute('SELECT expr_ids FROM path_dictionary WHERE expr_path = %s', (expr_path,))
    actual = json.loads(cursor.fetchone()[0])
    expected = ['1', '2', '3', '5', str(expr_id)]
    assert actual == expected


def test_select_json_array_append_lang_1(cursor):
    """Cursor.select_json_array_append_lang()のテスト．"""
    expr = '<math>a</math>'
    cursor.execute(
        'INSERT INTO inverted_index (expr, info) VALUES (%s, JSON_OBJECT("uri_id", JSON_ARRAY(%s, %s, %s), "lang", JSON_ARRAY(%s, %s, %s)))',
        (expr, "1", "2", "3", "ja", "ja", "ja")
        )

    cursor.execute('SELECT expr_id FROM inverted_index WHERE expr = %s', (expr,))
    expr_id = cursor.fetchone()[0]
    Cursor.select_json_array_append_lang(cursor, 'en', expr_id)

    cursor.execute('SELECT info FROM inverted_index WHERE expr = %s', (expr,))
    actual = json.loads(cursor.fetchone()[0])
    expected = {
        "uri_id": ["1", "2", "3"],
        "lang": ["ja", "ja", "ja", "en"]
        }
    assert actual == expected


def test_select_json_array_append_uri_id_1(cursor):
    """Cursor.select_json_array_append_uri_id()のテスト．"""
    expr = '<math>a</math>'
    cursor.execute(
        'INSERT INTO inverted_index (expr, info) VALUES (%s, JSON_OBJECT("uri_id", JSON_ARRAY(%s, %s, %s), "lang", JSON_ARRAY(%s, %s, %s)))',
        (expr, "1", "2", "3", "ja", "ja", "ja")
        )

    cursor.execute('SELECT expr_id FROM inverted_index WHERE expr = %s', (expr,))
    expr_id = cursor.fetchone()[0]
    Cursor.select_json_array_append_uri_id(cursor, 100, expr_id)

    cursor.execute('SELECT info FROM inverted_index WHERE expr = %s', (expr,))
    actual = json.loads(cursor.fetchone()[0])
    expected = {
        "uri_id": ["1", "2", "3", "100"],
        "lang": ["ja", "ja", "ja"]
        }
    assert actual == expected


def test_select_json_replace_info_1(cursor):
    """Cursor.select_json_replace_info()のテスト．
    replace lang.
    """
    expr = '<math>a</math>'
    cursor.execute(
        'INSERT INTO inverted_index (expr, info) VALUES (%s, JSON_OBJECT("uri_id", JSON_ARRAY(%s, %s, %s), "lang", JSON_ARRAY(%s, %s, %s)))',
        (expr, "1", "2", "3", "ja", "ja", "ja")
        )

    cursor.execute('SELECT expr_id FROM inverted_index WHERE expr = %s', (expr,))
    expr_id = cursor.fetchone()[0]

    lang_path = '$.lang[1]'
    lang = 'en'
    Cursor.select_json_replace_info(cursor, lang_path, lang, expr_id)

    cursor.execute('SELECT info FROM inverted_index WHERE expr = %s', (expr,))
    actual = json.loads(cursor.fetchone()[0])
    expected = {
        "uri_id": ["1", "2", "3"],
        "lang": ["ja", lang, "ja"],
        }
    assert actual == expected


def test_select_json_replace_info_2(cursor):
    """Cursor.select_json_replace_info()のテスト．
    replace uri_id.
    """
    expr = '<math>a</math>'
    cursor.execute(
        'INSERT INTO inverted_index (expr, info) VALUES (%s, JSON_OBJECT("uri_id", JSON_ARRAY(%s, %s, %s), "lang", JSON_ARRAY(%s, %s, %s)))',
        (expr, "1", "2", "3", "ja", "ja", "ja")
        )

    cursor.execute('SELECT expr_id FROM inverted_index WHERE expr = %s', (expr,))
    expr_id = cursor.fetchone()[0]

    uri_id_path = '$.uri_id[2]'
    uri_id = 5
    Cursor.select_json_replace_info(cursor, uri_id_path, str(uri_id), expr_id)

    cursor.execute('SELECT info FROM inverted_index WHERE expr = %s', (expr,))
    actual = json.loads(cursor.fetchone()[0])
    expected = {
        "uri_id": ["1", "2", str(uri_id)],
        "lang": ["ja", "ja", "ja"],
        }
    assert actual == expected


def test_select_json_search_expr_ids_from_path_dict_where_expr_path_1(cursor):
    """Cursor.select_json_search_expr_ids_1_from_path_dict_where_expr_path_2()のテスト．
    """
    expr_path = 'path1'
    expr_ids = ['1', '2', '3', '5']
    cursor.execute(
        'INSERT INTO path_dictionary (expr_path, expr_ids) VALUES (%s, %s)',
        (expr_path, json.dumps(expr_ids))
        )

    cursor.execute(
        'SELECT expr_ids FROM path_dictionary WHERE expr_path = %s',
        (expr_path,)
        )
    tmp = cursor.fetchone()[0]
    tmp_expr_ids = json.loads(tmp)
    assert tmp_expr_ids == expr_ids  # 正しくDBに登録されているか確認

    result_pos = Cursor.select_json_search_expr_ids_1_from_path_dict_where_expr_path_2(cursor, 3, expr_path)
    assert result_pos == "$[2]"


def test_select_json_search_uri_id_1_from_inverted_index_where_expr_2_1(cursor):
    """Cursor.select_json_search_uri_id_1_from_inverted_index_where_expr_2()のテスト．
    """
    expr = '<math>a</math>'
    uri_id = 2
    cursor.execute(
        'INSERT INTO inverted_index (expr, info) VALUES (%s, JSON_OBJECT("uri_id", JSON_ARRAY(%s, %s, %s), "lang", JSON_ARRAY(%s, %s, %s)))',
        (expr, "1", str(uri_id), "3", "ja", "ja", "ja")
        )

    actual = Cursor.select_json_search_uri_id_1_from_inverted_index_where_expr_2(cursor, uri_id, expr)
    expected = '$.uri_id[1]'
    assert actual == expected


def test_select_json_search_uri_id_1_from_inverted_index_where_expr_id_2_1(cursor):
    """Cursor.select_json_search_uri_id_1_from_inverted_index_where_expr_id_2()のテスト．"""
    expr = '<math>a</math>'
    uri_id = 2
    cursor.execute(
        'INSERT INTO inverted_index (expr, info) VALUES (%s, JSON_OBJECT("uri_id", JSON_ARRAY(%s, %s, %s), "lang", JSON_ARRAY(%s, %s, %s)))',
        (expr, "1", str(uri_id), "3", "ja", "ja", "ja")
        )

    cursor.execute('SELECT expr_id FROM inverted_index WHERE expr = %s', (expr,))
    expr_id: int = cursor.fetchone()[0]

    actual = Cursor.select_json_search_uri_id_1_from_inverted_index_where_expr_id_2(cursor, uri_id, expr_id)
    expected = '$.uri_id[1]'
    assert actual == expected


def test_select_json_search_uri_id_1_from_inverted_index_where_expr_id_2_2(cursor):
    """Cursor.select_json_search_uri_id_1_from_inverted_index_where_expr_id_2()のテスト．
    含まれないuri_idを探す処理
    """
    expr = '<math>a</math>'
    cursor.execute(
        'INSERT INTO inverted_index (expr, info) VALUES (%s, JSON_OBJECT("uri_id", JSON_ARRAY(%s, %s, %s), "lang", JSON_ARRAY(%s, %s, %s)))',
        (expr, "1", "2", "3", "ja", "ja", "ja")
        )

    cursor.execute('SELECT expr_id FROM inverted_index WHERE expr = %s', (expr,))
    expr_id: int = cursor.fetchone()[0]

    actual = Cursor.select_json_search_uri_id_1_from_inverted_index_where_expr_id_2(cursor, 10, expr_id)
    expected = None
    assert actual == expected


def test_update_inverted_index_set_info_1_where_expr_2(cursor):
    """Cursor.update_inverted_index_set_info_1_where_expr_2()のテスト．"""
    expr = '<math>a</math>'
    cursor.execute(
        'INSERT INTO inverted_index (expr, info) VALUES (%s, JSON_OBJECT("uri_id", JSON_ARRAY(%s, %s), "lang", JSON_ARRAY(%s, %s)))',
        (expr, "1", "2", "ja", "ja")
        )
    expected_info = {
        "uri_id": ["1", "2"],
        "lang": ["ja", "en"]
        }
    Cursor.update_inverted_index_set_info_1_where_expr_2(cursor, json.dumps(expected_info), expr)

    cursor.execute('SELECT info FROM inverted_index WHERE expr = %s', (expr,))
    actual_info = json.loads(cursor.fetchone()[0])
    assert actual_info == expected_info


def test_update_inverted_index_set_info_1_where_expr_id_2(cursor):
    """Cursor.update_inverted_index_set_info_1_where_expr_id_2()のテスト．"""
    expr = '<math>a</math>'
    cursor.execute(
        'INSERT INTO inverted_index (expr, info) VALUES (%s, JSON_OBJECT("uri_id", JSON_ARRAY(%s, %s), "lang", JSON_ARRAY(%s, %s)))',
        (expr, "1", "2", "ja", "ja")
        )
    expected_info = {
        "uri_id": ["1", "2"],
        "lang": ["ja", "en"]
        }

    cursor.execute('SELECT expr_id FROM inverted_index WHERE expr = %s', (expr,))
    expr_id: int = cursor.fetchone()[0]
    Cursor.update_inverted_index_set_info_1_where_expr_id_2(cursor, json.dumps(expected_info), expr_id)

    cursor.execute('SELECT info FROM inverted_index WHERE expr = %s', (expr,))
    actual_info = json.loads(cursor.fetchone()[0])
    assert actual_info == expected_info


def test_update_page_set_exprs_title_descr_where_uri_id_1(cursor):
    """Cursor.update_page_set_exprs_1_title_2_descr_3_where_uri_id_4()のテスト．
    """
    uri = 'https://ja.wikipedia.org/wiki/%E7%B7%8F%E5%92%8C'
    exprs = ['expr1', 'expr2']
    title = '総和 - Wikipedia'
    descr = 'descr'

    # insert
    cursor.execute(
        'INSERT INTO page (uri, exprs, title, descr) VALUES (%s, %s, %s, %s)', 
        (uri, json.dumps(exprs), title, descr)
        )

    # get uri_id
    cursor.execute('SELECT uri_id FROM page WHERE title = %s', (title,))
    uri_id = cursor.fetchone()[0]
    assert type(uri_id) == int

    # update
    new_exprs = ['new_expr1', 'new_expr2']
    new_title = 'new title'
    new_descr = 'new description'
    Cursor.update_page_set_exprs_1_title_2_descr_3_where_uri_id_4(cursor, new_exprs, new_title, new_descr, uri_id)

    # check updated record
    cursor.execute('SELECT * FROM page WHERE uri_id = %s', (uri_id,))
    result = cursor.fetchone()
    result_uri = result[0]
    result_uri_id = result[1]
    result_exprs = json.loads(result[2])
    result_title = result[3]
    result_descr = result[4]
    assert result_exprs == new_exprs
    assert result_title == new_title
    assert result_descr == new_descr


def test_update_path_dictionary_set_expr_ids_1_where_expr_path_2(cursor):
    """Cursor.update_path_dictionary_set_expr_ids_1_where_expr_path_2()のテスト．
    """
    expr_path = 'path1'
    expr_ids = ['1', '2', '3', '5']
    cursor.execute(
        'INSERT INTO path_dictionary (expr_path, expr_ids) VALUES (%s, %s)',
        (expr_path, json.dumps(expr_ids))
        )

    new_expr_ids = ['2', '7', '10', '11', '100']
    Cursor.update_path_dictionary_set_expr_ids_1_where_expr_path_2(cursor, json.dumps(new_expr_ids), expr_path)

    cursor.execute('SELECT expr_ids FROM path_dictionary WHERE expr_path = %s', (expr_path,))
    actual = json.loads(cursor.fetchone()[0])
    assert actual == new_expr_ids


def test_uri_is_already_registered_1(cursor):
    """Cursor.uri_is_already_registered()のテスト．
    """
    uri = 'https://ja.wikipedia.org/wiki/%E7%B7%8F%E5%92%8C'
    exprs = ['expr1', 'expr2']
    title = '総和 - Wikipedia'
    descr = 'descr'

    cursor.execute(
        'INSERT INTO page (uri, exprs, title, descr) VALUES (%s, %s, %s, %s)',
        (uri, json.dumps(exprs), title, descr)
        )

    # Trueの場合
    assert Cursor.uri_is_already_registered(cursor, uri) is True

    not_registered_uri = 'foo'
    # Falseの場合
    assert Cursor.uri_is_already_registered(cursor, not_registered_uri) is False
