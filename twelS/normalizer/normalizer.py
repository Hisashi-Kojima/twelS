# -*- coding: utf-8 -*-
"""module description
made by Hisashi
"""

from lark import Token

from twelS.constant.const import Const


class Normalizer:
    def normalize_num(number):
        """正規化を行う関数．
        0.999999を0.9にする．
        Args:
            number: 数字のトークン．
        """
        if type(number) is Token:
            num: str = number.value
            length = len(num)
            index = length
            last_char = num[length-1]
            # 一番最後の文字から連続している箇所の最初を探す．
            for i in range(length):
                # 一番最後の文字はチェックする必要がないのでスキップ
                if num[length-2-i] != last_char:
                    break
                # indexを1つずらす
                index -= 1
            result = num[:index]
            # すべて同じ文字なら''になる．
            if result == '':
                return Token(Const.token_type, last_char)
            else:
                return Token(Const.token_type, result)
        else:
            # 正規化できないときにはそのまま返す．
            return number
