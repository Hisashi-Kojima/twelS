# -*- coding: utf-8 -*-
"""module description
"""
import copy
import json
from typing import Self


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

        self.uri_id_list: list[str] = copy.deepcopy(info['uri_id'])
        self.lang_list: list[str] = copy.deepcopy(info['lang'])
        self.expr_start_pos_list: list[list[int]] = copy.deepcopy(info['expr_start_pos'])

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

    def extract(self, start: int, stop: int | None = None) -> Self:
        """指定された範囲のinfoを返す関数。
        Args:
            start: 開始位置。
            stop: 終了位置。
        Returns:
            startからstopまでのinfo。
        Notes:
            startが無効の場合、空のinfoを返す。
            startが有効で、stopがinfo.size()を超えている場合、
            指定されたstartから最後までのinfoを返す。
            startが有効で、かつstopがstartよりも小さい場合、空のinfoを返す。
            stopが省略された場合、startから最後までのinfoを返す。
        """
        if stop is None:
            stop = self.size()
        info = copy.deepcopy(self)
        info.uri_id_list = self.uri_id_list[start:stop]
        info.lang_list = self.lang_list[start:stop]
        info.expr_start_pos_list = self.expr_start_pos_list[start:stop]
        return info

    def merge(self, info: Self) -> Self:
        """このインスタンスと引数のinfoをマージした結果を返す関数。
        引数のinfoはこのインスタンスのinfoの後ろに追加される。
        Returns:
            info
        """
        result = copy.deepcopy(self)
        
        result.uri_id_list.extend(info.uri_id_list)
        result.lang_list.extend(info.lang_list)
        result.expr_start_pos_list.extend(info.expr_start_pos_list)
        return result

    def size(self) -> int:
        """このインスタンスの要素数を返す関数"""
        return len(self.uri_id_list)

    def __str__(self) -> str:
        return self.dumps()
