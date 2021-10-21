# -*- coding: utf-8 -*-
"""module description
made by Hisashi
"""

import collections
import itertools
from concurrent import futures

import latex2mathml.converter
from lark import exceptions

from expr.parser import Parser
from database.cursor import Cursor
from utils.utils import print_in_red
from .descr_formatter import DescrFormatter


class Searcher:
    """データベースに接続し，検索結果を取得するためのクラス．
    """
    @staticmethod
    def search(expr: str) -> dict:
        """
        Args:
            expr: 検索する式．
        Returns:
            {'search_result': search_result, 'result_num': result_num}
        """
        # LaTeX -> MathML -> Tree (-> Normalize) -> path set
        try:
            path_set: set[str] = Parser.parse(latex2mathml.converter.convert(expr))
            sorted_expr_ids = __class__._get_expr_ids(path_set)
            extracted_ids = __class__._extract_ids_from_sorted_expr_ids(sorted_expr_ids)
            info = __class__._get_info(extracted_ids)
            search_result = __class__._get_search_result(info, extracted_ids)
            result = {
                'search_result': search_result,
                'result_num': len(info['uri_id'])
                }
        except exceptions.LarkError:
            result = {
                'search_result': [],
                'result_num': 0
            }
        return result

    @staticmethod
    def _extract_ids_from_sorted_expr_ids(sorted_expr_ids: list[tuple[str, int]]) -> list[str]:
        """sorted_expr_idsからいくつかのidだけを取得する関数．
        Args:
            sorted_expr_ids: ("expr_id", 出現回数)を出現回数に並べたlist．
            ex. [('1', 7), ('2', 3), ('3', 1)]
        Returns:
            expr_idを出現回数の降順に並べたlist.
            ex. ['1', '2']
        """
        result: list[str] = []
        for id, num in sorted_expr_ids:
            # 検索結果の数を絞るためにnumを2以上にしている．
            if num == 1:
                break
            result.append(id)
        return result

    @staticmethod
    def _get_expr_ids(path_set: set[str]) -> list[tuple[str, int]]:
        """path setをクエリにpath_dictionary tableからexpr_idを取得する関数．
        Returns:
            ("expr_id", 出現回数)を出現回数に並べたlist．
            ex. [('1', 7), ('2', 3), ('3', 1)]
        """
        expr_ids: list[str] = []
        for path in path_set:
            with Cursor.connect() as cnx:
                with Cursor.cursor(cnx) as cursor:
                    expr_ids_json = Cursor.select_expr_ids_from_path_dictionary_where_expr_path_1(cursor, path)
            if expr_ids_json is None:
                continue
            expr_ids.extend(expr_ids_json)
        # expr_idsの中のexpr_idをカウント
        expr_ids_dict = collections.Counter(expr_ids)
        # クエリのpathを多く含むexpr_idが最初にくるようにソート
        sorted_expr_ids = expr_ids_dict.most_common()
        return sorted_expr_ids

    @staticmethod
    def _get_info(extracted_ids: list[str]) -> dict[str, list[str]]:
        """ヒットした数式のinfoを取得する関数．
        expr_idが多い順に，expr_idをクエリにinverted_index tableからinfo(uri_id, lang)を取得する．
        Args:
            extracted_ids: expr_idを出現回数の降順に並べたlist.
            ex. ['1', '2']
        Returns:
            info: {'uri_id': ['1', '2'], 'lang': ['ja', 'en']}のような形式．
        """
        loop_times = len(extracted_ids)
        uri_id_list = [[] for i in range(loop_times)]
        lang_list = [[] for i in range(loop_times)]

        with futures.ProcessPoolExecutor() as executor:
            f = [executor.submit(__class__._get_info_from_db, i, expr_id) for i, expr_id in enumerate(extracted_ids)]
            for future in futures.as_completed(f):
                index, info = future.result()
                if info is None:
                    continue
                # []を実際のリストに置き換える
                uri_id_list[index] = info['uri_id']
                lang_list[index] = info['lang']

        result_uri_id = list(itertools.chain.from_iterable(uri_id_list))
        result_lang = list(itertools.chain.from_iterable(lang_list))
        return {'uri_id': result_uri_id, 'lang': result_lang}

    @staticmethod
    def _get_info_from_db(index: int, expr_id: str):
        with Cursor.connect() as cnx:
            with Cursor.cursor(cnx) as cursor:
                info = Cursor.select_info_from_inverted_index_where_expr_id_1(cursor, int(expr_id))
                return index, info

    @staticmethod
    def _get_search_result(info: dict[str, list[str]], extracted_ids: list[str]) -> list[dict]:
        """uri_idをクエリにpage tableからpageの情報を取得して返す関数．
        Args:
            info: info.
            extracted_ids: expr_idを出現回数の降順に並べたlist.
            ex. ['1', '2']
        """
        # 現在の_get_infoのアルゴリズムだと，特定のページが複数回出てくる可能性がある
        uri_ids = []  # 表示するuri_idのリスト
        search_result: list[dict] = []
        display_num = 10  # 表示する検索結果の数
        count = 0
        for i, uri_id in enumerate(info['uri_id']):
            # 重複しているページをスキップ
            if uri_id not in uri_ids:
                uri_ids.append(uri_id)
                lang = info['lang'][i]
                # 指定した言語ではなかったらskip
                # if lang != 'ja'
                #   continue
                with Cursor.connect() as cnx:
                    with Cursor.cursor(cnx) as cursor:
                        page_info = Cursor.select_all_from_page_where_uri_id_1(cursor, uri_id)
                if page_info is None:
                    continue
                search_result.append({
                    'uri': page_info[0],
                    'title': page_info[3],
                    'description': DescrFormatter.format(page_info[4], extracted_ids)  # TODO: formatに時間がかかっているので，分散処理等を検討
                })

                count += 1
                if count == display_num:
                    break
        return search_result
