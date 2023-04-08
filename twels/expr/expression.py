# -*- coding: utf-8 -*-
"""module description
"""
import re

from bs4 import BeautifulSoup

from twels.snippet.cleaner import remove_comments, remove_not_content


MATHML_PATTERN = re.compile(r'<math[^>]*>.*?</math>', re.DOTALL)


class Expression:
    """Immutable class.
    どの言語の場合でも、同じ数式に対しては同じ処理をしたいので、
    そのような処理をこのクラスで行う。
    Notes:
        1. set()でself.mathmlが同じExpressionを
           重複しないようにするためにimmutable classにしている。
        2. '&#x0002B;'などは'+'などに変換される。
    """
    def __init__(self, mathml: str):
        if type(mathml) is not str:
            raise TypeError(f'Expression does not support {type(mathml)}.')

        matched = re.fullmatch(MATHML_PATTERN, mathml)
        if not matched:
            raise ValueError(f'"{mathml}" is invalid MathML syntax.')

        self.mathml = __class__._clean(mathml)

    def __str__(self) -> str:
        return self.mathml

    def __repr__(self) -> str:
        return f'Expression("{self.mathml}")'

    def __eq__(self, other) -> bool:
        if isinstance(other, Expression):
            return self.__dict__ == other.__dict__
        return False

    def __hash__(self) -> int:
        # set()でself.mathmlが同じExpressionを
        # 重複しないようにするためにこの関数を定義している。
        return hash(self.mathml)

    @staticmethod
    def _clean(mathml: str) -> str:
        """不要な情報を削除する関数。
        """
        # BeautifulSoupが<mspace/>を<mspace></mspace>に変換するので、
        # 変換前に<mspace/>を削除する。
        new_mathml = __class__._remove_mspace(mathml)

        soup = BeautifulSoup(new_mathml, 'lxml')
        soup.html.unwrap()
        soup.body.unwrap()

        remove_comments(soup)
        __class__._remove_unnecessary_tags(soup)
        tmp = remove_not_content(str(soup))
        return tmp.replace(' ', '')

    @staticmethod
    def _remove_mspace(mathml: str) -> str:
        """MathML中の<mspace />を削除する関数。
        Note:
            （要確認）mspaceは数式の区切り文字として使用されることもあるようなので、
            全てのmspaceを削除することには注意した方が良さそう。
        """
        return re.sub(r'<mspace.*?/>', '', mathml)

    @staticmethod
    def _remove_unnecessary_tags(soup: BeautifulSoup) -> str:
        """MathMLの不要なタグを削除する関数。
        Args:
            soup: MathMLをBeautifulSoupで解析したもの。
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
        remove_list = [
            'annotation'
        ]
        for item in soup.find_all(save_list):
            item.unwrap()

        for item in soup.find_all(remove_list):
            item.decompose()
