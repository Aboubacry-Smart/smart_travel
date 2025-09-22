from odoo import http
from odoo.http import request

class TravelBookingTicketController(http.Controller):
    @http.route(['/my/travel/ticket/<string:code>'], type='http', auth='public', website=True)
    def ticket_status(self, code, **kwargs):
        Order = request.env['travel.order'].sudo()
        order = Order.search([('code', '=', code)], order='id desc', limit=1)

        context = {
            'found': bool(order),
            'order': order,
            'status': order.state if order else None,
        }
        return request.render('travel_management.travel_booking_ticket', context)