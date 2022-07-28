# -*- coding: utf-8 -*-
{
    'name': "product_brands",

    'summary': """
        Marcas de Productos""",

    'description': """
        Clasificar los productos por Marcas
    """,

    'author': "3Digital",
    'website': "http://www.3digital.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'license': 'LGPL-3',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['product', 'stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/product_brand_view.xml',
    ],

}