SCHEMA = [
'''
Table: basic_info
Column: [
(stk_code, Comment: securities code. Types: text. Primary key.),
(stk_name, Comment: securities name. Types: text.)
]
''',

'''
Table: balance_sheet,
Column: [
(stk_code, Comment: securities code. Types: text.),
(cash_cb, Comment: cash and deposits with central bank. Types: real.),
(ib_deposits, Comment: due from interbank deposits. Types: real.),
(prec_metals, Comment: noble metal. Types: real.),
(lending_funds, Comment: lending funds. Types: real.),
(trad_fas, Comment: trading financial assets. Types: real.),
(deriv_assets, Comment: derivative financial assets. Types: real.),
(buyback_fas, Comment: purchase of resale financial assets. Types: real.),
(int_receiv, Comment: interest receivable. Types: real.),
(loans_adv, Comment: issuance of loans and advances. Types: real.),
(avail_sale_fas, Comment: available-for-sale financial assets. Types: real.),
(held_mat_invest, Comment: held-to-maturity investments. Types: real.),
(recv_invest, Comment: accounts receivable investment. Types: real.),
(lt_eq_invest, Comment: long term equity investment. Types: real.),
(inv_real_estate, Comment: investment real estate. Types: real.),
(fix_assets, Comment: fixed assets. Types: real.),
(intang_assets, Comment: intangible assets. Types: real.),
(def_it_assets, Comment: deferred tax assets. Types: real.),
(oth_assets, Comment: other assets. Types: real.),
(tot_assets, Comment: total assets. Types: real.),
(bor_cb, Comment: borrowing from the central bank. Types: real.),
(ib_dep_oth_fis, Comment: deposits from interbank and other financial institutions. Types: real.),
(bor_funds_oth_fis, Comment: borrowing funds. Types: real.),
(trad_fin_liab, Comment: trading financial liabilities. Types: real.),
(deriv_liab, Comment: derivative financial liabilities. Types: real.),
(sell_rep_fas, Comment: financial assets sold for repurchase. Types: real.),
(acc_deposits, Comment: deposit absorption. Types: real.),
(emp_comp_pay, Comment: payable employee compensation. Types: real.),
(tax_pay, Comment: taxes and fees payable. Types: real.),
(int_pay, Comment: interest payable. Types: real.),
(est_liab, Comment: estimated liabilities. Types: real.),
(bonds_pay, Comment: bonds payable. Types: real.),
(def_it_liab, Comment: deferred tax liability. Types: real.),
(oth_liab, Comment: other liabilities. Types: real.),
(tot_liab, Comment: total liabilities. Types: real.),
(paid_up_cap, Comment: paid-in capital (or share capital). Types: real.),
(cap_reserves, Comment: capital reserve. Types: real.),
(treas_stock, Comment: treasury stock. Types: real.),
(sur_reserves, Comment: surplus reserves. Types: real.),
(gen_risk_res, Comment: general risk preparation. Types: real.),
(undist_profits, Comment: undistributed profits. Types: real.),
(exch_diff_cash, Comment: translation difference of foreign currency statements. Types: real.),
(own_eq_attr_parent, Comment: total owner's equity attributable to the parent company. Types: real.),
(minor_int_eq, Comment: minority shareholders' equity. Types: real.),
(tot_own_eq, Comment: total owner's equity. Types: real.),
(tot_liab_own_eq, Comment: total liabilities and owner's equity. Types: real.)
]
''',

'''
Table: income_statement,
Column: [
(stk_code, Comment: securities code. Types: text.),
(oper_rev, Comment: operating income. Types: real.),
(net_int_inc, Comment: net interest income. Types: real.),
(int_inc, Comment: interest income. Types: real.),
(int_exp, Comment: interest expenses. Types: real.),
(fee_com_net_inc, Comment: net income from handling fees and commissions. Types: real.),
(fee_com_inc, Comment: fee and commission income. Types: real.),
(fee_com_exp, Comment: handling fees and commission expenses. Types: real.),
(inv_inc, Comment: investment income. Types: real.),
(inv_inc_assoc_jv, Comment: investment income from associates and joint ventures. Types: real.),
(fv_change_inc, Comment: income from changes in fair value. Types: real.),
(exch_gain_inc, Comment: exchange gains. Types: real.),
(oth_biz_inc, Comment: other business income. Types: real.),
(oper_exp, Comment: operating expenses. Types: real.),
(tax_n_surs, Comment: taxes and surcharges. Types: real.),
(gen_n_admin_exps, Comment: business and management fees. Types: real.),
(assets_imp_loss, Comment: assets impairment loss. Types: real.),
(oth_biz_costs, Comment: other business costs. Types: real.),
(oper_profit, Comment: operating profit. Types: real.),
(non_op_rev, Comment: non operating income. Types: real.),
(non_op_exp, Comment: non operating expenses. Types: real.),
(loss_disposal_nonc_assets, Comment: loss on disposal of non current assets. Types: real.),
(tot_profit, Comment: total profit. Types: real.),
(income_tax_exp, Comment: income tax expenses. Types: real.),
(net_profit, Comment: net profit. Types: real.),
(attr_parent_net_profit, Comment: net profit attributable to the owner of the parent company. Types: real.),
(minor_int_inc_loss, Comment: minority interest. Types: real.),
(basic_eps, Comment: basic earnings per share. Types: real.),
(diluted_eps, Comment: diluted earnings per share. Types: real.),
(oth_compre_inc, Comment: other comprehensive income. Types: real.),
(tot_compre_inc, Comment: total comprehensive income. Types: real.),
(attr_parent_shareholders_compre_inc, Comment: total comprehensive income attributable to shareholders of the parent company. Types: real.),
(minor_int_shareholders_compre_inc, Comment: total comprehensive income attributable to minority shareholders. Types: real.)
]
''',

'''
Table: cash_flow_statement,
Column: [
(stk_code, Comment: securities code. Types: text.),
(net_inc_cust_deposits_ib_deposits, Comment: net increase in customer deposits and interbank deposits. Types: real.),
(net_inc_borrowings_cb, Comment: net increase in borrowings from the central bank. Types: real.),
(net_inc_ib_borrowings, Comment: net increase in borrowing funds from other financial institutions. Types: real.),
(cash_int_commission_collected, Comment: cash received for interest, handling fees, and commissions. Types: real.),
(cash_oth_oper_activities, Comment: received other cash related to operating activities. Types: real.),
(op_cf_sub, Comment: subtotal of cash inflows from operating activities. Types: real.),
(cust_loans_net_inc, Comment: net increase in customer loans and advances. Types: real.),
(cenbank_interbank_net_inc, Comment: net increase in deposits with central bank and interbank funds. Types: real.),
(cash_pay_int_fees_com, Comment: cash paid for interest, handling fees, and commissions. Types: real.),
(cash_pay_emp, Comment: cash paid to and on behalf of employees. Types: real.),
(cash_pay_taxes, Comment: various taxes and fees paid. Types: real.),
(cash_pay_op_other, Comment: other cash payments related to operating activities. Types: real.),
(op_cf_out_sub, Comment: subtotal of cash outflows from operating activities. Types: real.),
(net_cf_op, Comment: net cash flow generated from operating activities. Types: real.),
(recv_investment, Comment: cash received from investment recovery. Types: real.),
(investment_income, Comment: cash received from obtaining investment income. Types: real.),
(cash_disposal_assets, Comment: net cash received from disposal of fixed assets, intangible assets, and other long-term assets. Types: real.),
(recv_other_invest, Comment: received other cash related to investment activities. Types: real.),
(inv_cf_in_sub, Comment: subtotal of cash inflows from investment activities. Types: real.),
(cash_pay_invest, Comment: cash paid for investment. Types: real.),
(cash_pay_assets, Comment: cash paid for the purchase and construction of fixed assets, intangible assets, and other long-term assets. Types: real.),
(cash_pay_inv_other, Comment: other cash payments related to investment activities. Types: real.),
(inv_cf_out_sub, Comment: subtotal of cash outflows from investment activities. Types: real.),
(net_cf_inv, Comment: net cash flow generated from investment activities. Types: real.),
(absorb_investment, Comment: cash received from absorbing investments. Types: real.),
(subsidiary_absorb_minority, Comment: cash received from subsidiaries absorbing minority shareholder investments. Types: real.),
(issue_bonds, Comment: cash received from issuing bonds. Types: real.),
(recv_other_fin, Comment: received other cash related to financing activities. Types: real.),
(fin_cf_in_sub, Comment: subtotal of cash inflows from financing activities. Types: real.),
(repay_debt, Comment: cash paid for debt repayment. Types: real.),
(distribute_dividends_profits, Comment: cash paid for distributing dividends, profits, or paying interest. Types: real.),
(subsidiary_pay_minority, Comment: dividends and profits paid by subsidiaries to minority shareholders. Types: real.),
(cash_pay_fin_other, Comment: other cash payments related to financing activities. Types: real.),
(fin_cf_out_sub, Comment: subtotal of cash outflows from financing activities. Types: real.),
(net_cf_fin, Comment: net cash flow generated from financing activities. Types: real.),
(fx_rate_change_cash, Comment: the impact of exchange rate changes on cash and cash equivalents. Types: real.),
(net_cf_cash_equiv, Comment: net increase in cash and cash equivalents. Types: real.),
(initial_cash_equiv, Comment: opening balance of cash and cash equivalents. Types: real.),
(final_cash_equiv, Comment: closing balance of cash and cash equivalents. Types: real.),
(cf_stmt_net_income, Comment: cash flow statement - net profit. Types: real.),
(asset_impairment_dec, Comment: asset impairment provision. Types: real.),
(fixed_asset_dep_amort_dec, Comment: depreciation of fixed assets, depletion of oil and gas assets, and depreciation of productive biological assets. Types: real.),
(intangible_asset_amortization, Comment: amortization of intangible assets. Types: real.),
(longterm_amortization, Comment: amortization of long-term deferred expenses. Types: real.),
(loss_disposal_fixed_assets_dec, Comment: losses on disposal of fixed assets, intangible assets, and other long-term assets. Types: real.),
(fixed_asset_scrap_loss, Comment: loss on scrapping of fixed assets. Types: real.),
(fair_value_change_loss, Comment: loss from changes in fair value. Types: real.),
(cf_stmt_fin_expenses, Comment: cash flow statement - financial expenses. Types: real.),
(investment_loss, Comment: investment losses. Types: real.),
(dit_asset_reduction, Comment: decrease in deferred income tax assets. Types: real.),
(dit_liability_increase, Comment: increase in deferred income tax liabilities. Types: real.),
(inventory_decrease, Comment: decrease in inventory. Types: real.),
(oper_receivables_decrease, Comment: reduction in operating receivables. Types: real.),
(oper_payables_increase, Comment: increase in operating payables. Types: real.),
(other, Comment: other. Types: real.),
(im_ncf_oper_activities, Comment: indirect method - net cash flow generated from operating activities. Types: real.),
(debt_converted_capital, Comment: debt converted to capital. Types: real.),
(conv_bonds_maturing_within_1y, Comment: convertible corporate bonds maturing within one year. Types: real.),
(fin_lease_additions_fixed_assets, Comment: fixed assets acquired through financing lease. Types: real.),
(cash_end_period, Comment: closing balance of cash. Types: real.),
(cash_begin_period, Comment: opening balance of cash. Types: real.),
(cash_eq_end_period, Comment: closing balance of cash equivalents. Types: real.),
(cash_eq_begin_period, Comment: opening balance of cash equivalents. Types: real.),
(im_ncf_cash_eq, Comment: indirect method - net increase in cash and cash equivalents. Types: real.)
]
'''
]

