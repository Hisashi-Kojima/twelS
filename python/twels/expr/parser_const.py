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
    abs_data = 'abs'
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
    log_data = 'log'
    cdots_data = 'cdots'
    omit_data = 'omit'  # 0.333...や0.9999...などの省略があったことを示す．
    abbr_add_data = 'abbr_add'
    abbr_mul_data = 'abbr_mul'
    slash_data = '\\slash'
    mod_data = 'mod'

    equal_data = 'equal'
    less_data = 'less'
    greater_data = 'greater'
    in_data = 'in'
    ni_data = 'ni'
    neq_data = 'neq'
    subset_data = 'subset'
    supset_data = 'supset'
    subseteq_data = 'subseteq'
    supseteq_data = 'supseteq'

    # modを含むので他のrelational operatorと同様には扱えないと思い
    # 他と分けて記述している。
    equiv_data = 'equiv'

    ro_commutative = [
        equal_data, neq_data
    ]
    ro_non_commutative = [
        less_data, greater_data, in_data, ni_data, subset_data, supset_data,
        subseteq_data, supseteq_data
    ]
    relational_operators = ro_commutative + ro_non_commutative
