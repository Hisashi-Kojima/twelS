# -*- coding: utf-8 -*-
"""testのためにpathを追加するモジュール
made by Hisashi
"""
import sys
from pathlib import Path


def add_path():
    """sys.pathにpathを追加する関数"""
    path = Path(__file__)  # add_path.pyのpath

    root_dir = path.parent.parent

    twels_dir = root_dir / 'twelS'
    _append_if_not_in(twels_dir)


def _append_if_not_in(path: Path):
    """pathがsys.pathに含まれていなかったら追加する関数．
    """
    if str(path) not in sys.path:
        sys.path.append(str(path))
