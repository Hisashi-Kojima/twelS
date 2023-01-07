# -*- coding: utf-8 -*-
"""module description
"""

import latex2mathml.converter
from lark import exceptions

from twels.expr.parser import Parser
from twels.database.cursor import Cursor
from twels.indexer.info import Info
from twels.normalizer.normalizer import Normalizer
from twels.snippet.formatter import Formatter
from twels.snippet.snippet import Snippet


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
            mathml = latex2mathml.converter.convert(expr)
            path_set: set[str] = Parser.parse(Normalizer.normalize_subsup(mathml))
            with (Cursor.connect() as cnx, Cursor.cursor(cnx) as cursor):
                score_list = Cursor.search(cursor, path_set)

            search_result = __class__._get_search_result(score_list, start)
            result = {
                'search_result': search_result
                }
            return result
        except exceptions.LarkError:
            result = {
                'search_result': []
            }
            return result
        except Exception:
            result = {
                'search_result': []
            }
            return result

    @staticmethod
    def _get_info(extracted_ids: list[str], start: int) -> Info:
        """ヒットした数式のinfoを取得する関数．
        expr_idが多い順に，expr_idをクエリにinverted_index tableからinfo(uri_id, lang)を取得する．
        Args:
            extracted_ids: expr_idを出現回数の降順に並べたlist.
            e.g. ['1', '2']
            start: 検索開始位置．
        Returns:
            info。
        Notes:
            ヒットした数式のinfoにはヒットした数式の開始位置が記録されている。
        """
        info = Info({
            "lang": [],
            "uri_id": [],
            "expr_start_pos": []
        })
        ids = iter(extracted_ids)
        end = start+__class__.search_num
        while info.size() < end:
            try:
                expr_id: str = next(ids)
                with (Cursor.connect() as cnx, Cursor.cursor(cnx) as cursor):
                    tmp_info, expr_len = Cursor.select_info_and_len_from_inverted_index_where_expr_id_1(cursor, int(expr_id))
                    for i in range(tmp_info.expr_start_pos):
                        # tmp_info.expr_start_pos[i].
                        pass
                    info = info.merge(tmp_info)
            except StopIteration:
                # 検索結果がsearch_num未満のとき
                break

        return info

    @staticmethod
    def _get_search_result(score_list: list, start: int) -> list[dict]:
        """uri_idをクエリにpage tableからpageの情報を取得して返す関数．
        Args:
            score_list: [['expr_id', degree of similarity], ...]
                e.g. [['10', 0.8], ['3', 0.7], ['23', 0.4]]
        Returns:
            uri, title, snippetをkeyに持つdictionaryのリスト。
        """
        # 現在の_get_infoのアルゴリズムだと，特定のページが複数回出てくる可能性がある
        uri_ids = []  # 表示するuri_idのリスト
        search_result: list[dict] = []
        num = len(score_list) - start
        if num <= 0:
            return []

        for i in range(num):
            expr_id: str = score_list[i][0]
            with (Cursor.connect() as cnx, Cursor.cursor(cnx) as cursor):
                info, expr_len = Cursor.select_info_and_len_from_inverted_index_where_expr_id_1(cursor, int(expr_id))
                for j, uri_id in enumerate(info.uri_id_list):
                    if uri_id in uri_ids:
                        continue
                    lang = info.lang_list[j]
                    # if lang != 'ja':
                    #     continue
                    page_info = Cursor.select_all_from_page_where_uri_id_1(cursor, uri_id)
                    if page_info is None:
                        continue
                    expr_start_pos = info.expr_start_pos_list[j]
                    if not expr_start_pos:
                        continue
                    search_result.append({
                        'uri': page_info[0],
                        'title': page_info[3],
                        'snippet': Formatter.format(
                            Snippet(page_info[4], no_clean=True), expr_start_pos, expr_len
                            )
                    })
                    if len(search_result) >= __class__.search_num:
                        break
                else:
                    # this code is executed when the inner loop doesn't break.
                    continue
                # the outer loop breaks when the inner loop breaks.
                break

        return search_result
