# -*- coding: utf-8 -*-
"""module description
made by Hisashi
"""
from pathlib import Path
import os

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(os.path.join(BASE_DIR.parent, '.env'))
env = environ.Env()


class Const:
    """定数をまとめたクラス．"""

    # 引数を2つ以上取る関数のリスト．
    # 引数の順番（pseudo num: #1など）の情報を持つ．
    need_args = ['elements', 'neg', 'frac', 'sup', 'sub', 'root', 'subsup', 'over', 'under', 'underover']

    # rule names
    root_data = 'start'
    token_type = 'TOKEN'
    expr_data = 'expr'
    sum_data = 'sum'
    product_data = 'product'
    equal_data = 'equal'
    atom_data = 'atom'
    in_data = 'in'
    neg_data = 'neg'
    paren_data = 'paren'
    frac_data = 'frac'
    sup_data = 'sup'
    sub_data = 'sub'
    subsup_data = 'subsup'
    sqrt_data = 'sqrt'
    func_root_data = 'root'
    over_data = 'over'
    under_data = 'under'
    underover_data = 'underover'
    table_data = 'table'
    tr_data = 'tr'
    td_data = 'td'
    cdots_data = 'cdots'
    omit_data = 'omit'  # 0.333...や0.9999...などの省略があったことを示す．

    # TODO: connection_timeoutの適切な値を設定する
    # 開発用のデータベース
    config_for_dev = {
        'user': 'hisashi',
        'password': env('MY_HISASHI_PASSWORD'),
        'host': 'mysql_container',  # MySQLのコンテナの名前で接続
        'database': 'twels',
        'connection_timeout': 100  # second
    }

    # TODO: localでもconfig_for_devで接続できるように修正．localでもdockerを使ってクロールすれば良い．
    config_for_local = {
        'user': 'hisashi',
        'password': 'lovebasketball',
        'database': 'twels',
        'connection_timeout': 100  # second
    }

    # テスト用
    config_for_test = {
        'user': 'hisashi',
        'password': env('MY_HISASHI_PASSWORD'),
        'database': 'twels',
        'port': 3000,
        'connection_timeout': 100  # second
    }
