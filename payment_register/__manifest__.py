# -*- coding: utf-8 -*-
{
    'name': "payment_register",

    'summary': """
        Circular y Nota para los registros de pago.""",

    'description': """
        Agregando circular y nota a los pagos múltiples de facturas
    """,

    'author': "Soluciones Ágiles S. A.",
    'website': "http://www.inteligos.gt",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Pagos',
    'license': 'LGPL-3',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'l10n_gt_check_printing'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/inherit_account_payment_register_view.xml',
    ],
}
