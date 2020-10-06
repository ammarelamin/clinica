# -*- coding: utf-8 -*-
{
    'name': "Clinica",

    'summary': """
        Beauty center management module""",

    'description': """
        ERP system to manage all the clinic operations
    """,

    'author': "Ammar Elamin",
    # 'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Health',
    'version': '1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'calendar', 'account', 'om_account_accountant', 'stock', 'point_of_sale'],

    # always loaded
    'data': [
        'security/clinic_security.xml',
        'security/ir.model.access.csv',
        'views/base.xml',
        'views/laboratory.xml',
        'views/setting.xml',
        'views/sits_room.xml',
        'views/templates.xml',
        'sequence.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
