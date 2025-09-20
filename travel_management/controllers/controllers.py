# -*- coding: utf-8 -*-
# from odoo import http


# class ./smartTravel/travelManagement(http.Controller):
#     @http.route('/./smart_travel/travel_management/./smart_travel/travel_management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/./smart_travel/travel_management/./smart_travel/travel_management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('./smart_travel/travel_management.listing', {
#             'root': '/./smart_travel/travel_management/./smart_travel/travel_management',
#             'objects': http.request.env['./smart_travel/travel_management../smart_travel/travel_management'].search([]),
#         })

#     @http.route('/./smart_travel/travel_management/./smart_travel/travel_management/objects/<model("./smart_travel/travel_management../smart_travel/travel_management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('./smart_travel/travel_management.object', {
#             'object': obj
#         })

