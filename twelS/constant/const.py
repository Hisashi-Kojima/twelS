# -*- coding: utf-8 -*-
"""module description
made by Hisashi
"""


class Const:
    """定数をまとめたクラス．"""

    # 引数を2つ以上取る関数のリスト．
    # 引数の順番の情報を持つ．
    # TODO: この２つの変数の見直し
    need_args = ['elements', 'frac', 'sup', 'sub', 'root', 'subsup', 'over', 'under', 'underover']
    need_args_m = ['mfrac', 'msup', 'msub', 'mroot', 'msubsup', 'mover', 'munder', 'munderover']

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
        'password': 'i6auwm!LJT57GPwAzmUB@dKyZ%Hjq^',
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
        'password': 'i6auwm!LJT57GPwAzmUB@dKyZ%Hjq^',
        'database': 'twels',
        'port': 3000,
        'connection_timeout': 100  # second
    }
