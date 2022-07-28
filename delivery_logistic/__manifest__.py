# -*- coding: utf-8 -*-
{
    'name': "delivery_logistic",

    'summary': """Logística de inventario para de entregas a domicilio.""",

    'description': """
        Logística de inventario para entregas de productos a domicilio según rutas establecidas y métodos de envío.
    """,

    'author': "Proyectos Ágiles S. A.",
    'website': "http://www.pragsa.odoo.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Entregas',
    'license': 'LGPL-3',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'sale', 'account', 'fleet', 'delivery'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security_groups.xml',
        'data/sequences.xml',
        # 'data/routes.xml',
        'views/inherit_delivery_carrier.xml',
        'views/inherit_res_partner.xml',
        'views/inherit_sale_order.xml',
        'views/inherit_stock_picking.xml',
        'views/menus.xml',
        'views/routes_views.xml',
        'views/trip_views.xml',
        #'views/templates.xml',
        'wizards/wizard_trip_generator.xml',
        'report/trip_report.xml',
        'report/report_trip_templates.xml'
    ],
    'qweb': [
        "static/src/xml/stock_picking_tree_views.xml",
        "static/src/xml/trip_tree_views.xml",
    ],
    "installable": True,
    'assets': {
        'web.assets_backend': [
            #'delivery_logistic/static/src/js/stock_picking.js',
            #'delivery_logistic/static/src/js/trip.js',
        ],
    }
}
