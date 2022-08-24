# -*- coding: utf-8 -*-
{
    'name': "Partner Extends - Denteco",
    'author': "Xetechs GT",
    'support': 'Abraham Febres --> afebres@xetechs.com',
    'license': 'LGPL-3',
    'website': "http://www.xetechs.gt",
    'version': '1.0.1',

    'depends': [ 
        'base',
        'sale',
        'product'
    ],
    'data': [
        'data/ir_cron_data.xml',
        'data/procduct_category_data.xml',
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/res_users_views.xml',
        'views/account_views.xml',
        'views/sale_views.xml',
    ]
}

