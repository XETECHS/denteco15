# -*- coding: utf-8 -*-
{
    'name': "td_generico_gt",

    'summary': """
        Tropicalización de 3Digital para Guatemala.""",

    'description': """
        Tipos de Documento
        Impuestos
        Datos fiscales en facturas
        Posiciones Fiscales
    """,

    'author': "Inteligos S.A.",
    'website': "http://www.3digital.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'accounting',
    'license': 'LGPL-3',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base','account','account_accountant','l10n_latam_base','l10n_latam_invoice_document',
                'account_tax_python', 'account_check_printing'],

    # always loaded
    'data': [
        # 'security/security.xml',
        # 'data/l10n_latam.document.type.csv',
        # 'data/l10n_latam_identification_type_data.xml',
        # 'data/l10n_gt_chart_data.xml',
        # 'data/account.account.template.csv',
        # 'data/l10n_gt_chart_post_data.xml',
        # 'data/account_tax_group_data.xml',
        # 'data/account_taxes_data.xml',
        # 'data/account_fiscal_template.xml',
        # 'data/res_country_group_data.xml',
        # 'views/account_account_view.xml',
        # 'views/account_move_view.xml',
        # 'views/account_payment_view.xml',
        # 'views/res_currency_view.xml',
        'views/res_partner_view.xml',
        # 'views/sale_order_view.xml',
        # 'views/stock_production_lot_views.xml',
        # 'views/td_generico_invoice_view.xml',
        # 'views/inherit_product_template_view.xml',
        # 'views/inherit_res_config_settings_account_views.xml',
        # 'views/invoice_cancel_view.xml',
        # 'views/report_invoice.xml',
      ],

}