# -*- coding: utf-8 -*-
"""デバッグのためのモジュール
made by Hisashi
"""

from xml.etree.ElementTree import parse
import latex2mathml.converter

from twels.expr.parser import Parser
from twels.search.searcher.searcher import Searcher


if __name__ == '__main__':
    result = Searcher.search('a')
    print(result)
