from odoo import http
from odoo.http import request

class TravelBookingTicketController(http.Controller):

    @http.route(['/my/ticket'], type='http', auth='public', website=True)
    def ticket(self, **kwargs):
        """Affiche le formulaire de recherche du ticket"""
        return request.render('travel_management.travel_booking_ticket_search')

    @http.route(['/my/travel/ticket/<string:code>'], type='http', auth='public', website=True)
    def ticket_status(self, code, **kwargs):
        """Recherche par URL directe (GET)"""
        Order = request.env['travel.order'].sudo()
        order = Order.search([('code', '=', code)], order='id desc', limit=1)

        user = request.env.user
        is_agent = user.has_group('travel_management.group_travel_agent') if user else False

        values = {
            'found': bool(order),
            'order': order,
            'status': order.state if order else None,
            'is_agent': is_agent,
        }
        return request.render('travel_management.travel_booking_ticket', values)

    @http.route(['/my/travel/ticket'], type='http', auth='public', methods=['POST'], website=True, csrf=False)
    def ticket_status_post(self, **post):
        """Recherche par POST (ex: scan de ticket ou formulaire)"""
        code = post.get('code')
        Order = request.env['travel.order'].sudo()
        order = Order.search([('code', '=', code)], order='id desc', limit=1)

        user = request.env.user
        is_agent = user.has_group('travel_management.group_travel_agent') if user else False

        values = {
            'found': bool(order),
            'order': order,
            'status': order.state if order else None,
            'is_agent': is_agent,
        }
        return request.render('travel_management.travel_booking_ticket', values)

    
