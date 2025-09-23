# -*- coding: utf-8 -*-
{
    'name': "Smart Travel Management",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'website', 'payment'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/travel_point_views.xml',
        'views/travel_route_views.xml',
        'views/trip_package_views.xml',
        'views/bus_agency_views.xml',
        'portal_views/travel_menu.xml',
        'portal_views/travel_booking.xml',
        'portal_views/travel_booking_place.xml',
        'portal_views/travel_booking_order.xml',
        'portal_views/travel_booking_ticket.xml',
        'views/payment_method.xml',
        'views/travel_order.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    'post_init_hook': 'post_init_hook',
}

