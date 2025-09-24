# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class Travel(http.Controller):
    @http.route(['/my/package/<string:code>'], type='http', auth='public', website=True, methods=['GET'])
    def trip_package_public_view(self, code, **kwargs):
        Package = request.env['trip.package'].sudo()
        package = Package.search([('code', '=', code)], limit=1)
        values = {
            'found': bool(package),
            'package': package,
        }
        return request.render('travel_management.trip_package_public_view', values)

