import sys
from pathlib import Path
path = Path(__file__)  # test_descr_formatter.pyのpath
sys.path.append(str(path.parent.parent))  # twels/twelS

from search.searcher.descr_formatter import DescrFormatter


def test_excerpt_1():
    """DescrFormatter._excerpt()のテスト．
    ハイライトされた数式とハイライトされていない数式を含む場合．
    先頭に140文字がある．
    """
    descr = 'aaaaaaaaaa aaaaaaaaa aaaaaaaaa aaaaaaaaa aaaaaaaaa aaaaaaaaa aaaaaaaaa'\
            'aaaaaaaaaa aaaaaaaaa aaaaaaaaa aaaaaaaaa aaaaaaaaa aaaaaaaaa aaaaaaaaa'\
                '<span class="hl">'\
                '<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">'\
                '<mrow>'\
                '<mn>1</mn>'\
                '<mo>&#x0002B;</mo>'\
                '<mn>2</mn>'\
                '</mrow>'\
                '</math>'\
                '</span>'\
            'aaaaaaaaaa aaaaaaaaa aaaaaaaaa aaaaaaaaa aaaaaaaaa aaaaaaaaa aaaaaaaaa'\
                '<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">'\
                '<mrow>'\
                '<mn>3</mn>'\
                '<mo>&#x0002B;</mo>'\
                '<mn>4</mn>'\
                '</mrow>'\
                '</math>'\
            'aaaaaaaaaa aaaaaaaaa aaaaaaaaa aaaaaaaaa aaaaaaaaa aaaaaaaaa aaaaaaaaa'

    head = descr.find('<span class="hl">')
    tail = descr.find('</span>') + len('</span>')
    result = DescrFormatter._excerpt(descr, head, tail)
    assert True == result  # デバッグ用
