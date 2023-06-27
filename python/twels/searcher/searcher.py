# -*- coding: utf-8 -*-
"""module description
"""
import re

import latex2mathml.converter
from lark import exceptions

from twels.expr.expression import Expression
from twels.expr.parser import Parser
from twels.database.cursor import Cursor
from twels.normalizer.normalizer import Normalizer
from twels.snippet.formatter import Formatter
from twels.snippet.snippet import Snippet
from twels.solr.client import get_solr_client


class Searcher:
    """データベースに接続し，検索結果を取得するためのクラス．
    """
    # 検索結果として表示する数
    search_num = 10

    @staticmethod
    def search(query: str, start: int, lr_list: list[str], test: bool = False) -> dict:
        """
        Args:
            query: 検索する自然言語または数式（LaTeX）。
            start: 検索開始位置。
            lr_list: 検索対象の言語のリスト。
            test: testのときにはTrueにする。
        Returns:
            {
                'search_result': search result.
                'has_next': 未表示の検索結果が残っていればTrue。
            }
        """
        # LaTeX -> MathML -> Tree (-> Normalize) -> path set
        try:
            if __class__._is_expr(query):
                return __class__._search_expr(query, start, lr_list, test)
            else:
                return __class__._search_natural_lang(query)

        except exceptions.LarkError:
            return {
                'search_result': [],
                'has_next': False
            }
        except Exception:
            return {
                'search_result': [],
                'has_next': False
            }

    @staticmethod
    def _get_search_result(score_list: list, start: int, lr_list: list[str], test: bool = False) -> tuple[list[dict], bool]:
        """uri_idをクエリにpage tableからpageの情報を取得して返す関数．
        Args:
            score_list: [['expr_id', degree of similarity], ...]
                e.g. [['10', 0.8], ['3', 0.7], ['23', 0.4]]
            start: 検索開始位置。
            test: testのときにはTrueにする。
        Returns:
            (search_result, has_next)
            search_result: uri, title, snippetをkeyに持つdictionaryのリスト。
            has_next: 未表示の検索結果が残っていればTrue。
        """
        page_count = 0
        result_uri_ids = []
        search_result: list[dict] = []

        for score in score_list:
            expr_id: str = score[0]
            with (Cursor.connect(test) as cnx, Cursor.cursor(cnx) as cursor):
                info, expr_len = Cursor.select_info_and_len_from_inverted_index_where_expr_id_1(cursor, int(expr_id))

                for j, uri_id in enumerate(info.uri_id_list):
                    expr_start_pos = info.expr_start_pos_list[j]
                    if (info.lang_list[j] not in lr_list) or\
                       (uri_id in result_uri_ids) or\
                       (not expr_start_pos):
                        continue

                    page_info = Cursor.select_all_from_page_where_uri_id_1(cursor, uri_id)
                    if page_info is None:
                        continue
                    if start <= page_count:
                        if len(search_result) < __class__.search_num:
                            search_result.append(__class__._search_result(
                                page_info[0],
                                page_info[3],
                                Formatter.format(Snippet(page_info[4], clean=False), expr_start_pos, expr_len)
                            ))
                            result_uri_ids.append(uri_id)
                        else:
                            # (search_num + 1)個の検索結果があるとき
                            return search_result, True
                    page_count += 1

        return search_result, False

    @staticmethod
    def _is_expr(s: str) -> bool:
        """return True when the input is a mathematical expression.
        TODO: '/'をどう扱うかを決める。1/2は数式だが、he/sheは数式ではない。
            エスケープを用意する？もっと前の処理で区別できるようにしておく？
        TODO: a-bとwell-beingを区別する方法を考える。
        TODO: 'K8s'のように数字を含む自然言語と'8y'などを区別することについて考える。
        """
        # starting with '\'.
        # numbers.
        # include operators.
        expr_pattern = r'\\.+|\d+|.*[+\-*/<>^]+.*'
        result = re.search(expr_pattern, s)
        return result is not None

    @staticmethod
    def _search_expr(latex: str, start: int, lr_list: list[str], test: bool = False) -> dict:
        """数式を検索する関数。
        Args:
            latex: 検索する数式（LaTeX）。
            start: 検索開始位置。
            lr_list: 検索対象の言語のリスト。
            test: testのときにはTrueにする。
        Returns:
            {
                'search_result': search result.
                'has_next': 未表示の検索結果が残っていればTrue。
            }
        """
        mathml = latex2mathml.converter.convert(latex)
        normalized = Normalizer.normalize_subsup(mathml)
        path_set: set[str] = Parser.parse(Expression(normalized))
        print('path_set:', str(path_set))
        with (Cursor.connect(test) as cnx, Cursor.cursor(cnx) as cursor):
            score_list = Cursor.search(cursor, path_set)

        search_result, has_next = __class__._get_search_result(score_list, start, lr_list, test)
        return {
            'search_result': search_result,
            'has_next': has_next
            }

    @staticmethod
    def _search_natural_lang(query: str) -> dict:
        """自然言語を検索する関数。
        TODO: start, lr_listへの対応。
        """
        print('search_natural_lang()')
        solr = get_solr_client()
        print('0')
        results = solr.search(f'text:{query}', **{
            'hl': 'true',
            'hl.fl': 'content',
            'hl.fragsize': 300,
            'hl.tag.pre': '<span class="hl">',
            'hl.tag.post': '</span>',
        })

        search_result: list[dict] = []

        for result in results:
            search_result.append(__class__._search_result(
                result['url'],
                result['title'][0],
                Snippet(results.highlighting[result['id']]['content'][0], clean=False)
            ))

        # TODO: has_nextの更新。
        return {
            'search_result': search_result,
            'has_next': False
            }

    @staticmethod
    def _search_result(uri: str, title: str, snippet: Snippet) -> dict:
        """コンストラクタの役割。"""
        return {
            'uri': uri,
            'title': title,
            'snippet': snippet
        }
