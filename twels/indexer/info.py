# -*- coding: utf-8 -*-
"""module description
"""
import json


class Info:
    """inverted_indexのinfo。
    uri_id:
        ["1つ目のページのid", "2つ目のページのid", ...]
    lang:
        ["1つ目のページの言語", "2つ目のページの言語", ...]
    expr_start_pos:
        [
            [1箇所目の数式の開始位置, 2箇所目の数式の開始位置, ...]  # 1ページ目
            [1箇所目の数式の開始位置, 2箇所目の数式の開始位置, ...]  # 2ページ目
            ...
        ]
    """
    def __init__(self, info: dict):
        if not isinstance(info['uri_id'], list):
            raise TypeError(f"info['uri_id'] is not list, but {type(info['uri_id'])}.")
        if not isinstance(info['lang'], list):
            raise TypeError(f"info['lang'] is not list, but {type(info['lang'])}.")
        if not isinstance(info['expr_start_pos'], list):
            raise TypeError(f"info['expr_start_pos'] is not list, but {type(info['expr_start_pos'])}.")

        self.uri_id_list: list[str] = info['uri_id']
        self.lang_list: list[str] = info['lang']
        self.expr_start_pos_list: list[list[int]] = info['expr_start_pos']

    def dumps(self) -> str:
        """stringにdumpする関数。
        Returns:
            infoをdumpした結果。
        """
        info = {
            "uri_id": self.uri_id_list,
            "lang": self.lang_list,
            "expr_start_pos": self.expr_start_pos_list
        }
        return json.dumps(info)

    def is_empty(self) -> bool:
        """
        Returns:
            True when the info is empty.
        """
        if len(self.uri_id_list) == 0:
            assert len(self.lang_list) == 0, f'lang_list should be empty. actual: {self.lang_list}'
            assert len(self.expr_start_pos_list) == 0, f'expr_start_pos_list should be empty. actual: {self.lang_list}'
            return True
        else:
            return False

    def __str__(self) -> str:
        return self.dumps()
