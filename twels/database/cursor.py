# -*- coding: utf-8 -*-
"""module description
made by Hisashi
"""

import json
import os
from contextlib import contextmanager
from pathlib import Path

import environ
import mysql.connector

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(os.path.join(BASE_DIR.parent, '.env'))
env = environ.Env()

environ.Env.read_env(os.path.join(BASE_DIR.parent, '.env.test'))
test_env = environ.Env()


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
        'password': test_env('MY_HISASHI_PASSWORD'),
        'host': test_env('DB_TEST_CONTAINER_NAME'),  # MySQLのコンテナの名前で接続
        'database': test_env('MY_TEST_DB_NAME'),
        'port': 3306,  # container側のportは3306．
        'connection_timeout': 100  # second
    }

    @staticmethod
    def append_expr_id_if_not_registered(cursor, expr_id: int, expr_path: str):
        """path_dictionaryのexpr_pathに対応するexpr_idsにexpr_idが未登録であれば登録する関数．
        Returns:
            expr_ids: expr_idのjson．
        """
        # TODO: この関数をもっと効率よくできそう
        tpl = __class__.select_all_from_path_dict_where_expr_path_1(cursor, expr_path)
        # path_dictionaryにexpr_pathがまだ登録されていない場合
        if tpl is None:
            __class__.insert_into_path_dictionary_values_1_2(cursor, expr_path, expr_id)
            return __class__.select_expr_ids_from_path_dictionary_where_expr_path_1(cursor, expr_path)
        else:
            id_path = __class__.select_json_search_expr_ids_1_from_path_dict_where_expr_path_2(cursor, expr_id, expr_path)
            if id_path is None:
                # expr_idが未登録のとき
                return __class__.select_json_array_append_expr_ids_where_expr_path_2(cursor, expr_id, expr_path)
            else:
                return __class__.select_expr_ids_from_path_dictionary_where_expr_path_1(cursor, expr_path)

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
    def delete_from_path_dictionary_where_expr_path_1(cursor, expr_path: str):
        """path_dictionary tableのexpr_pathが一致するレコードを削除する関数．
        最大1つしか一致しないので，'LIMIT 1'を付けている．
        """
        cursor.execute('DELETE FROM path_dictionary WHERE expr_path = %s LIMIT 1', (expr_path,))

    @staticmethod
    def get_cleaned_path(path: str) -> str:
        """ '"$[2]"'のような文字列から無駄なダブルクォーテーションを削除して返す関数．
        """
        tmp = path[1:]
        return tmp[:-1]

    @staticmethod
    def insert_into_index_values_1_2(cursor, expr: str, uri_id: int, lang: str):
        cursor.execute(
            'INSERT INTO inverted_index (expr, info) VALUES (%s, JSON_OBJECT("uri_id", JSON_ARRAY(%s), "lang", JSON_ARRAY(%s)))',
            (expr, str(uri_id), lang)
            )

    @staticmethod
    def insert_into_page_values_1_2_3_4(cursor, uri: str, exprs: list, title: str, descr: str):
        cursor.execute('INSERT INTO page (uri, exprs, title, descr) VALUES (%s, %s, %s, %s)', (uri, json.dumps(exprs), title, descr))

    @staticmethod
    def insert_into_path_dictionary_values_1_2(cursor, expr_path: str, expr_id: int):
        cursor.execute('INSERT INTO path_dictionary (expr_path, expr_ids) VALUES (%s, %s)', (expr_path, json.dumps([str(expr_id)])))

    @staticmethod
    def remove_expr_id_from_path_dictionary(cursor, expr_id: int, expr_path: str) -> list:
        """expr_idsから引数のexpr_idを削除する関数．
        Returns:
            expr_ids: 削除済みのexpr_ids
        """
        remove_path = __class__.select_json_search_expr_ids_1_from_path_dict_where_expr_path_2(cursor, expr_id, expr_path)
        cursor.execute('SELECT JSON_REMOVE(expr_ids, %s) FROM path_dictionary', (remove_path,))
        expr_ids_json = cursor.fetchone()[0]
        __class__.update_path_dictionary_set_expr_ids_1_where_expr_path_2(cursor, expr_ids_json, expr_path)
        return json.loads(expr_ids_json)

    @staticmethod
    def remove_info_from_inverted_index(cursor, expr: str, uri_id: int) -> dict[str, list[str]]:
        """削除する数式とuri_idをもとにinverted_indexのinfoの該当箇所を削除する関数"""
        uri_id_path = __class__.select_json_search_uri_id_1_from_inverted_index_where_expr_2(cursor, uri_id, expr)
        cursor.execute('SELECT JSON_REMOVE(info, %s) FROM inverted_index', (uri_id_path,))
        remove_uri_id_info = json.loads(cursor.fetchone()[0])

        lang_path = uri_id_path.replace('uri_id', 'lang')
        cursor.execute('SELECT JSON_REMOVE(info, %s) FROM inverted_index', (lang_path,))
        remove_lang_info = json.loads(cursor.fetchone()[0])

        # merge
        result_dict = {"uri_id": [], "lang": []}
        result_dict['uri_id'] = remove_uri_id_info['uri_id']
        result_dict['lang'] = remove_lang_info['lang']
        __class__.update_inverted_index_set_info_1_where_expr_2(cursor, json.dumps(result_dict), expr)
        return result_dict

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
    def select_all_from_path_dict_where_expr_path_1(cursor, expr_path: str) -> tuple | None:
        cursor.execute('SELECT * FROM path_dictionary WHERE expr_path = %s', (expr_path,))
        return cursor.fetchone()

    @staticmethod
    def select_expr_id_from_inverted_index_where_expr_1(cursor, expr: str) -> int | None:
        cursor.execute('SELECT expr_id FROM inverted_index WHERE expr = %s', (expr,))
        tpl = cursor.fetchone()
        if tpl is None:
            return None
        else:
            return tpl[0]

    @staticmethod
    def select_expr_ids_from_path_dictionary_where_expr_path_1(cursor, expr_path: str) -> list[str] | None:
        cursor.execute('SELECT expr_ids FROM path_dictionary WHERE expr_path = %s', (expr_path,))
        tpl = cursor.fetchone()
        if tpl is None:
            return None
        else:
            return json.loads(tpl[0])

    @staticmethod
    def select_info_from_inverted_index_where_expr_id_1(cursor, expr_id: int) -> dict[str, list[str]] | None:
        cursor.execute('SELECT info FROM inverted_index WHERE expr_id = %s', (expr_id,))
        tpl = cursor.fetchone()
        if tpl is None:
            return None
        else:
            return json.loads(tpl[0])

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
    def select_json_array_append_expr_ids_where_expr_path_2(cursor, expr_id: int, expr_path: str):
        """expr_idsの末尾に引数のexpr_idを追加する関数．
        """
        cursor.execute(
            'SELECT JSON_ARRAY_APPEND(expr_ids, "$", %s) FROM path_dictionary WHERE expr_path = %s',
            (str(expr_id), expr_path)
            )
        expr_ids_json = cursor.fetchone()[0]
        __class__.update_path_dictionary_set_expr_ids_1_where_expr_path_2(cursor, expr_ids_json, expr_path)
        return json.loads(expr_ids_json)

    @staticmethod
    def select_json_array_append_lang(cursor, lang: str, expr_id: int) -> dict:
        """inverted_indexのinfoのlangの末尾に引数のlangを追加する関数．
        """
        cursor.execute(
            'SELECT JSON_ARRAY_APPEND(info, "$.lang", %s) FROM inverted_index WHERE expr_id = %s',
            (lang, expr_id)
            )
        # langがappendされたレコード
        info_json = cursor.fetchone()[0]
        __class__.update_inverted_index_set_info_1_where_expr_id_2(cursor, info_json, expr_id)
        return json.loads(info_json)

    @staticmethod
    def select_json_array_append_uri_id(cursor, uri_id: int, expr_id: int) -> dict:
        """inverted_indexのinfoのlangの末尾に引数のuri_idを追加する関数．
        """
        cursor.execute(
            'SELECT JSON_ARRAY_APPEND(info, "$.uri_id", %s) FROM inverted_index WHERE expr_id = %s',
            (str(uri_id), expr_id)
            )
        # uri_idがappendされたレコード
        info_json = cursor.fetchone()[0]
        __class__.update_inverted_index_set_info_1_where_expr_id_2(cursor, info_json, expr_id)
        return json.loads(info_json)

    @staticmethod
    def select_json_replace_info(cursor, path: str, value: str, expr_id: int) -> dict:
        """infoの要素を置換する関数．
        Args:
            path: 置換先のpath．
            value: 置き換える値．uri_idかlangを想定．
        Returns:
            置換後のinfo．
        """
        cursor.execute(
            'SELECT JSON_REPLACE(info, %s, %s) FROM inverted_index WHERE expr_id = %s',
            (path, value, expr_id)
            )
        info_json = cursor.fetchone()[0]
        __class__.update_inverted_index_set_info_1_where_expr_id_2(cursor, info_json, expr_id)
        return json.loads(info_json)

    @staticmethod
    def select_json_search_expr_ids_1_from_path_dict_where_expr_path_2(cursor, expr_id: int, expr_path: str) -> str | None:
        """path_dictionaryのexpr_ids内の指定されたexpr_idへのpathを返す"""
        cursor.execute('SELECT JSON_SEARCH(expr_ids, "one", %s) FROM path_dictionary WHERE expr_path = %s', (str(expr_id), expr_path))
        json_path = cursor.fetchone()[0]
        if json_path is None:
            return None
        else:
            # '"$[2]"'のような形になっているので，先頭と末尾の無駄なダブルクォーテーションを削除．
            return __class__.get_cleaned_path(json_path)

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
    def select_json_search_uri_id_1_from_inverted_index_where_expr_id_2(cursor, uri_id: int, expr_id: int) -> str | None:
        """inverted_indexのinfo内の指定されたuri_idへのpathを返す．
        TODO: inverted_index tableのinfo内にuri_id以外で数字を保存すると，この関数はそのpathを返してしまう．
              それへの対応．
        """
        cursor.execute(
                'SELECT JSON_SEARCH(info, "one", %s) FROM inverted_index WHERE expr_id = %s',
                (uri_id, expr_id)
                )
        json_path = cursor.fetchone()[0]
        if json_path is None:
            return None
        else:
            # '"$.uri_id[0]"'のような形になっているので，先頭と末尾の無駄なダブルクォーテーションを削除．
            return __class__.get_cleaned_path(json_path)

    @staticmethod
    def update_inverted_index_set_info_1_where_expr_2(cursor, info_json: str, expr: str):
        cursor.execute('UPDATE inverted_index SET info = %s WHERE expr = %s', (info_json, expr))

    @staticmethod
    def update_inverted_index_set_info_1_where_expr_id_2(cursor, info_json: str, expr_id: int):
        cursor.execute('UPDATE inverted_index SET info = %s WHERE expr_id = %s', (info_json, expr_id))

    @staticmethod
    def update_page_set_exprs_1_title_2_descr_3_where_uri_id_4(cursor, exprs: list, title: str, descr: str, uri_id):
        cursor.execute('UPDATE page SET exprs = %s, title = %s, descr = %s WHERE uri_id = %s', (json.dumps(exprs), title, descr, uri_id))

    @staticmethod
    def update_path_dictionary_set_expr_ids_1_where_expr_path_2(cursor, expr_ids_json: str, expr_path: str):
        cursor.execute('UPDATE path_dictionary SET expr_ids = %s WHERE expr_path = %s', (expr_ids_json, expr_path))

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