DOCUMENT = [
    ["the debt to asset ratio",
     "the debt to asset ratio = tot_liab / tot_assets"],

    ["current assets",
     "current assets = cash_cb + ib_deposits + prec_metals + trad_fas + deriv_assets + buyback_fas + int_receiv + loans_adv + avai_sale_fas + recv_invest"],

    ["current liabilities",
     "current liabilities = acc_deposits + emp_comp_pay + tax_pay + int_pay + est_liab + oth_liab"],

    ["current ratio",
     "current assets = cash_cb + ib_deposits + prec_metals + trad_fas + deriv_assets + buyback_fas + int_receiv + loans_adv + avai_sale_fas + recv_invest"],
    ["current ratio",
     "current liabilities = acc_deposits + emp_comp_pay + tax_pay + int_pay + est_liab + oth_liab"],
    ["current ratio",
     "current ratio = current assets / current liabilities"],

    ["equity ratio",
     "equity ratio = tot_own_eq / tot_assets"],

    ["net profit margin",
     "net profit margin = net_profit / oper_rev"],

    ["return on assets",
     "return on assets = net_profit / tot_assets"],

    ["operating cash flow ratio",
     "current liabilities = acc_deposits + emp_comp_pay + tax_pay + int_pay + est_liab + oth_liab"],
    ["operating cash flow ratio",
     "operating cash flow ratio = net_cf_op / current liabilities"],

    ["equity multiplier",
     "equity multiplier = tot_assets / tot_own_eq"],

    ["working capital",
     "current assets = cash_cb + ib_deposits + prec_metals + trad_fas + deriv_assets + buyback_fas + int_receiv + loans_adv + avai_sale_fas + recv_invest"],
    ["working capital",
     "current liabilities = acc_deposits + emp_comp_pay + tax_pay + int_pay + est_liab + oth_liab"],
    ["working capital",
     "working capital = current assets - current liabilities"],

    ["asset turnover",
     "asset turnover = oper_rev / tot_assets"],

    ["return on equity",
     "return on equity = net_profit / tot_own_eq"],

    ["cash flow return on assets",
     "cash flow return on assets = net_cf_op / tot_assets"],

    ["cash ratio",
     "current liabilities = acc_deposits + emp_comp_pay + tax_pay + int_pay + est_liab + oth_liab"],
    ["cash ratio",
     "cash ratio = cash_cb / current liabilities"],

    ["free cash flow",
     "free cash flow = net_cf_op - cash_pay_assets"],

    ["gross profit",
     "gross profit = oper_rev - oper_exp"],

    ["gross profit margin",
     "gross profit = oper_rev - oper_exp"],
    ["gross profit margin",
     "gross profit margin = gross profit / oper_rev"],

    ["operating net profit margin",
     "operating net profit margin = oper_profit / oper_rev"],

    ["financial expense ratio",
     "financial expense ratio = cf_stmt_fin_expenses / oper_rev"],

    ["capital expenditure ratio",
     "capital expenditure ratio = cash_pay_assets / oper_rev"],

    ["cash dividend ratio",
     "cash dividend ratio = distribute_dividends_profits / net_profit"],

    ["cash flow adequacy ratio",
     "cash flow adequacy ratio = net_cf_op / (cash_pay_assets + distribute_dividends_profits)"],

    ["net assets",
     "net assets and total owner's equity are the same"],

    ["total stockholder's equity",
     "total stockholder's equity and total owner's equity are the same"],

    ["shareholders' equity",
     "shareholders' equity and total owner's equity are the same"],
]


