# -*- coding: utf-8 -*-
"""module description
made by Hisashi
"""

import traceback

from itemadapter import ItemAdapter
from lark import exceptions

from twels.database.cursor import Cursor
from twels.expr.parser import Parser
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
            # そのページが数式を含まないとき
            if not page_info['exprs']:
                with Cursor.connect(test) as cnx:
                    with Cursor.cursor(cnx) as cursor:
                        uri_id, delete_set = Cursor.select_uri_id_and_exprs_from_page_where_uri_1(cursor, page_info['uri'])
                        # そのページが登録されていたとき
                        if uri_id is not None:
                            # 数式がないページでも，以前はそのページに数式があったかもしれない．
                            # なので，そのページがpage tableに登録されていたら，そのページを削除．
                            Cursor.delete_from_page_where_uri_id_1(cursor, uri_id)
                            # 登録されていた数式をもとにinverted_indexやpath_dictionaryを更新．
                            __class__._delete_expr_from_database_with_delete_set(uri_id, delete_set, test=test)
                return True

            uri_id, registered_exprs = __class__._update_page_table(page_info, test=test)
            __class__._update_index_and_path_table(uri_id, registered_exprs, page_info, test=test)
            return True
        except Exception as e:
            print_in_red(f'error in indexer.update_db(). {e}')
            traceback.print_exc()
            return False

    @staticmethod
    def _check_expr_id(mathml: str, uri_id: int, lang: str, test: bool = False) -> tuple[int, bool]:
        """inverted_index tableに問い合わせて，mathmlのexpr_idを取得する関数．
        数式が未登録の場合は，登録してexpr_idを取得する．
        数式が登録済みの場合は，infoを更新する．
        Returns:
            (expr_id, was_registered): was_registeredは数式が登録済みのときにTrueを返す．
        """
        with Cursor.connect(test) as cnx:
            with Cursor.cursor(cnx) as cursor:
                expr_id = Cursor.select_expr_id_from_inverted_index_where_expr_1(cursor, mathml)
                if expr_id is None:
                    Cursor.insert_into_index_values_1_2(cursor, mathml, uri_id, lang)
                    cnx.commit()
                    expr_id = Cursor.select_expr_id_from_inverted_index_where_expr_1(cursor, mathml)
                    return expr_id, False
                else:
                    # 登録済みの場合にはinfoを更新する．
                    __class__._update_index_table(cursor, uri_id, lang, expr_id)
                    cnx.commit()
                    return expr_id, True

    @staticmethod
    def _delete_expr_from_database(cursor, mathml: str, uri_id: int, test: bool = False) -> bool:
        """数式(MathML)をデータベースから削除する関数．
        tableはinverted_index, path_dictionaryを操作する．
        Returns:
            削除に成功したらTrue，失敗したらFalseを返す．
        """
        # 削除対象の数式とuri_idをもとにinverted_indexのinfoの該当箇所を削除．
        info = Cursor.remove_info_from_inverted_index(cursor, mathml, uri_id)

        # path_dictionaryの操作時にexpr_idが必要なので，ここで取得．
        expr_id = Cursor.select_expr_id_from_inverted_index_where_expr_1(cursor, mathml)
        if not info['uri_id']:
            # infoが空になった場合，そのexpr_idのレコードをinverted_index tableから削除．
            Cursor.delete_from_inverted_index_where_expr_id_1(cursor, expr_id)

            # その数式のpathそれぞれとexpr_idがセットでpath_dictionaryに登録されているので，削除．
            try:
                expr_path_set = Parser.parse(mathml)
                for expr_path in expr_path_set:
                    expr_ids = Cursor.remove_expr_id_from_path_dictionary(cursor, expr_id, expr_path)
                    if not expr_ids:
                        # そのpathのexpr_idsが空になったら，そのpathのレコードを削除．
                        Cursor.delete_from_path_dictionary_where_expr_path_1(cursor, expr_path)
                return True
            except exceptions.LarkError as e:
                print_in_red(f'error in indexer._delete_expr_from_database(). {e}')
                traceback.print_exc()
                return False

    @staticmethod
    def _delete_expr_from_database_with_delete_set(uri_id: int, delete_set: set[str], test: bool = False):
        """Indexer._delete_expr_from_database()をwrapしたmethod．
        tableはinverted_index, path_dictionaryを操作する．
        """
        for mathml in delete_set:
            with Cursor.connect(test) as cnx:
                with Cursor.cursor(cnx) as cursor:
                    __class__._delete_expr_from_database(cursor, mathml, uri_id, test=test)
                    cnx.commit()

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
    def _update_index_table(cursor, uri_id: int, lang: str, expr_id: int):
        """inverted_index tableを更新する関数．"""
        uri_id_path = Cursor.select_json_search_uri_id_1_from_inverted_index_where_expr_id_2(cursor, uri_id, expr_id)
        if uri_id_path is None:
            # infoにuri_idがなければuri_idとlangをappend
            Cursor.select_json_array_append_uri_id(cursor, uri_id, expr_id)
            Cursor.select_json_array_append_lang(cursor, lang, expr_id)
        else:
            # infoにuri_idがあればlangを更新する．
            lang_path = uri_id_path.replace('uri_id', 'lang')
            Cursor.select_json_replace_info(cursor, lang_path, lang, expr_id)

    @staticmethod
    def _update_index_and_path_table(uri_id: int, registered_exprs: set, page_info: ItemAdapter, test: bool = False):
        """inverted_index table, path_dictionary tableを更新する関数．
        最初に新たな式を追加して，その後に古い式を削除する．
        Args:
            uri_id: そのページのuri id
            registered_exprs: そのページに登録されている式のMathMLの集合
            page_info: uriなど，そのページの情報
        """
        insert_set, delete_set = __class__._get_insert_and_delete_set(set(page_info['exprs']), registered_exprs)

        for mathml in insert_set:
            expr_id, was_registered = __class__._check_expr_id(mathml, uri_id, page_info['lang'], test=test)
            try:
                if not was_registered:
                    expr_path_set = Parser.parse(mathml)
                    with Cursor.connect(test) as cnx:
                        with Cursor.cursor(cnx) as cursor:
                            for path in expr_path_set:
                                Cursor.append_expr_id_if_not_registered(cursor, expr_id, path)
                            cnx.commit()
            except exceptions.LarkError as e:
                print_in_red(f'error in indexer._update_index_and_path_table(). {e}')
                traceback.print_exc()

        __class__._delete_expr_from_database_with_delete_set(uri_id, delete_set, test=test)

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
                    Cursor.update_page_set_exprs_1_title_2_descr_3_where_uri_id_4(cursor, page_info['exprs'], page_info['title'], page_info['descr'], uri_id)
                    cnx.commit()
                    return uri_id, registered_exprs
                else:
                    # レコードが存在しなかったら，新しい情報を登録して，uri_idを取得する．
                    Cursor.insert_into_page_values_1_2_3_4(cursor, page_info['uri'], page_info['exprs'], page_info['title'], page_info['descr'])
                    uri_id = Cursor.select_uri_id_from_page_where_uri_1(cursor, page_info['uri'])
                    cnx.commit()
                    return uri_id, set()
