# -*- coding: utf-8 -*-
"""module description
"""


class ParserConst:
    """Parserのための定数を定義するclass．
    twels.expr.parserとtwels.expr.treeやtwels.normalizer.normalizerの
    循環参照を防ぐために用意．
    """
    # rule names
    root_data = 'start'
    token_type = 'TOKEN'
    expr_data = 'expr'
    sum_data = 'sum'
    product_data = 'product'
    atom_data = 'atom'
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
    cdots_data = 'cdots'
    omit_data = 'omit'  # 0.333...や0.9999...などの省略があったことを示す．
    slash_data = '\\slash'

    equal_data = 'equal'
    less_data = 'less'
    greater_data = 'greater'
    in_data = 'in'

    relational_operators = [expr_data, less_data, greater_data, in_data]
