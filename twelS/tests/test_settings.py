# for path
import sys
from pathlib import Path
path = Path(__file__)  # test_indexer.pyのpath
print('path: ', path)
sys.path.append(str(path.parent.parent))  # twels/twelS



from twelS.settings import DEBUG


def test_debug_false():
    """DEBUG = FALSEとなっていることの確認．
    """
    assert DEBUG is False
