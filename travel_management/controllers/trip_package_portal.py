# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class TripPackagePortal(http.Controller):
    @http.route(['/my/package', '/my/package/'], type='http', auth='public', website=True, methods=['GET', 'POST'])
    def trip_package_search(self, **post):
        code = (post.get('code') or request.params.get('code') or '').strip()
        package = False
        found = False
        if code:
            Package = request.env['trip.package'].sudo()
            package = Package.search([('code', '=', code)], limit=1)
            found = bool(package)
        values = {
            'code': code,
            'package': package,
            'found': found,
        }
        return request.render('travel_management.trip_package_search', values)

    @http.route(['/my/package/<string:code>'], type='http', auth='public', website=True, methods=['GET', 'POST'])
    def trip_package_view(self, code, **kwargs):
        Package = request.env['trip.package'].sudo()
        package = Package.search([('code', '=', code)], limit=1)
        values = {
            'found': bool(package),
            'package': package,
        }
        return request.render('travel_management.trip_package_view', values)


