# -*- coding: utf-8 -*-
"""module description
made by Hisashi
"""

from twels.database.cursor import Cursor
from twels.utils.utils import print_in_red


class SnippetFormatter:
    """書式整形のためのクラス．
    """
    omit_str = '...'
    excerpt_len = 400
    space_in_front_of_math = 200

    @staticmethod
    def format(snippet: str, extracted_ids: list[str]) -> str:
        """snippetを表示用に整形する関数．
        数式のハイライトと文章の抜粋を行う．
        Args:
            snippet: snippet.
            extracted_ids: expr_idを出現回数の降順に並べたlist.
            ex. ['1', '2']
        Returns:
            excerpted_snippet: 抜粋された文章．
        """
        _snippet = snippet
        for i, expr_id in enumerate(extracted_ids):
            if i > 30:
                # extracted_idsの先頭のexpr_idから順にページを取得し，
                # 検索結果の上位10件しか表示しない今の実装では，
                # extracted_idsを30件調べれば十分であると考える．
                # 別の式が同じページにヒットすることに注意．
                break
            # expr_idをもとに，数式を取得
            with Cursor.connect() as cnx:
                with Cursor.cursor(cnx) as cursor:
                    expr = Cursor.select_expr_from_expression_where_expr_id_1(cursor, int(expr_id))
            # 数式がsnippetに含まれているか確認．
            head = snippet.find(expr)
            tail = head + len(expr)
            if head == -1:
                # 含まれていなければ，繰り返す．
                continue
            else:
                # 含まれていれば，ハイライトする．
                _snippet = __class__._highlight(snippet, head, tail)
                # ハイライトする数式は1つだけ．
                break

        return __class__._excerpt(_snippet, head, tail+len('<span class="hl"></span>'))

    @staticmethod
    def _highlight(snippet: str, head: int, tail: int) -> str:
        """該当する数式をハイライトする関数．
        ハイライトされるタグを数式の前後に埋め込む．
        Args:
            snippet: snippet.
            head: ハイライトする数式の開始位置．
            tail: ハイライトする数式の終了位置．
        """
        # headから先に挿入するとtailがずれるので，tailから挿入する．
        tmp = snippet[:tail] + '</span>' + snippet[tail:]
        return tmp[:head] + '<span class="hl">' + tmp[head:]

    @staticmethod
    def _excerpt(snippet: str, head: int, tail: int) -> str:
        """ハイライトされる数式の部分を抜粋する関数．
        ハイライト部分がなければ，先頭から抜粋．
        Args:
            snippet: ハイライトされた数式を含んでいるかもしれないsnippet.
            head: ハイライトする数式の開始位置．
            tail: ハイライトする数式の終了位置．
        """
        # mathタグ箇所は文字数に含めない．
        if len(snippet) < __class__.excerpt_len:
            return snippet
        elif head == -1:
            # ハイライトされた数式はないので，先頭から抜粋．
            return __class__._excerpt_from_head(snippet)
        else:
            # ハイライトされた数式があるとき
            # 数式が複数ある場合もある
            if head < __class__.space_in_front_of_math:
                # 先頭から抜粋
                return __class__._excerpt_from_head(snippet)
            else:
                # 途中から抜粋
                start_index = head - __class__.space_in_front_of_math
                # 抜粋開始位置がmathタグの中でないことを確認
                if snippet.find('</math>', start_index) - snippet.find('<math', start_index) > 0:
                    # '/math>'のどこかでないことを確認．
                    tmp = snippet[start_index:start_index+len('/math>')]
                    if (tmp[:1] != '>' and
                       tmp[:2] != 'h>' and
                       tmp[:3] != 'th>' and
                       tmp[:4] != 'ath>' and
                       tmp[:5] != 'math>' and
                       tmp[:6] != '/math>'):
                        return __class__._excerpt_from_head(snippet[start_index:])
                    else:
                        start_index = __class__._get_last_math_tag_index(snippet, start_index)
                        return __class__._excerpt_from_head(snippet[start_index:])
                else:
                    # <math>と</math>の間の場合
                    start_index = __class__._get_last_math_tag_index(snippet, start_index)
                    return __class__._excerpt_from_head(snippet[start_index:])

    @staticmethod
    def _excerpt_from_head(snippet: str) -> str:
        """mathタグ以外の文字数がexcerpt_lenになるように抜粋する関数．
        Args:
            snippet: ハイライトされた数式を含んでいるかもしれないsnippetiption.
        TODO:
            終了箇所が<math></math>の中の場合があり，このとき，MathMLを正しく解釈できないので
            'Math input error'になる．これの解決．
        """
        tail = 0  # mathタグの終わりの位置
        result_length = 0

        while True:
            last_tail = tail
            head = snippet.find('<math', tail)
            if head == -1:
                return __class__._get_result(snippet, result_length, last_tail)
            tail = snippet.find('</math>', head)
            additional_length = head - last_tail

            if result_length + additional_length > __class__.excerpt_len:
                return __class__._get_result(snippet, result_length, last_tail)

            result_length += additional_length

    @staticmethod
    def _get_last_math_tag_index(snippet: str, start_index: int) -> int:
        """start_indexの直前のmathタグの開始位置を取得する．
        """
        index = snippet.find('<math')
        last_index = 0
        while True:
            if index == -1 or start_index - index < 0:
                break
            last_index = index
            index = snippet.find('<math', index+1)
        return last_index

    @staticmethod
    def _get_result(snippet: str, result_length: int, last_tail: int):
        extra = __class__.excerpt_len - result_length
        return snippet[:last_tail+extra] + __class__.omit_str
