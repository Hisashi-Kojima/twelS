# -*- coding: utf-8 -*-
"""module description
"""

import json
import os
from contextlib import contextmanager
from pathlib import Path

import environ
import mysql.connector

from twels.indexer.info import Info
from twels.snippet.snippet import Snippet

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(os.path.join(BASE_DIR.parent, '.env'))
env = environ.Env()


class Cursor:
    """Databaseと接続するためのクラス．
    """
    # TODO: connection_timeoutの適切な値を設定する
    # 開発用のデータベース
    config_for_dev = {
        'user': 'hisashi',
        'password': env('MY_HISASHI_PASSWORD'),
        'host': env('DB_CONTAINER_NAME'),  # MySQLのコンテナの名前で接続
        'database': env('MY_DB_NAME'),
        'port': 3306,
        'connection_timeout': 100  # second
    }

    # テスト用
    config_for_test = {
        'user': 'hisashi',
        'password': env('MY_HISASHI_PASSWORD'),
        'host': env('DB_TEST_CONTAINER_NAME'),  # MySQLのコンテナの名前で接続
        'database': env('MY_TEST_DB_NAME'),
        'port': 3306,  # container側のportは3306．
        'connection_timeout': 100  # second
    }

    @staticmethod
    def append_expr_id_if_not_registered(cursor, expr_id: int, expr_path: str, expr_size: int):
        """path_dictionaryのexpr_pathに対応するexpr_idsにexpr_idが未登録であれば登録する関数．
        """
        query = """
        CALL append_expr_id_if_not_registered(%(path)s, %(ids)s, %(id)s, %(size)s)
        """

        data = {
            'path': expr_path,
            'ids': json.dumps([str(expr_id)]),
            'id': str(expr_id),
            'size': expr_size
        }
        cursor.execute(query, data)

    @staticmethod
    def delete_from_inverted_index_where_expr_1(cursor, expr: str):
        """inverted_index tableのexprが一致するレコードを削除する関数．
        最大1つしか一致しないので，'LIMIT 1'を付けている．
        """
        cursor.execute('DELETE FROM inverted_index WHERE expr = %s LIMIT 1', (expr,))

    @staticmethod
    def delete_from_inverted_index_where_expr_id_1(cursor, expr_id: int):
        """inverted_index tableのexpr_idが一致するレコードを削除する関数．
        最大1つしか一致しないので，'LIMIT 1'を付けている．
        """
        cursor.execute('DELETE FROM inverted_index WHERE expr_id = %s LIMIT 1', (expr_id,))

    @staticmethod
    def delete_from_page_where_uri_id_1(cursor, uri_id: int):
        """page tableのuri_idが一致するレコードを削除する関数．
        最大1つしか一致しないので，'LIMIT 1'を付けている．
        """
        cursor.execute('DELETE FROM page WHERE uri_id = %s LIMIT 1', (uri_id,))

    @staticmethod
    def delete_from_path_dictionary_where_expr_path_1(cursor, expr_path: str, expr_size: int):
        """path_dictionary tableのexpr_pathが一致するレコードを削除する関数．
        最大1つしか一致しないので，'LIMIT 1'を付けている．
        """
        cursor.execute(
            'DELETE FROM path_dictionary WHERE expr_path = %s AND expr_size = %s LIMIT 1',
            (expr_path, expr_size)
            )

    @staticmethod
    def get_cleaned_path(path: str) -> str:
        """ '"$[2]"'のような文字列から無駄なダブルクォーテーションを削除して返す関数．
        """
        tmp = path[1:]
        return tmp[:-1]

    @staticmethod
    def insert_into_page_values_1_2_3_4(cursor, uri: str, exprs: list, title: str, snippet: Snippet):
        cursor.execute('INSERT INTO page (uri, exprs, title, snippet) VALUES (%s, %s, %s, %s)', (uri, json.dumps(exprs), title, str(snippet)))

    @staticmethod
    def remove_expr_id_from_path_dictionary(cursor, expr_id: int, expr_path: str, expr_size: int) -> list:
        """expr_idsから引数のexpr_idを削除する関数．
        Returns:
            expr_ids: 削除済みのexpr_ids
        Notes:
            expr_idsに登録されていないexpr_idが引数に指定された場合、
            expr_idsをそのまま返す。
        """
        query = """
        SELECT remove_expr_id_from_path_dictionary(%(expr_id)s, %(expr_path)s, %(expr_size)s)
        """
        data = {
            'expr_id': expr_id,
            'expr_path': expr_path,
            'expr_size': expr_size
        }
        cursor.execute(query, data)
        return json.loads(cursor.fetchone()[0])

    @staticmethod
    def remove_info_from_inverted_index(cursor, expr: str, uri_id: int) -> Info:
        """削除する数式とuri_idをもとにinverted_indexのinfoの該当箇所を削除する関数
        """
        query = """
        SELECT remove_info(%(expr)s, %(uri_id)s)
        """
        data = {
            'expr': expr,
            'uri_id': str(uri_id)
        }
        cursor.execute(query, data)
        info_dict: dict = json.loads(cursor.fetchone()[0])
        return Info(info_dict)

    @staticmethod
    def search(cursor, path_set: set[str]) -> list:
        """[['expr_id', degree of similarity], ...]を返す関数。
        e.g. [['10', 0.8], ['3', 0.7], ['23', 0.4]]
        """
        query = """
        SELECT search(%(path_set)s)
        """
        data = {
            'path_set': json.dumps(list(path_set))
        }
        cursor.execute(query, data)
        similarity = json.loads(cursor.fetchone()[0])
        sorted_similarity = sorted(similarity, key=lambda x: x[1], reverse=True)
        return sorted_similarity

    @staticmethod
    def select_all_from_index_where_expr_id_1(cursor, expr_id: int) -> tuple | None:
        cursor.execute('SELECT * FROM inverted_index WHERE expr_id = %s', (expr_id,))
        return cursor.fetchone()

    @staticmethod
    def select_all_from_page_where_uri_id_1(cursor, uri_id: int) -> tuple | None:
        cursor.execute('SELECT * FROM page WHERE uri_id = %s', (uri_id,))
        tpl = cursor.fetchone()
        if tpl is None:
            return None
        else:
            return tpl

    @staticmethod
    def select_expr_from_inverted_index_where_expr_id_1(cursor, expr_id: int) -> str | None:
        cursor.execute('SELECT expr FROM inverted_index WHERE expr_id = %s', (expr_id,))
        tpl = cursor.fetchone()
        if tpl is None:
            return None
        else:
            return tpl[0]

    @staticmethod
    def select_expr_id_from_inverted_index_where_expr_1(cursor, expr: str) -> int | None:
        cursor.execute('SELECT expr_id FROM inverted_index WHERE expr = %s', (expr,))
        tpl = cursor.fetchone()
        if tpl is None:
            return None
        else:
            return tpl[0]

    @staticmethod
    def select_info_from_inverted_index_where_expr_id_1(cursor, expr_id: int) -> dict[str, list[str]] | None:
        cursor.execute('SELECT info FROM inverted_index WHERE expr_id = %s', (expr_id,))
        tpl = cursor.fetchone()
        if tpl is None:
            return None
        else:
            return json.loads(tpl[0])

    @staticmethod
    def select_info_and_len_from_inverted_index_where_expr_id_1(cursor, expr_id: int) -> tuple[Info, int]:
        cursor.execute('SELECT info, expr_len FROM inverted_index WHERE expr_id = %s', (expr_id,))
        info_str, expr_len = cursor.fetchone()
        return Info(json.loads(info_str)), expr_len

    @staticmethod
    def select_uri_id_and_exprs_from_page_where_uri_1(cursor, uri: str) -> tuple[int, set[str]]:
        cursor.execute('SELECT uri_id, exprs FROM page WHERE uri = %s', (uri,))
        # type(exprs) is bytearray.
        uri_id, exprs = cursor.fetchone()
        return uri_id, set(json.loads(exprs))

    @staticmethod
    def select_uri_id_from_page_where_uri_1(cursor, uri: str) -> int | None:
        cursor.execute('SELECT uri_id FROM page WHERE uri = %s', (uri,))
        tpl = cursor.fetchone()
        if tpl is None:
            return None
        else:
            return tpl[0]

    @staticmethod
    def select_json_search_uri_id_1_from_inverted_index_where_expr_2(cursor, uri_id: int, expr: str) -> str | None:
        """inverted_indexのinfo内の指定されたuri_idへのpathを返す．
        TODO: inverted_index tableのinfo内にuri_id以外で数字を保存すると，この関数はそのpathを返してしまう．
              それへの対応．
        """
        cursor.execute(
                'SELECT JSON_SEARCH(info, "one", %s) FROM inverted_index WHERE expr = %s',
                (uri_id, expr)
                )
        json_path = cursor.fetchone()[0]
        if json_path is None:
            return None
        else:
            # '"$.uri_id[0]"'のような形になっているので，先頭と末尾の無駄なダブルクォーテーションを削除．
            return __class__.get_cleaned_path(json_path)

    @staticmethod
    def update_index(cursor, mathml: str, expr_size: int, info: Info) -> tuple[int, bool]:
        """inverted_index tableに問い合わせて，mathmlのexpr_idを取得する関数．
        数式が未登録の場合は，登録してexpr_idを取得する．
        数式が登録済みの場合は，infoを更新する．
        Args:
            info: 1ページ分のinfo。
        Returns:
            (expr_id, was_registered): was_registeredは数式が登録済みのときにTrueを返す．
        """
        query = """
        SELECT update_index(%(expr)s, %(expr_len)s, %(expr_size)s, %(info)s)
        """

        data = {
            'expr': mathml,
            'expr_len': len(mathml),
            'expr_size': expr_size,
            'info': info.dumps()
        }
        cursor.execute(query, data)
        d: dict = json.loads(cursor.fetchone()[0])
        return d['expr_id'], d['was_registered']

    @staticmethod
    def update_inverted_index_set_info_1_where_expr_2(cursor, info_json: str, expr: str):
        cursor.execute('UPDATE inverted_index SET info = %s WHERE expr = %s', (info_json, expr))

    @staticmethod
    def update_inverted_index_set_info_1_where_expr_id_2(cursor, info_json: str, expr_id: int):
        cursor.execute('UPDATE inverted_index SET info = %s WHERE expr_id = %s', (info_json, expr_id))

    @staticmethod
    def update_page_set_exprs_1_title_2_snippet_3_where_uri_id_4(cursor, exprs: list, title: str, snippet: Snippet, uri_id):
        cursor.execute('UPDATE page SET exprs = %s, title = %s, snippet = %s WHERE uri_id = %s', (json.dumps(exprs), title, str(snippet), uri_id))

    @staticmethod
    def uri_is_already_registered(cursor, uri: str) -> bool:
        """page tableに指定したuriのレコードがあればTrueを返す関数．
        """
        cursor.execute('SELECT * FROM page WHERE uri = %s LIMIT 1', (uri,))
        return cursor.fetchone() is not None

    @contextmanager
    def connect(test: bool = False):
        """データベースに接続してconnectionを返す関数．エラーが発生してもちゃんとclose()する．
        Args:
            test: testのときにはTrueにする．
        """
        # enter method
        if test:
            cnx = mysql.connector.connect(**__class__.config_for_test)
        else:
            cnx = mysql.connector.connect(**__class__.config_for_dev)
        yield cnx
        cnx.close()  # exit method

    @contextmanager
    def cursor(cnx):
        """cursorを返す関数．エラーが発生してもちゃんとclose()する．
        """
        # TODO: 可能であればPrepared Statementにする．
        c = cnx.cursor()
        yield c
        c.close()  # exit method
