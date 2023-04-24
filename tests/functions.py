# -*- coding: utf-8 -*-
"""functions for test.
"""
from twels.database.cursor import Cursor


def reset_tables():
    """tableのレコードをすべて削除する関数．
    try-finallyを使って，必ずtestの最後に呼び出すことでtableを常に同じ状態に保つ．
    Notes:
        この関数を呼び出すファイルのテストはデータベースの中にレコードがない状態で開始。
    """
    with Cursor.connect(test=True) as cnx:
        with Cursor.cursor(cnx) as cursor:
            cursor.execute('TRUNCATE TABLE inverted_index')
            cursor.execute('TRUNCATE TABLE page')
            cursor.execute('TRUNCATE TABLE path_dictionary')
