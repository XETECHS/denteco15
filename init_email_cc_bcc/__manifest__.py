# -*- coding: utf-8 -*-
{
    'name': 'Email CC/BCC',
    'version': '15.0.1.0.2',
    'category': 'Extra Tools',
    'summary': 'Allow user can compose email with CC and BCC recipient',
    'author': 'Init Co. Ltd',
    'support': 'contact@init.vn',
    'website': 'https://init.vn/?utm_source=odoo-store&utm_medium=15&utm_campaign=email-cc-bcc',
    'license': 'LGPL-3',
    'price': '9',
    'currency': 'USD',
    'description': """
    We show CC/BCC input in compose email wizard, so that user can send email with CC/BCC recipients
    """,
    'depends': [
        "mail"
    ],
    'data': [
        # data

        # groups

        # views
        'views/mail_mail_view.xml',
        'views/mail_compose_message_view.xml',

        # wizard

        # report

        # menu

        # security
    ],
    'demo': [],
    'test': [],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