GRAPH_LIST = [
    ("Elem","current ratio"),
    ("Elem","current assets"),
    ("Elem","current liabilities"),
    ("Elem","the debt to asset ratio"),
    ("Elem","equity ratio"),
    ("Elem","net profit margin"),
    ("Elem","return on assets"),
    ("Elem","operating cash flow ratio"),
    ("Elem","equity multiplier"),
    ("Elem","working capital"),
    ("Elem","asset turnover"),
    ("Elem","return on equity"),
    ("Elem","cash flow return on assets"),
    ("Elem","cash ratio"),
    ("Elem","free cash flow"),
    ("Elem","gross profit"),
    ("Elem","gross profit margin"),
    ("Elem","operating net profit margin"),
    ("Elem","financial expense ratio"),
    ("Elem","capital expenditure ratio"),
    ("Elem","cash dividend ratio"),
    ("Elem","cash flow adequacy ratio"),

    ("Mid","cash flow adequacy ratio_0"),

    ("Col", "cash_cb"),
    ("Col", "ib_deposits"),
    ("Col", "prec_metals"),
    ("Col", "trad_fas"),
    ("Col", "deriv_assets"),
    ("Col", "buyback_fas"),
    ("Col", "int_receiv"),
    ("Col", "loans_adv"),
    ("Col", "avai_sale_fas"),
    ("Col", "recv_invest"),
    ("Col", "acc_deposits"),
    ("Col", "emp_comp_pay"),
    ("Col", "tax_pay"),
    ("Col", "int_pay"),
    ("Col", "est_liab"),
    ("Col", "oth_liab"),
    ("Col", "tot_liab"),
    ("Col", "tot_assets"),
    ("Col", "net_profit"),
    ("Col", "oper_rev"),
    ("Col", "tot_own_eq"),
    ("Col", "net_cf_op"),
    ("Col", "cash_pay_assets"),
    ("Col", "oper_exp"),
    ("Col", "oper_profit"),
    ("Col", "cf_stmt_fin_expenses"),
    ("Col", "distribute_dividends_profits"),

    # Current Ratio
    ("Op", "Dvd", "Elem", "current ratio", "Elem", "current assets", 0),
    ("Op", "Dvs", "Elem", "current ratio", "Elem", "current liabilities", 1),

    # Current Assets
    ("Op", "Add", "Elem", "current assets", "Col", "cash_cb"),
    ("Op", "Add", "Elem", "current assets", "Col", "ib_deposits"),
    ("Op", "Add", "Elem", "current assets", "Col", "prec_metals"),
    ("Op", "Add", "Elem", "current assets", "Col", "trad_fas"),
    ("Op", "Add", "Elem", "current assets", "Col", "deriv_assets"),
    ("Op", "Add", "Elem", "current assets", "Col", "buyback_fas"),
    ("Op", "Add", "Elem", "current assets", "Col", "int_receiv"),
    ("Op", "Add", "Elem", "current assets", "Col", "loans_adv"),
    ("Op", "Add", "Elem", "current assets", "Col", "avai_sale_fas"),
    ("Op", "Add", "Elem", "current assets", "Col", "recv_invest"),

    # Current Liabilities
    ("Op", "Add", "Elem", "current liabilities", "Col", "acc_deposits"),
    ("Op", "Add", "Elem", "current liabilities", "Col", "emp_comp_pay"),
    ("Op", "Add", "Elem", "current liabilities", "Col", "tax_pay"),
    ("Op", "Add", "Elem", "current liabilities", "Col", "int_pay"),
    ("Op", "Add", "Elem", "current liabilities", "Col", "est_liab"),
    ("Op", "Add", "Elem", "current liabilities", "Col", "oth_liab"),

    # Debt to Asset Ratio
    ("Op", "Dvd", "Elem", "the debt to asset ratio", "Col", "tot_liab", 0),
    ("Op", "Dvs", "Elem", "the debt to asset ratio", "Col", "tot_assets", 1),

    # Equity Ratio
    ("Op", "Dvd", "Elem", "equity ratio", "Col", "tot_own_eq", 0),
    ("Op", "Dvs", "Elem", "equity ratio", "Col", "tot_assets", 1),

    # Net Profit Margin
    ("Op", "Dvd", "Elem", "net profit margin", "Col", "net_profit", 0),
    ("Op", "Dvs", "Elem", "net profit margin", "Col", "oper_rev", 1),

    # Return on Assets
    ("Op", "Dvd", "Elem", "return on assets", "Col", "net_profit", 0),
    ("Op", "Dvs", "Elem", "return on assets", "Col", "tot_assets", 1),

    # Operating Cash Flow Ratio
    ("Op", "Dvd", "Elem", "operating cash flow ratio", "Col", "net_cf_op", 0),
    ("Op", "Dvs", "Elem", "operating cash flow ratio", "Elem", "current liabilities", 1),

    # Equity Multiplier
    ("Op", "Dvd", "Elem", "equity multiplier", "Col", "tot_assets", 0),
    ("Op", "Dvs", "Elem", "equity multiplier", "Col", "tot_own_eq", 1),

    # Working Capital
    ("Op", "Mnd", "Elem", "working capital", "Elem", "current assets", 0),
    ("Op", "Sub", "Elem", "working capital", "Elem", "current liabilities", 1),

    # Asset Turnover
    ("Op", "Dvd", "Elem", "asset turnover", "Col", "oper_rev", 0),
    ("Op", "Dvs", "Elem", "asset turnover", "Col", "tot_assets", 1),

    # Return on Equity
    ("Op", "Dvd", "Elem", "return on equity", "Col", "net_profit", 0),
    ("Op", "Dvs", "Elem", "return on equity", "Col", "tot_own_eq", 1),

    # Cash Flow Return on Assets
    ("Op", "Dvd", "Elem", "cash flow return on assets", "Col", "net_cf_op", 0),
    ("Op", "Dvs", "Elem", "cash flow return on assets", "Col", "tot_assets", 1),

    # Cash Ratio
    ("Op", "Dvd", "Elem", "cash ratio", "Col", "cash_cb", 0),
    ("Op", "Dvs", "Elem", "cash ratio", "Elem", "current liabilities", 1),

    # Free Cash Flow
    ("Op", "Mnd", "Elem", "free cash flow", "Col", "net_cf_op", 0),
    ("Op", "Sub", "Elem", "free cash flow", "Col", "cash_pay_assets", 1),

    # Gross Profit
    ("Op", "Mnd", "Elem", "gross profit", "Col", "oper_rev", 0),
    ("Op", "Sub", "Elem", "gross profit", "Col", "oper_exp", 1),

    # Gross Profit Margin
    ("Op", "Dvd", "Elem", "gross profit margin", "Elem", "gross profit", 0),
    ("Op", "Dvs", "Elem", "gross profit margin", "Col", "oper_rev", 1),

    # Operating Net Profit Margin
    ("Op", "Dvd", "Elem", "operating net profit margin", "Col", "oper_profit", 0),
    ("Op", "Dvs", "Elem", "operating net profit margin", "Col", "oper_rev", 1),

    # Financial Expense Ratio
    ("Op", "Dvd", "Elem", "financial expense ratio", "Col", "cf_stmt_fin_expenses", 0),
    ("Op", "Dvs", "Elem", "financial expense ratio", "Col", "oper_rev", 1),

    # Capital Expenditure Ratio
    ("Op", "Dvd", "Elem", "capital expenditure ratio", "Col", "cash_pay_assets", 0),
    ("Op", "Dvs", "Elem", "capital expenditure ratio", "Col", "oper_rev", 1),

    # Cash Dividend Ratio
    ("Op", "Dvd", "Elem", "cash dividend ratio", "Col", "distribute_dividends_profits", 0),
    ("Op", "Dvs", "Elem", "cash dividend ratio", "Col", "net_profit", 1),

    # Cash Flow Adequacy Ratio
    ("Op", "Dvd", "Elem", "cash flow adequacy ratio", "Col", "net_cf_op", 0),
    ("Op", "Dvs", "Elem", "cash flow adequacy ratio", "Mid", "cash flow adequacy ratio_0", 1),
    ("Op", "Add", "Mid", "cash flow adequacy ratio_0", "Col", "cash_pay_assets"),
    ("Op", "Add", "Mid", "cash flow adequacy ratio_0", "Col", "distribute_dividends_profits"),
]