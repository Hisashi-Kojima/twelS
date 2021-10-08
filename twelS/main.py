# -*- coding: utf-8 -*-
"""デバッグのためのモジュール
made by Hisashi
"""

from xml.etree.ElementTree import parse
import latex2mathml.converter

from expr.parser import Parser
from search.searcher.searcher import Searcher


if __name__ == '__main__':
    result = Searcher.search('a')
    print(result)
