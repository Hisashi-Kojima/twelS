# -*- coding: utf-8 -*-
"""module description
"""
import re

from bs4 import BeautifulSoup

from twels.expr.expression import Expression, MATHML_PATTERN
from twels.snippet.cleaner import remove_comments, remove_not_content


class Snippet:
    """Snippetに関するクラス。
    Notes:
        '&#x0002B;'などは'+'などに置き換えられる。
        数式は数式オブジェクトに変換することで文字数を調整できるようになる。
    TODO:
        登録できる文字のmax lengthを設定して、それに収まっているかを確認する。
    """
    def __init__(self, snippet: str, no_clean=False):
        """登録時にはcleanする。検索時にはcleanは不要。
        """
        if no_clean:
            self.snippet = __class__._parse_snippet(snippet)
        else:
            cleaned = __class__._clean(snippet)
            self.snippet = __class__._parse_snippet(cleaned)

        self.text = __class__.__str__(self)

    def __str__(self):
        return ''.join(map(str, self.snippet))

    def search_expr_start_pos(self, expr: Expression) -> list[int]:
        """snippetに含まれているmathmlの開始位置のリストを返す関数。
        Returns:
            [pos1, pos2, pos3,...]
            e.g. [20, 55, 239]
        """
        pos_list = []
        pos = 0
        for i in range(len(self.snippet)):
            if type(self.snippet[i]) is Expression:
                if self.snippet[i] == expr:
                    pos_list.append(pos)
                pos += len(self.snippet[i].mathml)
            else:
                pos += len(self.snippet[i])
        return pos_list

    @staticmethod
    def _clean(text: str) -> str:
        """コメント、HTMLタグ、インデントや改行などを削除し、
        2つ以上のスペースを1つに減らす関数。
        Note:
            英語の記事や日本語の記事中の英文に対応できるように
            スペースを1つ残している。
        """
        soup = BeautifulSoup(text, 'lxml')
        soup.html.unwrap()
        soup.body.unwrap()

        remove_comments(soup)

        t1 = __class__._clean_text(soup)
        t2 = re.sub(r' {2,}', ' ', t1)
        return remove_not_content(t2)

    @staticmethod
    def _clean_text(soup: BeautifulSoup) -> str:
        """不要なタグなどを削除する関数．
        不要な情報を削除することで，登録するデータ量を小さくする．
        classなどが自作のものとかぶっても困るので，そのあたりの削除．
        Notes:
            use only MathML of KaTeX outputs.
            don't use HTML of KaTeX outputs.
            support "htmlAndMathml" and "mathml" in KaTeX output option.
            don't support "html" in KaTeX output option, because
            you must change data structure in inverted_index expr columns,
            which stores MathML when support KaTeX as expr.
            "support KaTeX as expr" means not only MathML but also
            KaTeX are rendered in search results.
        """
        remove_list = [
            'button', 'br', 'canvas', 'footer', 'form', 'header', 'img',
            'iframe', 'input', 'label', 'nav', 'noscript', 'script', 'svg'
            ]

        save_list = [
            'a', 'article', 'aside', 'b', 'caption', 'colgroup',
            'dl', 'dt', 'dd', 'div', re.compile('h[1-6]'), 'i', 'ins', 'li',
            'main', 'ol', 'p', 'span', 'section', 'table', 'tbody', 'td',
            'tfoot', 'th', 'thread', 'tr', 'ul'
            ]

        for item in soup.find_all(remove_list):
            item.decompose()

        for katex_html in soup.find_all('span', class_='katex-html'):
            katex_html.decompose()

        for item in soup.find_all(save_list):
            item.unwrap()

        return str(soup)

    @staticmethod
    def _parse_snippet(snippet: str) -> list[str | Expression]:
        """snippetの数式部分をオブジェクトに変換する関数。
        Args:
            snippet: snippet.
        Returns:
            snippet_list: 数式部分と非数式部分で分けられたリスト。
        Note:
            re.split()の仕様上、
            (1) expr + textの場合（exprで始まる場合）、textsの最初に''が含まれるので、
                text + expr + text になる。
            (2) text + exprの場合（exprで終わる場合）、textsの最後に''が含まれるので、
                text + expr + text になる。
            (3) expr + text + expr （exprで始まって終わる場合）、textsの最初と最後に''が含まれるので、
                text + expr + text + expr + text になる。
            つまり、最初と最後の要素は必ずtextになる。
        """
        mathmls = MATHML_PATTERN.findall(snippet)
        exprs = [Expression(mathml) for mathml in mathmls]

        # snippetの先頭や末尾にMathMLが含まれている場合、
        # split()の結果に空文字列が含まれる。
        texts = re.split(MATHML_PATTERN, snippet)

        if len(exprs) == 0 and len(texts) == 0:
            snippet_list = []
        else:
            # 最初と最後の要素は必ずtext。
            snippet_list = [elem for pair in zip(texts, exprs) for elem in pair]
            if texts[-1] != '':
                snippet_list.append(texts[-1])
            if snippet_list[0] == '':
                snippet_list.pop(0)
        return snippet_list
