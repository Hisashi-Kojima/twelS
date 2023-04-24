# -*- coding: utf-8 -*-
"""module description
"""
import re

from bs4 import BeautifulSoup, Comment


def remove_comments(soup: BeautifulSoup):
    """HTMLのコメントを削除する関数．
    """
    for comment in soup(string=lambda x: isinstance(x, Comment)):
        comment.extract()


def remove_not_content(text: str) -> str:
    """インデントや改行、属性などを削除する関数。
    ここではスペースに変換して、続く関数で複数のスペースを1つにまとめる。
    """
    # 属性を削除したい。
    # ' '以降を削除できればよい。
    attr_pattern = '<([a-z]+).*?>'

    # <tag attr=""> ->  <tag>
    tmp = re.sub(attr_pattern, r'<\1>', text)

    return re.sub(r'[\t\f\r\n]', ' ', tmp)
