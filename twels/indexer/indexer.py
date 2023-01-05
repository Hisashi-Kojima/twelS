# -*- coding: utf-8 -*-
"""module description
"""

import traceback

from itemadapter import ItemAdapter
from lark import exceptions

from twels.database.cursor import Cursor
from twels.expr.parser import Parser
from twels.indexer.info import Info
from twels.snippet.snippet import Snippet
from twels.utils.utils import print_in_red


class Indexer:

    @staticmethod
    def update_db(page_info: ItemAdapter, test: bool = False) -> bool:
        """データベースの情報を更新する関数．
        Args:
            page_info: ページについての情報を持つオブジェクト．
            test: testのときにはTrueにする．
        Returns:
            データベースの情報の更新に成功したらTrueを返す．
        """
        try:
            is_success = True
            # そのページが数式を含まないとき
            if not page_info['exprs']:
                with Cursor.connect(test) as cnx:
                    with Cursor.cursor(cnx) as cursor:
                        uri_id, delete_set = Cursor.select_uri_id_and_exprs_from_page_where_uri_1(cursor, page_info['uri'])
                # そのページが登録されていたとき
                if uri_id is not None:
                    # 数式がないページでも，以前はそのページに数式があったかもしれない．
                    # なので，そのページがpage tableに登録されていたら，そのページを削除．
                    with Cursor.connect(test) as cnx:
                        with Cursor.cursor(cnx) as cursor:
                            Cursor.delete_from_page_where_uri_id_1(cursor, uri_id)
                            cnx.commit()
                    # 登録されていた数式をもとにinverted_indexやpath_dictionaryを更新．
                    is_success = __class__._delete_expr_from_database_with_delete_set(uri_id, delete_set, test=test)
                return is_success

            uri_id, registered_exprs = __class__._update_page_table(page_info, test=test)
            is_success = __class__._update_index_and_path_table(uri_id, registered_exprs, page_info, test=test)
            return is_success
        except Exception as e:
            print_in_red(f'error in indexer.update_db(). {e}')
            traceback.print_exc()
            return False

    @staticmethod
    def _delete_expr_from_database(cursor, mathml: str, uri_id: int, test: bool = False) -> bool:
        """数式(MathML)をデータベースから削除する関数．
        tableはinverted_index, path_dictionaryを操作する．
        Returns:
            削除に成功したらTrue，失敗したらFalseを返す．
        """
        try:
            # 削除対象の数式とuri_idをもとにinverted_indexのinfoの該当箇所を削除．
            info = Cursor.remove_info_from_inverted_index(cursor, mathml, uri_id)

            if info.is_empty():
                # path_dictionaryの操作時にexpr_idが必要なので，ここで取得．
                expr_id = Cursor.select_expr_id_from_inverted_index_where_expr_1(cursor, mathml)

                # infoが空になった場合，そのexpr_idのレコードをinverted_index tableから削除．
                Cursor.delete_from_inverted_index_where_expr_id_1(cursor, expr_id)

                # その数式のpathそれぞれとexpr_idがセットでpath_dictionaryに登録されているので，削除．
                expr_path_set = Parser.parse(mathml)
                expr_size = len(expr_path_set)
                for expr_path in expr_path_set:
                    expr_ids = Cursor.remove_expr_id_from_path_dictionary(cursor, expr_id, expr_path, expr_size)
                    if not expr_ids:
                        # そのpathのexpr_idsが空になったら，そのpathのレコードを削除．
                        Cursor.delete_from_path_dictionary_where_expr_path_1(cursor, expr_path, expr_size)
            return True
        except exceptions.LarkError as e:
            print_in_red(f'error in indexer._delete_expr_from_database(). {e}')
            traceback.print_exc()
            return False
        except Exception as e:
            print_in_red(f'error in indexer._delete_expr_from_database(). {e}')
            traceback.print_exc()
            return False

    @staticmethod
    def _delete_expr_from_database_with_delete_set(uri_id: int, delete_set: set[str], test: bool = False) -> bool:
        """Indexer._delete_expr_from_database()をwrapしたmethod．
        tableはinverted_index, path_dictionaryを操作する．
        Returns:
            削除に成功したらTrue，失敗したらFalseを返す．
        """
        delete_success = True
        # TODO: delete_successがTrueとFalse何度も切り替わる場合が考えられるので、
        #       それの対応を決める。
        try:
            for mathml in delete_set:
                with Cursor.connect(test) as cnx:
                    with Cursor.cursor(cnx) as cursor:
                        delete_success = __class__._delete_expr_from_database(cursor, mathml, uri_id, test=test)
                        cnx.commit()
            return delete_success
        except Exception as e:
            print_in_red(f'error in indexer._delete_expr_from_database_with_delete_set(). {e}')
            traceback.print_exc()
            return False

    @staticmethod
    def _get_insert_and_delete_set(new_exprs: set, registered_exprs: set) -> tuple[set[str], set[str]]:
        """登録する数式と削除する数式それぞれの集合を返す関数．
        そのページに登録されていたexpressionsと今回取得したexpressionsを比較することで，
        新たに登録するexprと削除するexprがわかる．
        Args:
            new_exprs: 今回取得したexpressions
            registered_exprs: そのページに登録されていたexpressions
        Returns:
            (insert_set, delete_set): 登録する数式の集合と削除する数式の集合のタプル．
        """
        insert_set = new_exprs - registered_exprs
        delete_set = registered_exprs - new_exprs
        return insert_set, delete_set

    @staticmethod
    def _update_index_and_path_table(uri_id: int, registered_exprs: set, page_info: ItemAdapter, test: bool = False) -> bool:
        """inverted_index table, path_dictionary tableを更新する関数．
        最初に新たな式を追加して，その後に古い式を削除する．
        Args:
            uri_id: そのページのuri id
            registered_exprs: そのページに登録されている式のMathMLの集合
            page_info: uriなど，そのページの情報
        Returns:
            更新に成功したらTrue、失敗したらFalseを返す。
        """
        insert_set, delete_set = __class__._get_insert_and_delete_set(set(page_info['exprs']), registered_exprs)
        snippet: Snippet = page_info['snippet']

        try:
            for mathml in insert_set:
                expr_start_pos_list = [snippet.search_expr_start_pos(mathml)]
                info = Info({
                    "uri_id": [str(uri_id)],
                    "lang": [page_info['lang']],
                    "expr_start_pos": expr_start_pos_list
                })

                expr_path_set = Parser.parse(mathml)
                expr_size = len(expr_path_set)
                with Cursor.connect(test) as cnx:
                    with Cursor.cursor(cnx) as cursor:
                        expr_id, was_registered = Cursor.update_index(
                            cursor, mathml, len(expr_path_set), info
                            )
                        if not was_registered:
                            for path in expr_path_set:
                                Cursor.append_expr_id_if_not_registered(
                                    cursor, expr_id, path, expr_size
                                    )
                        cnx.commit()

            return __class__._delete_expr_from_database_with_delete_set(uri_id, delete_set, test=test)
        except exceptions.LarkError as e:
            print_in_red(f'error in indexer._update_index_and_path_table(). {e}')
            traceback.print_exc()
            return False
        except Exception as e:
            print_in_red(f'error in indexer._update_index_and_path_table(). {e}')
            traceback.print_exc()
            return False

    @staticmethod
    def _update_page_table(page_info: ItemAdapter, test: bool = False) -> tuple[int, set]:
        """page tableを更新する関数．
        そのページのuri_idと登録されているexprsを返す．
        Returns:
            (uri_id, registered_exprs)
        """
        with Cursor.connect(test) as cnx:
            with Cursor.cursor(cnx) as cursor:
                if Cursor.uri_is_already_registered(cursor, page_info['uri']):
                    # DBに登録されているuri_idとexpressionsを取得して，そのレコードの情報を新しい情報に更新する．
                    # 取得した登録されているexprsは，今回スクレイプしたexprsと比較するために使う．
                    uri_id, registered_exprs = Cursor.select_uri_id_and_exprs_from_page_where_uri_1(cursor, page_info['uri'])
                    Cursor.update_page_set_exprs_1_title_2_snippet_3_where_uri_id_4(cursor, page_info['exprs'], page_info['title'], page_info['snippet'], uri_id)
                    cnx.commit()
                    return uri_id, registered_exprs
                else:
                    # レコードが存在しなかったら，新しい情報を登録して，uri_idを取得する．
                    Cursor.insert_into_page_values_1_2_3_4(cursor, page_info['uri'], page_info['exprs'], page_info['title'], page_info['snippet'])
                    uri_id = Cursor.select_uri_id_from_page_where_uri_1(cursor, page_info['uri'])
                    cnx.commit()
                    return uri_id, set()
