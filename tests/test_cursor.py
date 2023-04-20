import json
import traceback

import pytest
import mysql.connector

from twels.database.cursor import Cursor
from twels.expr.expression import Expression
from twels.expr.parser import Parser
from twels.indexer.info import Info
from twels.snippet.snippet import Snippet
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
    expr_size = 5

    select_query = 'SELECT expr_ids FROM path_dictionary WHERE expr_path = %s AND expr_size = %s'

    cursor.execute(select_query, (expr_path, expr_size))
    assert cursor.fetchone() is None  # insert前

    Cursor.append_expr_id_if_not_registered(cursor, expr_id, expr_path, expr_size)

    cursor.execute(select_query, (expr_path, expr_size))
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
    expr_size = 5

    # expr_pathと他のexpr_idを登録．
    cursor.execute(
        'INSERT INTO path_dictionary (expr_path, expr_size, expr_ids) VALUES (%s, %s, %s)',
        (expr_path, expr_size, json.dumps([str(other_expr_id)]))
        )

    select_query = 'SELECT expr_ids FROM path_dictionary WHERE expr_path = %s AND expr_size = %s'

    cursor.execute(select_query, (expr_path, expr_size))
    assert cursor.fetchone() is not None  # expr_pathが登録されていることを確認

    Cursor.append_expr_id_if_not_registered(cursor, expr_id, expr_path, expr_size)

    cursor.execute(select_query, (expr_path, expr_size))
    result_expr_ids = json.loads(cursor.fetchone()[0])
    assert result_expr_ids == [str(other_expr_id), str(expr_id)]


def test_append_expr_id_if_not_registered_3(cursor):
    """Cursor.append_expr_id_if_not_registered()のテスト．
    path_dictionaryにexpr_pathは登録されていて，expr_idも登録されている場合．
    重複して追加されていないことを確認．
    """
    expr_id = 1
    expr_path = 'path1'
    expr_size = 5

    # expr_pathとexpr_idを登録．
    cursor.execute(
        'INSERT INTO path_dictionary (expr_path, expr_size, expr_ids) VALUES (%s, %s, %s)',
        (expr_path, expr_size, json.dumps([str(expr_id)]))
        )

    select_query = 'SELECT expr_ids FROM path_dictionary WHERE expr_path = %s AND expr_size = %s'

    cursor.execute(select_query, (expr_path, expr_size))
    assert cursor.fetchone() is not None  # expr_pathが登録されていることを確認

    Cursor.append_expr_id_if_not_registered(cursor, expr_id, expr_path, expr_size)

    cursor.execute(select_query, (expr_path, expr_size))
    result = cursor.fetchone()
    result_expr_ids = json.loads(result[0])
    assert result_expr_ids == [str(expr_id)]


def test_count_json_values_1(cursor):
    """count_json_values()のテスト。"""
    ids_1 = ['1', '2', '3']
    ids_2 = ['1', '2', '4']
    ids_3 = ['1', '2', '4']
    ids_4 = ['1', '2', '4']
    ids_5 = ['1', '3', '5']

    ids_1.extend(ids_2)
    ids_1.extend(ids_3)
    ids_1.extend(ids_4)
    ids_1.extend(ids_5)

    query = """
    SELECT count_json_values(%(j)s)
    """
    data = {
        'j': json.dumps(list(ids_1))
    }
    cursor.execute(query, data)
    actual = json.loads(cursor.fetchone()[0])
    actual_sorted = sorted(actual, key=lambda x: x[1], reverse=True)
    expected = [
        ['1', 5], ['2', 4], ['4', 3], ['3', 2], ['5', 1]
    ]

    assert actual_sorted == expected


def test_delete_from_inverted_index_where_expr_1(cursor):
    """Cursor.delete_from_inverted_index_where_expr_1()のテスト．
    """
    mathml = '<math>a</math>'
    info = Info({
        "uri_id": ["1", "2"],
        "lang": ["ja", "ja"],
        "expr_start_pos": [
            [40, 93, 279],
            [20, 66]
        ]
    })

    query = """INSERT INTO inverted_index (expr, expr_len, info) VALUES (%(expr)s, %(len)s, %(info)s)"""
    data = {
            'expr': mathml,
            'len': len(mathml),
            'info': info.dumps()
    }

    cursor.execute(query, data)

    select_query = 'SELECT * FROM inverted_index WHERE expr = %s'

    cursor.execute(select_query, (mathml,))
    assert cursor.fetchone() is not None  # データが登録されていることを確認．

    expr = Expression(mathml)
    Cursor.delete_from_inverted_index_where_expr_1(cursor, expr)

    cursor.execute(select_query, (expr.mathml,))
    assert cursor.fetchone() is None  # データが削除されていることを確認．


