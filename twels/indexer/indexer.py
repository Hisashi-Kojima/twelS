# -*- coding: utf-8 -*-
"""module description
made by Hisashi
"""

import traceback

from itemadapter import ItemAdapter
from lark import exceptions

from twelS.database.cursor import Cursor
from twelS.expr.parser import Parser
from twelS.utils.utils import print_in_red


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
                            # 登録されていた数式をもとにinverted_indexやpath_dictionary，expressionを更新．
                            __class__._delete_expr_from_database_with_delete_set(uri_id, delete_set, test=test)
                return True

            uri_id, registered_exprs = __class__._update_page_table(page_info, test=test)
            __class__._update_index_and_path_and_expr_table(uri_id, registered_exprs, page_info, test=test)
            return True
        except Exception as e:
            print_in_red(f'error in indexer.update_db(). {e}')
            traceback.print_exc()
            return False

    @staticmethod
    def _delete_expr_from_database(cursor, mathml: str, uri_id: int, test: bool = False) -> bool:
        """数式(MathML)をデータベースから削除する関数．
        tableはinverted_index, path_dictionary, expressionを操作する．
        Returns:
            削除に成功したらTrue，失敗したらFalseを返す．
        """
        expr_id = __class__._get_expr_id(mathml, test=test)

        # 削除する数式のexpr_idとuri_idをもとにinverted_indexのinfoの該当箇所を削除．
        info = Cursor.remove_info_from_inverted_index(cursor, expr_id, uri_id)

        if not info['uri_id']:
            # infoが空になった場合，そのexpr_idのレコードをinverted_index tableとexpression tableから削除．
            Cursor.delete_from_inverted_index_where_expr_id_1(cursor, expr_id)
            Cursor.delete_from_expression_where_expr_id_1(cursor, expr_id)

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
        tableはinverted_index, path_dictionary, expressionを操作する．
        """
        for mathml in delete_set:
            with Cursor.connect(test) as cnx:
                with Cursor.cursor(cnx) as cursor:
                    __class__._delete_expr_from_database(cursor, mathml, uri_id, test=test)
                    cnx.commit()

    @staticmethod
    def _get_expr_id(mathml: str, test: bool = False) -> int:
        """expression tableに問い合わせて，mathmlのexpr_idを取得する関数．
        数式が未登録の場合は，登録してexpr_idを取得する．
        """
        with Cursor.connect(test) as cnx:
            with Cursor.cursor(cnx) as cursor:
                expr_id = Cursor.select_expr_id_from_expression_where_expr_1(cursor, mathml)
                if expr_id is None:
                    Cursor.insert_into_expr_values_1(cursor, mathml)
                    expr_id = Cursor.select_expr_id_from_expression_where_expr_1(cursor, mathml)
                cnx.commit()
                return expr_id

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
    def _insert_expr_into_database(cursor, expr_path_set: set, expr_id: int, uri_id: int, lang: str):
        """数式の情報をデータベースに登録する関数．
        path_dictinoary tableとinverted_index tableを操作する．
        Returns:
            info(dict): inverted_indexのinfo.
        """
        for path in expr_path_set:
            # 必要があれば，expr_idとpathをpath_dictionaryに追記する．
            Cursor.append_expr_id_if_not_registered(cursor, expr_id, path)
        # 必要があれば，expr_idをもとにinverted_index tableに追記する．
        # inverted_index tableにはexpr_idとそのpageのuri_id, langを登録．
        return Cursor.insert_into_index_values_expr_id_and_info(cursor, expr_id, uri_id, lang)

    @staticmethod
    def _update_index_and_path_and_expr_table(uri_id: int, registered_exprs: set, page_info: ItemAdapter, test: bool = False):
        """inverted_index table, path_dictionary table, expression tableを更新する関数．
        最初に新たな式を追加して，その後に古い式を削除する．
        Args:
            uri_id: そのページのuri id
            registered_exprs: そのページに登録されている式のMathMLの集合
            page_info: uriなど，そのページの情報
        """
        insert_set, delete_set = __class__._get_insert_and_delete_set(set(page_info['exprs']), registered_exprs)

        for mathml in insert_set:
            expr_id = __class__._get_expr_id(mathml)
            try:
                expr_path_set = Parser.parse(mathml)
                with Cursor.connect(test) as cnx:
                    with Cursor.cursor(cnx) as cursor:
                        __class__._insert_expr_into_database(cursor, expr_path_set, expr_id, uri_id, page_info['lang'])
                        cnx.commit()
            except exceptions.LarkError as e:
                print_in_red(f'error in indexer._update_index_and_path_and_expr_table(). {e}')
                traceback.print_exc()

        __class__._delete_expr_from_database_with_delete_set(uri_id, delete_set, test=test)

    @staticmethod
    def _update_page_table(page_info: ItemAdapter, test: bool = False) -> tuple[int, set]:
        """page tableを更新する関数．
        そのページのuri_idと登録されているexpressionsを返す．
        Returns:
            (uri_id, expressions)
        """
        with Cursor.connect(test) as cnx:
            with Cursor.cursor(cnx) as cursor:
                if Cursor.uri_is_already_registered(cursor, page_info['uri']):
                    # DBに登録されているuri_idとexpressionsを取得して，そのレコードの情報を新しい情報に更新する．
                    # 取得した登録されているexpressionsは，今回スクレイプしたexpressionsと比較するために使う．
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
