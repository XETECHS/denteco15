# -*- coding: utf-8 -*-
{
    'name': "payments_and_orders",

    'summary': """Realizar pagos desde los pedidos.""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Proyectos Ágiles S. A.",
    'website': "http://www.inteligos.gt",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'license': 'LGPL-3',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'td_generico_gt','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/inherit_account_payment_order_count.xml',
        'views/inherit_sale_order_to_receive_payment.xml',
    ],
}
