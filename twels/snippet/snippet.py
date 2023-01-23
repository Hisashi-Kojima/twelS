# -*- coding: utf-8 -*-
"""module description
"""
import re

from bs4 import BeautifulSoup, Comment


class Snippet:
    """Snippetに関するクラス。
    Notes:
        '&#x0002B;'などは'+'などに置き換えられる。
    TODO:
        登録できる文字のmax lengthを設定して，それに収まっているかを確認する．
    """
    def __init__(self, snippet: str, no_clean=False):
        """登録時にはcleanする。検索時にはcleanは不要。"""
        if no_clean:
            self.snippet = snippet
        else:
            self.snippet = __class__._clean_text(snippet)

    def __str__(self):
        return self.snippet

    def clean(text: str) -> str:
        """不要なものを削除する関数"""
        soup = BeautifulSoup(text, 'lxml')
        soup.html.unwrap()
        soup.body.unwrap()
        for p in soup.find_all('p'):
            p.unwrap()
        __class__._remove_comments(soup)
        __class__._remove_unnecessary_tags(soup)

        result = str(soup)
        return __class__._remove_spaces(result)

    def search_expr_start_pos(self, mathml: str) -> list[int]:
        """snippetに含まれているmathmlの開始位置のリストを返す関数。
        Returns:
            [pos1, pos2, pos3,...]
            e.g. [20, 55, 239]
        """
        pos_list = []
        pos = self.snippet.find(mathml)
        while pos != -1:
            pos_list.append(pos)
            pos = self.snippet.find(mathml, pos+1)
        return pos_list

    @staticmethod
    def _clean_text(text: str):
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
            'button', 'br', 'footer', 'form', 'header', 'img',
            'iframe', 'input', 'label', 'nav', 'noscript', 'script'
            ]

        save_list = [
            'a', 'article', 'aside', 'b', 'caption', 'colgroup',
            'dl', 'dt', 'dd', 'div', re.compile('h[1-6]'), 'i', 'ins', 'li',
            'main', 'ol', 'p', 'span', 'section', 'table', 'tbody', 'td',
            'tfoot', 'th', 'thread', 'tr', 'ul'
            ]

        soup = BeautifulSoup(text, 'lxml')
        soup.html.unwrap()
        soup.body.unwrap()

        for item in soup.find_all(remove_list):
            item.decompose()

        for katex_html in soup.find_all('span', class_='katex-html'):
            katex_html.decompose()

        for item in soup.find_all(save_list):
            item.unwrap()

        result = str(soup)
        return __class__.clean(result)

    @staticmethod
    def _remove_comments(soup: BeautifulSoup):
        """HTMLのコメントを削除する関数．
        """
        for comment in soup(text=lambda x: isinstance(x, Comment)):
            comment.extract()

    @staticmethod
    def _remove_spaces(text: str) -> str:
        """インデントや改行、属性などを削除する関数．
        """
        # 属性を削除したい。
        # ' '以降を削除できればよい。
        attr_pattern = '<([a-z]+).*?>'

        t1 = re.sub(attr_pattern, '<\\1>', text)
        t2 = t1.replace(' ', '')
        t3 = t2.replace('\n', '')
        return t3.replace('\t', '')

    @staticmethod
    def _remove_unnecessary_tags(soup: BeautifulSoup):
        """MathMLの不要なタグを削除する関数。
        Notes:
            mrowを削除すると、
            <mfrac>
                <mi>d</mi>
                <mrow>
                    <mi>d</mi>
                    <mi>x</mi>
                </mrow>
            </mfrac>
            などを正しくparseできなくなってしまう。
            なので、mrowを常に削除することはできない。
        """
        save_list = [
            'semantics', 'mstyle'
        ]
        for item in soup.find_all(save_list):
            item.unwrap()
        for annotation in soup.find_all('annotation'):
            annotation.decompose()
