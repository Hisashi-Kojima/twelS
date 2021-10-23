# -*- coding: utf-8 -*-
"""module description
made by Hisashi
"""

import collections

import latex2mathml.converter
from lark import exceptions

from expr.parser import Parser
from database.cursor import Cursor
from utils.utils import print_in_red
from .descr_formatter import DescrFormatter


class Searcher:
    """データベースに接続し，検索結果を取得するためのクラス．
    """
    # 検索結果として表示する数
    search_num = 10

    @staticmethod
    def search(expr: str, start: int) -> dict:
        """
        Args:
            expr: 検索する式．
            start: 検索開始位置．
        Returns:
            {'search_result': search_result, 'result_num': result_num}
        """
        # LaTeX -> MathML -> Tree (-> Normalize) -> path set
        try:
            path_set: set[str] = Parser.parse(latex2mathml.converter.convert(expr))
            sorted_expr_ids = __class__._get_expr_ids(path_set)
            extracted_ids = __class__._extract_ids_from_sorted_expr_ids(sorted_expr_ids, start)
            info = __class__._get_info(extracted_ids, start)
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
    def _extract_ids_from_sorted_expr_ids(sorted_expr_ids: list[tuple[str, int]], start: int) -> list[str]:
        """sorted_expr_idsからいくつかのidだけを取得する関数．
        Args:
            sorted_expr_ids: ("expr_id", 出現回数)を出現回数に並べたlist．
            ex. [('1', 7), ('2', 3), ('3', 1)]
            start: 検索開始位置．
        Returns:
            expr_idを出現回数の降順に並べたlist.
            ex. ['1', '2']
        """
        result: list[str] = []
        try:
            # 検索結果として表示する数と同じ数だけexpr_idがあれば十分だと仮定し，
            # rangeのstopをstart+search_numに設定
            for i in range(start+__class__.search_num):
                # append expr_id
                result.append(sorted_expr_ids[i][0])
        except IndexError:
            pass
        finally:
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
            with (Cursor.connect() as cnx, Cursor.cursor(cnx) as cursor):
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
    def _get_info(extracted_ids: list[str], start) -> dict[str, list[str]]:
        """ヒットした数式のinfoを取得する関数．
        expr_idが多い順に，expr_idをクエリにinverted_index tableからinfo(uri_id, lang)を取得する．
        Args:
            extracted_ids: expr_idを出現回数の降順に並べたlist.
            ex. ['1', '2']
            start: 検索開始位置．
        Returns:
            info: {'uri_id': ['1', '2'], 'lang': ['ja', 'en']}のような形式．
        """
        info: dict[str, list[str]] = {'uri_id': [], 'lang': []}
        ids = iter(extracted_ids)
        end = start+__class__.search_num
        while len(info['uri_id']) < end:
            expr_id: str = next(ids)
            with (Cursor.connect() as cnx, Cursor.cursor(cnx) as cursor):
                tmp_info = Cursor.select_info_from_inverted_index_where_expr_id_1(cursor, int(expr_id))
                info['uri_id'].extend(tmp_info['uri_id'])
                info['lang'].extend(tmp_info['lang'])

        return {
            'uri_id': info['uri_id'][start:end],
            'lang': info['lang'][start:end]
            }

    @staticmethod
    def _get_info_from_db(index: int, expr_id: str):
        with (Cursor.connect() as cnx, Cursor.cursor(cnx) as cursor):
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
        for i, uri_id in enumerate(info['uri_id']):
            # 重複しているページをスキップ
            if uri_id not in uri_ids:
                uri_ids.append(uri_id)
                lang = info['lang'][i]
                # 指定した言語ではなかったらskip
                # if lang != 'ja'
                #   continue
                with (Cursor.connect() as cnx, Cursor.cursor(cnx) as cursor):
                    page_info = Cursor.select_all_from_page_where_uri_id_1(cursor, uri_id)
                if page_info is None:
                    continue
                search_result.append({
                    'uri': page_info[0],
                    'title': page_info[3],
                    'description': DescrFormatter.format(page_info[4], extracted_ids)  # TODO: formatに時間がかかっているので，分散処理等を検討
                })

        return search_result
