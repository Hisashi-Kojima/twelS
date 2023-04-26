# -*- coding: utf-8 -*-
"""module description
"""
from urllib.parse import parse_qs


def parse_url(query: str) -> dict:
    """URLを解析し、パラメータに分割する関数。
    Args:
        query: query in the URL. query doesn't include '@'.
               e.g. q=a&lr=ja
    Returns:
        params: keyがパラメーター名、valueがパラメータの値になっている辞書。
    Notes:
        '%20'は'a \lt b'等、LaTeXの区切り文字を表す。
        '+'はクエリの区切り文字を表す。
    """
    url_params = {
        'q': [],
        'start': ['0'],
        'lr': []
    }
    delimiter = '@'

    # '@'はURLの予約文字の1つなので、parse_url()の引数であるqueryは'@'を必ず含まない。
    # '+'のままだとparse_qs()で' 'に変換されてしまい、'+'と'%20'を区別できなくなる。
    # それを避けるために'+'を'@'に置き換える。
    tmp = query.replace('+', delimiter)
    url_params.update(parse_qs(tmp))
    if url_params['q'] and delimiter in url_params['q'][0]:
        url_params['q'] = url_params['q'][0].split(delimiter)
    return url_params
