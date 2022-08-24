# -*- coding: utf-8 -*- 

{
    'name': 'Electronic Invoice GT',
    'version': '1.1.5',
    'depends': [
        'account',
        'l10n_gt'
    ],
    'data': [
        'data/webservice_data.xml',
        'data/account_fe_phrase_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/company_views.xml',
        'views/account_move_views.xml',
        'views/account_journal_views.xml',
        'views/res_users_views.xml',
        'report/invoice_fel_template.xml',
        'report/action_report.xml',
        #'views/account_tax_views.xml',
    ]
}