# -*- coding: utf-8 -*-
"""module description
"""

from twels.snippet.snippet import Snippet


class Formatter:
    """書式整形のためのクラス．
    """
    omit_str = '...'
    excerpt_len = 400
    space_in_front_of_math = 200

    @staticmethod
    def format(snippet: Snippet, expr_start_pos: list[int], expr_len: int) -> str:
        """snippetを表示用に整形する関数．
        数式のハイライトと文章の抜粋を行う．
        Args:
            snippet: snippet.
            expr_start_pos: [1箇所目の数式の開始位置, 2箇所目の数式の開始位置, ...].
            expr_len: 数式の長さ。
        Returns:
            excerpted_snippet: 抜粋された文章．
        """
        s = str(snippet)
        snippet_highlighted = ''
        for start_pos in expr_start_pos:
            try:
                end_pos = start_pos + expr_len
                # headから先に挿入するとtailがずれるので，tailから挿入する．
                tmp = s[:end_pos] + '</span>' + snippet[end_pos:]
                snippet_highlighted = tmp[:start_pos] + '<span class="hl">' + tmp[start_pos:]
                break
            except Exception:
                continue

        return __class__._excerpt(snippet_highlighted, start_pos)

    @staticmethod
    def _excerpt(snippet: str, start_pos: int) -> str:
        """ハイライトされる数式の部分を抜粋する関数．
        ハイライト部分がなければ，先頭から抜粋．
        Args:
            snippet: ハイライトされた数式を含んでいるかもしれないsnippet.
            start_pos: ハイライトする数式の開始位置．
        """
        # mathタグ箇所は文字数に含めない．
        if len(snippet) < __class__.excerpt_len:
            return snippet
        elif snippet.find('<span class="hl">') == -1:
            # ハイライトされた数式はないので，先頭から抜粋．
            return __class__._excerpt_from_head(snippet)
        else:
            # ハイライトされた数式があるとき
            # 数式が複数ある場合もある
            if start_pos < __class__.space_in_front_of_math:
                # 先頭から抜粋
                return __class__._excerpt_from_head(snippet)
            else:
                # 途中から抜粋
                start_index = start_pos - __class__.space_in_front_of_math
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
            snippet: ハイライトされた数式を含んでいるかもしれないsnippet。
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
