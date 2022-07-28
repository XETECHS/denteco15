# -*- coding: utf-8 -*-
{
    'name': "l10n_gt_sat",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Gerson Ovale",
    'website': "http://www.xetechs.com",
    'license': "LGPL-3",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    #'depends': ['base','account','account_tax_python','report_xlsx','stock','account_reports','purchase_stock'],
    'depends': ['l10n_gt','account_tax_python', 'account','purchase','report_xlsx'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/account_chart_template_data.xml',
        'data/product_dai_data.xml',
        'views/account_payment_report.xml',
        'views/account_report.xml',
        
        'views/account_move_views.xml',
        'views/account_tax.xml',
        'views/account_journal_view.xml',
        'views/product_template_view.xml',
        'views/report_libro_diario.xml',
        'views/stock_piking_view.xml',
        'views/account_payment_view.xml',
        'views/contract_views.xml',
        'views/res_partner_views.xml',
        'report/check_account_payment.xml',
        'wizard/account_report_libros_view.xml',
        'wizard/libro_contable_view.xml',
        'report/account_librofiscal_report_view.xml',
        'report/purchase_order_templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',

    ],
}
