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
    def __init__(self, snippet: str):
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
        """
        soup = BeautifulSoup(text, 'lxml')
        soup.html.unwrap()
        soup.body.unwrap()
        for a in soup.find_all('a'):
            a.unwrap()
        for b in soup.find_all('b'):
            b.unwrap()
        for i in soup.find_all('i'):
            i.unwrap()
        for p in soup.find_all('p'):
            p.unwrap()
        for div in soup.find_all('div'):
            div.unwrap()
        for span in soup.find_all('span'):
            span.unwrap()
        for dl in soup.find_all('dl'):
            dl.unwrap()
        for dt in soup.find_all('dt'):
            dt.unwrap()
        for dd in soup.find_all('dd'):
            dd.unwrap()
        for table in soup.find_all('table'):
            table.decompose()
        for ol in soup.find_all('ol'):
            ol.decompose()
        for ul in soup.find_all('ul'):
            ul.decompose()
        for label in soup.find_all('label'):
            label.decompose()
        for h in soup.find_all(re.compile('h[1-6]')):
            h.decompose()
        for br in soup.find_all('br'):
            br.decompose()
        for img in soup.find_all('img'):
            img.decompose()
        for form in soup.find_all('form'):
            form.decompose()
        for input_ in soup.find_all('input'):
            input_.decompose()
        for button in soup.find_all('button'):
            button.decompose()
        for script in soup.find_all('script'):
            script.decompose()
        for footer in soup.find_all('footer'):
            footer.decompose()
        for nav in soup.find_all('nav'):
            nav.decompose()

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
        """
        for semantics in soup.find_all('semantics'):
            semantics.unwrap()
        for mstyle in soup.find_all('mstyle'):
            mstyle.unwrap()
        for mrow in soup.find_all('mrow'):
            mrow.unwrap()
        for annotation in soup.find_all('annotation'):
            annotation.decompose()
