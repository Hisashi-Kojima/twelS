# -*- coding: utf-8 -*-
"""module description
"""


class Info:
    """inverted_indexのinfo。
    lang:
        ["1つ目のページの言語", "2つ目のページの言語", ...]
    uri_id:
        ["1つ目のページのid", "2つ目のページのid", ...]
    area:
        [
            [# 1つ目のページに含まれている数式の出現範囲のリスト
                [1箇所目の数式の開始位置, 1箇所目の数式の終了位置],
                [2箇所目の数式の開始位置, 2箇所目の数式の終了位置],
                ...
            ],
            [# 2つ目のページに含まれている数式の出現範囲のリスト
                [1箇所目の数式の開始位置, 1箇所目の数式の終了位置],
                [2箇所目の数式の開始位置, 2箇所目の数式の終了位置],
                ...
            ],
            ...
        ]
    """

    def __init__(self, info: dict):
        self.lang_list: list[str] = info['lang']
        self.uri_id_list: list[str] = info['uri_id']
        self.area_list: list[list[list[int]]] = info['area']
