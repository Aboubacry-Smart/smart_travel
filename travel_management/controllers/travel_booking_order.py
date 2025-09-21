from odoo import http
from odoo.http import request


class TravelBookingOrderController(http.Controller):
    @http.route('/my/travel/order', type='http', auth='user', website=True, methods=['GET', 'POST'])
    def travel_order(self, **post):
        # Handle form submission (create orders) then redirect to confirmation
        if request.httprequest.method == 'POST':
            route_id = int((post.get('route_id') or 0))
            selected_seats = (post.get('selected_seats') or '').split(',') if post.get('selected_seats') else []

            created_order_ids = []
            for seat in [s for s in selected_seats if s]:
                name = (post.get(f'passenger_{seat}_name') or '').strip()
                phone = (post.get(f'passenger_{seat}_phone') or '').strip()
                gender = (post.get(f'passenger_{seat}_gender') or '').strip()
                place = (post.get(f'passenger_{seat}_place') or '').strip()

                # Find or create passenger partner
                Partner = request.env['res.partner'].sudo()
                partner = Partner.search([('name', '=', name), ('phone', '=', phone)], limit=1)
                if not partner:
                    vals = {'name': name, 'phone': phone}
                    # Set gender if field exists on res.partner
                    if 'sexe' in Partner._fields and gender:
                        vals['sexe'] = gender
                    partner = Partner.create(vals)

                order_vals = {
                    'route_id': route_id,
                    'passenger_id': partner.id,
                    'place': place,
                }
                order = request.env['travel.order'].sudo().create(order_vals)
                created_order_ids.append(order.id)

            return request.redirect('/my/travel/order?ids=' + ','.join(map(str, created_order_ids)))

        # Render confirmation page with created orders
        ids_param = request.params.get('ids') or post.get('ids')
        orders = request.env['travel.order'].sudo()
        if ids_param:
            try:
                ids_list = [int(i) for i in ids_param.split(',') if i]
                orders = orders.browse(ids_list)
            except Exception:
                orders = request.env['travel.order'].sudo()

        values = {
            'orders': orders,
        }
        return request.render('travel_management.travel_booking_order', values)