def test_delete_from_inverted_index_where_expr_id_1(cursor):
    """Cursor.delete_from_inverted_index_where_expr_id_1()のテスト．
    """
    mathml = '<math>a</math>'
    info = Info({
        "uri_id": ["1", "2"],
        "lang": ["ja", "ja"],
        "expr_start_pos": [
            [40, 93, 279],
            [20, 66]
        ]
    })

    query = """INSERT INTO inverted_index (expr, expr_len, info) VALUES (%(expr)s, %(len)s, %(info)s)"""
    data = {
            'expr': mathml,
            'len': len(mathml),
            'info': info.dumps()
    }

    cursor.execute(query, data)

    select_query = 'SELECT * FROM inverted_index WHERE expr = %s'

    cursor.execute(select_query, (mathml,))
    tpl = cursor.fetchone()
    # データが登録されていることを確認．
    expr_id: int = tpl[0]
    assert tpl[1] == mathml

    Cursor.delete_from_inverted_index_where_expr_id_1(cursor, expr_id)

    cursor.execute(select_query, (mathml,))
    assert cursor.fetchone() is None  # データが削除されていることを確認．


def test_delete_from_page_where_uri_id_1(cursor):
    """Cursor.delete_from_page_where_uri_id_1()のテスト．
    """
    uri = 'https://ja.wikipedia.org/wiki/%E7%B7%8F%E5%92%8C'
    exprs = ['expr1', 'expr2']
    title = '総和 - Wikipedia'
    snippet = 'snippet'

    cursor.execute(
        'INSERT INTO page (uri, exprs, title, snippet) VALUES (%s, %s, %s, %s)',
        (uri, json.dumps(exprs), title, snippet)
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
    expr_size = 5

    # expr_pathとexpr_idsを登録．
    cursor.execute(
        'INSERT INTO path_dictionary (expr_path, expr_size, expr_ids) VALUES (%s, %s, %s)',
        (expr_path, expr_size, json.dumps(expr_ids))
        )

    select_query = 'SELECT * FROM path_dictionary WHERE expr_path = %s AND expr_size = %s'

    cursor.execute(select_query, (expr_path, expr_size))
    assert cursor.fetchone() is not None  # データが登録されていることを確認．

    Cursor.delete_from_path_dictionary_where_expr_path_1(cursor, expr_path, expr_size)

    cursor.execute(select_query, (expr_path, expr_size))
    assert cursor.fetchone() is None  # データが削除されていることを確認．


def test_insert_into_uri_values_1(cursor):
    """Cursor.insert_into_page_values_1_2_3_4()のテスト．
    """
    uri = 'https://ja.wikipedia.org/wiki/%E7%B7%8F%E5%92%8C'
    exprs = [Expression('<math>expr1</math>'), Expression('<math>expr2</math>')]
    title = '総和 - Wikipedia'
    snippet = Snippet('snippet')

    select_query = 'SELECT * FROM page WHERE uri = %s'

    # insert前
    cursor.execute(select_query, (uri,))
    assert cursor.fetchone() is None
    Cursor.insert_into_page_values_1_2_3_4(cursor, uri, exprs, title, snippet)
    # insert後
    cursor.execute(select_query, (uri,))
    result = cursor.fetchone()
    result_uri = result[0]
    result_uri_id = result[1]
    result_exprs = json.loads(result[2])
    result_title = result[3]
    result_snippet = result[4]
    assert result_uri == uri
    assert type(result_uri_id) == int  # idの値は毎回異なるので，型の確認だけする
    assert result_exprs == list(map(str, exprs))
    assert result_title == title
    assert result_snippet == snippet.text


def test_merge_expr_ids_1(cursor):
    """merge_expr_ids()のテスト。"""
    path_set = {'path1', 'path2', 'path3', 'path4', 'path5'}
    ids_1 = ['1', '2', '3', '4', '5']
    ids_2 = ['1', '3', '5', '7', '9']
    ids_3 = ['1', '2', '4', '8', '16']
    ids_4 = ['1', '2', '3', '5', '8']
    ids_5 = ['1', '4', '9', '16', '25']
    expr_size = len(path_set)

    query = 'INSERT INTO path_dictionary (expr_path, expr_size, expr_ids) VALUES (%s, %s, %s)'
    cursor.execute(query, ('path1', expr_size, json.dumps(ids_1)))
    cursor.execute(query, ('path2', expr_size, json.dumps(ids_2)))
    cursor.execute(query, ('path3', expr_size, json.dumps(ids_3)))
    cursor.execute(query, ('path4', expr_size, json.dumps(ids_4)))
    cursor.execute(query, ('path5', expr_size, json.dumps(ids_5)))

    query = """
    SELECT merge_expr_ids(%(path_set)s, %(expr_size)s)
    """
    data = {
        'path_set': json.dumps(list(path_set)),
        'expr_size': expr_size
    }
    cursor.execute(query, data)
    actual = json.loads(cursor.fetchone()[0])
    actual_sorted = sorted(actual)

    ids_1.extend(ids_2)
    ids_1.extend(ids_3)
    ids_1.extend(ids_4)
    ids_1.extend(ids_5)
    expected_sorted = sorted(ids_1)

    assert actual_sorted == expected_sorted


def test_remove_expr_id_from_path_dictionary_1(cursor):
    """Cursor.remove_expr_id_from_path_dictionary()のテスト．
    """
    remove_expr_id = 2
    expr_ids = ['1', str(remove_expr_id), '3']
    expr_path = 'path1'
    expr_size = 5

    # expr_pathとexpr_idsを登録．
    cursor.execute(
        'INSERT INTO path_dictionary (expr_path, expr_size, expr_ids) VALUES (%s, %s, %s)',
        (expr_path, expr_size, json.dumps(expr_ids))
        )

    select_query = 'SELECT expr_ids FROM path_dictionary WHERE expr_path = %s AND expr_size = %s'

    cursor.execute(select_query, (expr_path, expr_size))
    tmp = cursor.fetchone()
    tmp_expr_ids = json.loads(tmp[0])
    assert tmp_expr_ids == expr_ids  # expr_pathが登録されていることを確認

    result_expr_ids = Cursor.remove_expr_id_from_path_dictionary(cursor, remove_expr_id, expr_path, expr_size)

    assert result_expr_ids == ['1', '3']


def test_remove_expr_id_from_path_dictionary_2(cursor):
    """Cursor.remove_expr_id_from_path_dictionary()のテスト．
    削除する前の要素数が1つの場合。
    """
    remove_expr_id = 1
    expr_ids = [str(remove_expr_id)]
    expr_path = 'path1'
    expr_size = 5

    # expr_pathとexpr_idsを登録．
    cursor.execute(
        'INSERT INTO path_dictionary (expr_path, expr_size, expr_ids) VALUES (%s, %s, %s)',
        (expr_path, expr_size, json.dumps(expr_ids))
        )

    select_query = 'SELECT expr_ids FROM path_dictionary WHERE expr_path = %s AND expr_size = %s'

    cursor.execute(select_query, (expr_path, expr_size))
    tmp = cursor.fetchone()
    tmp_expr_ids = json.loads(tmp[0])
    assert tmp_expr_ids == expr_ids  # expr_pathが登録されていることを確認

    result_expr_ids = Cursor.remove_expr_id_from_path_dictionary(cursor, remove_expr_id, expr_path, expr_size)

    assert result_expr_ids == []


def test_remove_expr_id_from_path_dictionary_3(cursor):
    """Cursor.remove_expr_id_from_path_dictionary()のテスト．
    登録されていないexpr_idを指定した場合。
    """
    expr_ids = ['1']
    expr_path = 'path1'
    expr_size = 5

    # expr_pathとexpr_idsを登録．
    cursor.execute(
        'INSERT INTO path_dictionary (expr_path, expr_size, expr_ids) VALUES (%s, %s, %s)',
        (expr_path, expr_size, json.dumps(expr_ids))
        )

    select_query = 'SELECT expr_ids FROM path_dictionary WHERE expr_path = %s AND expr_size = %s'

    cursor.execute(select_query, (expr_path, expr_size))
    tmp = cursor.fetchone()
    tmp_expr_ids = json.loads(tmp[0])
    assert tmp_expr_ids == expr_ids  # expr_pathが登録されていることを確認

    result_expr_ids = Cursor.remove_expr_id_from_path_dictionary(cursor, 2, expr_path, expr_size)

    assert result_expr_ids == expr_ids


def test_remove_info_from_inverted_index_1(cursor):
    """Cursor.remove_info_from_inverted_index()のテスト．
    """
    mathml = '<math>a</math>'
    expr = Expression(mathml)
    remove_uri_id = 2
    info = Info({
        "uri_id": ["1", str(remove_uri_id), "3"],
        "lang": ["ja", "ja", "ja"],
        "expr_start_pos": [
            [40, 93, 279],
            [20, 66],
            [77, 165, 222]
        ]
    })

    query = """INSERT INTO inverted_index (expr, expr_len, info) VALUES (%(expr)s, %(len)s, %(info)s)"""
    data = {
            'expr': expr.mathml,
            'len': len(expr.mathml),
            'info': info.dumps()
    }

    cursor.execute(query, data)

    actual_info = Cursor.remove_info_from_inverted_index(cursor, expr, remove_uri_id)

    expected_info = Info({
        "uri_id": ["1", "3"],
        "lang": ["ja", "ja"],
        "expr_start_pos": [
            [40, 93, 279],
            [77, 165, 222]
        ]
    })
    assert str(actual_info) == str(expected_info)


def test_search_1(cursor):
    """Cursor.search()のテスト。"""
    path_set = {'path1', 'path2', 'path3', 'path4', 'path5'}
    expr_size = len(path_set)
    info = Info({
        "uri_id": ["1", "2", "3"],
        "lang": ["ja", "ja", "ja"],
        "expr_start_pos": [
            [40, 93, 279],
            [20, 66],
            [77, 165, 222]
        ]
    })

    query1 = """INSERT INTO inverted_index (expr, expr_len, expr_size, info) VALUES (
            %s, %s, %s, %s)"""
    for i in range(10):
        cursor.execute(query1, (f'expr{i}', 14, expr_size, info.dumps()))

    query2 = 'SELECT expr_id FROM inverted_index WHERE expr = %s'
    cursor.execute(query2, ('expr0',))
    id_0 = str(cursor.fetchone()[0])
    cursor.execute(query2, ('expr1',))
    id_1 = str(cursor.fetchone()[0])
    cursor.execute(query2, ('expr2',))
    id_2 = str(cursor.fetchone()[0])
    cursor.execute(query2, ('expr3',))
    id_3 = str(cursor.fetchone()[0])
    cursor.execute(query2, ('expr4',))
    id_4 = str(cursor.fetchone()[0])
    cursor.execute(query2, ('expr5',))
    id_5 = str(cursor.fetchone()[0])
    cursor.execute(query2, ('expr6',))
    id_6 = str(cursor.fetchone()[0])
    cursor.execute(query2, ('expr7',))
    id_7 = str(cursor.fetchone()[0])
    cursor.execute(query2, ('expr8',))
    id_8 = str(cursor.fetchone()[0])
    cursor.execute(query2, ('expr9',))
    id_9 = str(cursor.fetchone()[0])

    query3 = 'INSERT INTO path_dictionary (expr_path, expr_size, expr_ids) VALUES (%s, %s, %s)'
    cursor.execute(query3, ('path1', expr_size, json.dumps([id_1, id_2, id_3, id_4, id_5])))
    cursor.execute(query3, ('path2', expr_size, json.dumps([id_1, id_3, id_5, id_6, id_8])))
    cursor.execute(query3, ('path3', expr_size, json.dumps([id_1, id_2, id_4, id_7, id_9])))
    cursor.execute(query3, ('path4', expr_size, json.dumps([id_1, id_2, id_3, id_5, id_7])))
    cursor.execute(query3, ('path5', expr_size, json.dumps([id_1, id_4, id_8, id_9, id_0])))

    result = Cursor.search(cursor, path_set)
    for item in result:
        assert 0 <= item[1] <= 1


def test_select_all_from_index_where_expr_id_1(cursor):
    """Cursor.select_all_from_index_where_expr_id_1()のテスト．
    """
    mathml = '<math><mi>a</mi></math>'
    expr_len = len(mathml)
    path_set = Parser.parse(Expression(mathml))
    expr_start_pos = [
        [76, 130],
        [27, 64, 113, 270]
    ]
    data = {
        "uri_id": ["1", "2"],
        "lang": ["ja", "ja"],
        "expr_start_pos": expr_start_pos
    }
    info = Info(data)

    query = """INSERT INTO inverted_index (expr, expr_len, expr_size, info)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (mathml, expr_len, len(path_set), info.dumps()))

    cursor.execute('SELECT expr_id FROM inverted_index WHERE expr = %s', (mathml,))
    expr_id = cursor.fetchone()[0]

    result = Cursor.select_all_from_index_where_expr_id_1(cursor, expr_id)
    result_expr_id = result[0]
    result_expr = result[1]
    result_expr_len = result[2]
    result_info = Info(json.loads(result[4]))
    assert result_expr_id == expr_id
    assert result_expr == mathml
    assert result_expr_len == expr_len
    assert str(result_info) == str(info)


def test_select_all_from_page_where_uri_id_1(cursor):
    """Cursor.select_all_from_page_where_uri_id_1()のテスト．
    """
    uri = 'https://ja.wikipedia.org/wiki/%E7%B7%8F%E5%92%8C'
    exprs = ['expr1', 'expr2']
    title = '総和 - Wikipedia'
    snippet = 'snippet'

    cursor.execute(
        'INSERT INTO page (uri, exprs, title, snippet) VALUES (%s, %s, %s, %s)',
        (uri, json.dumps(exprs), title, snippet)
        )
    cursor.execute('SELECT uri_id FROM page WHERE title = %s', (title,))
    uri_id = cursor.fetchone()[0]
    assert type(uri_id) == int

    result = Cursor.select_all_from_page_where_uri_id_1(cursor, uri_id)
    result_uri = result[0]
    result_uri_id = result[1]
    result_exprs = json.loads(result[2])
    result_title = result[3]
    result_snippet = result[4]
    assert result_uri == uri
    assert type(result_uri_id) == int  # idの値は毎回異なるので，型の確認だけする
    assert result_exprs == exprs
    assert result_title == title
    assert result_snippet == snippet


def test_select_expr_from_inverted_index_where_expr_id_1(cursor):
    """Cursor.select_expr_from_inverted_index_where_expr_id_1()のテスト．
    """
    expr = '<math>a</math>'
    info = Info({
        "uri_id": ["1", "2", "3"],
        "lang": ["ja", "ja", "ja"],
        "expr_start_pos": [
            [40, 93, 279],
            [20, 66],
            [88, 267]
        ]
    })

    query = """INSERT INTO inverted_index (expr, expr_len, info) VALUES (%(expr)s, %(len)s, %(info)s)"""
    data = {
            'expr': expr,
            'len': len(expr),
            'info': info.dumps()
    }

    cursor.execute(query, data)

    cursor.execute('SELECT expr_id FROM inverted_index WHERE expr = %s', (expr,))
    expr_id = cursor.fetchone()[0]
    assert type(expr_id) == int

    actual = Cursor.select_expr_from_inverted_index_where_expr_id_1(cursor, expr_id)
    assert actual == expr


def test_select_info_from_inverted_index_where_expr_id_1(cursor):
    """Cursor.select_info_from_inverted_index_where_expr_id_1()のテスト．
    """
    mathml = '<math>a</math>'
    expr = Expression(mathml)
    info = Info({
        "uri_id": ["1", "2"],
        "lang": ["ja", "ja"],
        "expr_start_pos": [
            [40, 93, 279],
            [88, 267]
        ]
    })

    query = """INSERT INTO inverted_index (expr, expr_len, info) VALUES (%(expr)s, %(len)s, %(info)s)"""
    data = {
            'expr': expr.mathml,
            'len': len(expr.mathml),
            'info': info.dumps()
    }

    cursor.execute(query, data)

    expr_id = Cursor.select_expr_id_from_inverted_index_where_expr_1(cursor, expr)
    result_info = Cursor.select_info_from_inverted_index_where_expr_id_1(cursor, expr_id)
    assert str(Info(result_info)) == str(info)


def test_select_uri_id_and_exprs_from_page_where_uri_1(cursor):
    """Cursor.select_uri_id_and_exprs_from_page_where_uri_1()のテスト．
    指定したURIが登録されていた場合。
    """
    uri = 'https://ja.wikipedia.org/wiki/%E7%B7%8F%E5%92%8C'
    exprs = [Expression('<math>expr1</math>'), Expression('<math>expr2</math>')]
    exprs_str = Cursor._make_exprs_json_serializable(exprs)
    title = '総和 - Wikipedia'
    snippet = 'snippet'

    cursor.execute(
        'INSERT INTO page (uri, exprs, title, snippet) VALUES (%s, %s, %s, %s)',
        (uri, json.dumps(exprs_str), title, snippet)
        )

    result_uri_id, result_exprs = Cursor.select_uri_id_and_exprs_from_page_where_uri_1(cursor, uri)
    assert type(result_uri_id) == int  # idの値は毎回異なるので，型の確認だけする
    assert result_exprs == set(exprs)


def test_select_uri_id_and_exprs_from_page_where_uri_2(cursor):
    """Cursor.select_uri_id_and_exprs_from_page_where_uri_1()のテスト．
    指定したURIが登録されていなかった場合。
    """
    uri = 'https://ja.wikipedia.org/wiki/%E7%B7%8F%E5%92%8C'

    result_uri_id, result_exprs = Cursor.select_uri_id_and_exprs_from_page_where_uri_1(cursor, uri)
    assert result_uri_id is None


def test_select_uri_id_from_page_where_uri_1(cursor):
    """Cursor.select_uri_id_from_page_where_uri_1()のテスト．
    """
    uri = 'https://ja.wikipedia.org/wiki/%E7%B7%8F%E5%92%8C'
    exprs = ['expr1', 'expr2']
    title = '総和 - Wikipedia'
    snippet = 'snippet'

    cursor.execute(
        'INSERT INTO page (uri, exprs, title, snippet) VALUES (%s, %s, %s, %s)',
        (uri, json.dumps(exprs), title, snippet)
        )

    result_uri_id = Cursor.select_uri_id_from_page_where_uri_1(cursor, uri)
    assert type(result_uri_id) == int  # idの値は毎回異なるので，型の確認だけする


def test_select_uri_id_from_page_where_uri_2(cursor):
    """Cursor.select_uri_id_from_page_where_uri_1()のテスト．
    """
    uri_1 = 'uri1'
    exprs = ['expr1', 'expr2']
    title = '総和 - Wikipedia'
    snippet = 'snippet'

    cursor.execute(
        'INSERT INTO page (uri, exprs, title, snippet) VALUES (%s, %s, %s, %s)',
        (uri_1, json.dumps(exprs), title, snippet)
        )

    uri_2 = 'uri2'
    result_uri_id = Cursor.select_uri_id_from_page_where_uri_1(cursor, uri_2)
    assert result_uri_id == None  # idの値は毎回異なるので，型の確認だけする


def test_select_json_search_uri_id_1_from_inverted_index_where_expr_2_1(cursor):
    """Cursor.select_json_search_uri_id_1_from_inverted_index_where_expr_2()のテスト．
    """
    mathml = '<math>a</math>'
    expr = Expression(mathml)
    uri_id = 2
    info = Info({
        "uri_id": ["1", str(uri_id), "3"],
        "lang": ["ja", "ja", "ja"],
        "expr_start_pos": [
            [40, 93, 279],
            [88, 267],
            [55, 123, 231]
        ]
    })

    query = """INSERT INTO inverted_index (expr, expr_len, info) VALUES (%(expr)s, %(len)s, %(info)s)"""
    data = {
            'expr': expr.mathml,
            'len': len(expr.mathml),
            'info': info.dumps()
    }

    cursor.execute(query, data)

    actual = Cursor.select_json_search_uri_id_1_from_inverted_index_where_expr_2(cursor, uri_id, expr)
    expected = '$.uri_id[1]'
    assert actual == expected


def test_update_index_1(cursor):
    """Cursor.update_index()のテスト。
    数式が未登録の場合。
    """
    mathml = '<math><mi>a</mi></math>'
    expr = Expression(mathml)
    info = Info({
        "uri_id": ["1"],
        "lang": ["ja"],
        "expr_start_pos": [
            [40, 93, 279]
        ]
    })
    expr_path_set = Parser.parse(expr)
    actual_expr_id, was_registered = Cursor.update_index(
        cursor, expr, len(expr_path_set), info
        )
    assert type(actual_expr_id) == int
    assert was_registered is False


def test_update_index_2(cursor):
    """Cursor.update_index()のテスト。
    数式が既に登録されていて、uri_idも登録されている場合。
    langとexpr_start_posが更新されることを確認。
    """
    mathml = '<math><mi>a</mi></math>'
    expr = Expression(mathml)
    info1 = Info({
        "uri_id": ["1"],
        "lang": ["ja"],
        "expr_start_pos": [
            [40, 93, 279]
        ]
    })
    expr_path_set = Parser.parse(expr)
    expr_id_1, was_registered_1 = Cursor.update_index(
        cursor, expr, len(expr_path_set), info1
        )
    assert type(expr_id_1) == int
    assert was_registered_1 is False

    info2 = Info({
        "uri_id": ["1"],
        "lang": ["en"],
        "expr_start_pos": [
            [77]
        ]
    })
    expr_id_2, was_registered_2 = Cursor.update_index(
        cursor, expr, len(expr_path_set), info2
        )
    assert expr_id_1 == expr_id_2
    assert was_registered_2 is True

    info_dict = Cursor.select_info_from_inverted_index_where_expr_id_1(cursor, expr_id_2)
    assert str(info2) == str(Info(info_dict))


def test_update_index_3(cursor):
    """Cursor.update_index()のテスト。
    数式が既に登録されていて、uri_idが未登録の場合。
    uri_id、lang、expr_start_posが追加されることを確認。
    """
    mathml = '<math><mi>a</mi></math>'
    expr = Expression(mathml)
    info1 = Info({
        "uri_id": ["1"],
        "lang": ["ja"],
        "expr_start_pos": [
            [40, 93, 279]
        ]
    })
    expr_path_set = Parser.parse(expr)
    expr_id_1, was_registered_1 = Cursor.update_index(
        cursor, expr, len(expr_path_set), info1
        )
    assert type(expr_id_1) == int
    assert was_registered_1 is False

    info2 = Info({
        "uri_id": ["2"],
        "lang": ["en"],
        "expr_start_pos": [
            [77]
        ]
    })
    expr_id_2, was_registered_2 = Cursor.update_index(
        cursor, expr, len(expr_path_set), info2
        )
    assert expr_id_1 == expr_id_2
    assert was_registered_2 is True

    expected_info = Info({
        "uri_id": ["1", "2"],
        "lang": ["ja", "en"],
        "expr_start_pos": [
            [40, 93, 279],
            [77]
        ]
    })
    info_dict = Cursor.select_info_from_inverted_index_where_expr_id_1(cursor, expr_id_2)
    assert str(expected_info) == str(Info(info_dict))


def test_update_inverted_index_set_info_1_where_expr_2(cursor):
    """Cursor.update_inverted_index_set_info_1_where_expr_2()のテスト．"""
    mathml = '<math>a</math>'
    expr = Expression(mathml)
    info = Info({
        "uri_id": ["1", "2"],
        "lang": ["ja", "ja"],
        "expr_start_pos": [
            [40, 93, 279],
            [88, 267]
        ]
    })

    query = """INSERT INTO inverted_index (expr, expr_len, info) VALUES (%(expr)s, %(len)s, %(info)s)"""
    data = {
            'expr': expr.mathml,
            'len': len(expr.mathml),
            'info': info.dumps()
    }

    cursor.execute(query, data)

    expected_info = Info({
        "uri_id": ["1", "2"],
        "lang": ["ja", "en"],
        "expr_start_pos": [
            [40, 93, 279],
            [88, 267]
        ]
    })
    Cursor.update_inverted_index_set_info_1_where_expr_2(cursor, expected_info.dumps(), expr)

    cursor.execute('SELECT info FROM inverted_index WHERE expr = %s', (expr.mathml,))
    actual_info = json.loads(cursor.fetchone()[0])
    assert str(Info(actual_info)) == str(expected_info)


def test_update_inverted_index_set_info_1_where_expr_id_2(cursor):
    """Cursor.update_inverted_index_set_info_1_where_expr_id_2()のテスト．"""
    mathml = '<math>a</math>'
    info = Info({
        "uri_id": ["1", "2"],
        "lang": ["ja", "ja"],
        "expr_start_pos": [
            [40, 93, 279],
            [88, 267]
        ]
    })

    query = """INSERT INTO inverted_index (expr, expr_len, info) VALUES (%(expr)s, %(len)s, %(info)s)"""
    data = {
            'expr': mathml,
            'len': len(mathml),
            'info': info.dumps()
    }

    cursor.execute(query, data)

    expected_info = Info({
        "uri_id": ["1", "2"],
        "lang": ["ja", "en"],
        "expr_start_pos": [
            [40, 93, 279],
            [88, 267]
        ]
    })

    cursor.execute('SELECT expr_id FROM inverted_index WHERE expr = %s', (mathml,))
    expr_id: int = cursor.fetchone()[0]
    Cursor.update_inverted_index_set_info_1_where_expr_id_2(cursor, expected_info.dumps(), expr_id)

    cursor.execute('SELECT info FROM inverted_index WHERE expr = %s', (mathml,))
    actual_info = json.loads(cursor.fetchone()[0])
    assert str(Info(actual_info)) == str(expected_info)


def test_update_page_set_exprs_title_snippet_where_uri_id_1(cursor):
    """Cursor.update_page_set_exprs_1_title_2_snippet_3_where_uri_id_4()のテスト．
    """
    uri = 'https://ja.wikipedia.org/wiki/%E7%B7%8F%E5%92%8C'
    exprs = ['expr1', 'expr2']
    title = '総和 - Wikipedia'
    snippet = 'snippet'

    # insert
    cursor.execute(
        'INSERT INTO page (uri, exprs, title, snippet) VALUES (%s, %s, %s, %s)',
        (uri, json.dumps(exprs), title, snippet)
        )

    # get uri_id
    cursor.execute('SELECT uri_id FROM page WHERE title = %s', (title,))
    uri_id = cursor.fetchone()[0]
    assert type(uri_id) == int

    # update
    new_exprs = [Expression('<math>new_expr1</math>'), Expression('<math>new_expr2</math>')]
    new_title = 'new title'
    new_snippet = Snippet('new snippet')
    Cursor.update_page_set_exprs_1_title_2_snippet_3_where_uri_id_4(cursor, new_exprs, new_title, new_snippet, uri_id)

    # check updated record
    cursor.execute('SELECT * FROM page WHERE uri_id = %s', (uri_id,))
    result = cursor.fetchone()
    result_uri = result[0]
    result_uri_id = result[1]
    result_exprs = json.loads(result[2])
    result_title = result[3]
    result_snippet = result[4]
    assert result_exprs == list(map(str, new_exprs))
    assert result_title == new_title
    assert result_snippet == new_snippet.text


def test_uri_is_already_registered_1(cursor):
    """Cursor.uri_is_already_registered()のテスト．
    """
    uri = 'https://ja.wikipedia.org/wiki/%E7%B7%8F%E5%92%8C'
    exprs = ['expr1', 'expr2']
    title = '総和 - Wikipedia'
    snippet = 'snippet'

    cursor.execute(
        'INSERT INTO page (uri, exprs, title, snippet) VALUES (%s, %s, %s, %s)',
        (uri, json.dumps(exprs), title, snippet)
        )

    # Trueの場合
    assert Cursor.uri_is_already_registered(cursor, uri) is True

    not_registered_uri = 'foo'
    # Falseの場合
    assert Cursor.uri_is_already_registered(cursor, not_registered_uri) is False
