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
    summation_data = 'summation'
    product_of_seq_data = 'product_of_seq'
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
    integral_data = 'integral'
    lim_data = 'lim'
    cdots_data = 'cdots'
    omit_data = 'omit'  # 0.333...や0.9999...などの省略があったことを示す．
    slash_data = '\\slash'

    equal_data = 'equal'
    less_data = 'less'
    greater_data = 'greater'
    in_data = 'in'

    relational_operators = [equal_data, less_data, greater_data, in_data]
    ro_commutative = [equal_data]
    ro_non_commutative = [less_data, greater_data, in_data]
