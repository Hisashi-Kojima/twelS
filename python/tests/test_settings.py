# -*- coding: utf-8 -*-
"""module description
"""

from front.twelS.settings import DEBUG


def test_debug_false():
    """DEBUG = FALSEとなっていることの確認．
    """
    assert DEBUG is False
