from add_path import add_path
add_path()

from twelS.settings import DEBUG


def test_debug_false():
    """DEBUG = FALSEとなっていることの確認．
    """
    assert DEBUG is False
