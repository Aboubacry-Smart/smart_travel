from odoo import http
from odoo.http import request
import base64


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
                
                # Le numéro de place EST le numéro de siège lui-même
                place = seat
                
                # Debug - pour voir ce qui est reçu (à enlever en production)
                import logging
                _logger = logging.getLogger(__name__)
                _logger.info(f"Seat: {seat}, Place utilisée: {place}, Name: {name}, Phone: {phone}")

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

        # Render confirmation page with created orders and payment methods
        ids_param = request.params.get('ids') or post.get('ids')
        orders = request.env['travel.order'].sudo()
        if ids_param:
            try:
                ids_list = [int(i) for i in ids_param.split(',') if i]
                orders = orders.browse(ids_list)
            except Exception:
                orders = request.env['travel.order'].sudo()

        # Get payment methods
        payment_methods = request.env['payment.method'].sudo().search([
            ('active', '=', True)
        ])

        values = {
            'orders': orders,
            'payment_methods': payment_methods,
        }
        return request.render('travel_management.travel_booking_order', values)
    
    @http.route('/my/travel/order/pay', type='http', auth='user', website=True, methods=['POST'])
    def pay_travel_order(self, **post):
        order_ids = post.get('order_ids', '')
        payment_method_id = int(post.get('payment_method_id', 0))
        payment_proof = request.httprequest.files.get('payment_proof')

        if not order_ids or not payment_method_id:
            return request.redirect('/my/travel/order')

        try:
            ids_list = [int(i) for i in order_ids.split(',') if i]
            orders = request.env['travel.order'].sudo().browse(ids_list)
        except Exception:
            orders = request.env['travel.order'].sudo()

        payment_method = request.env['payment.method'].sudo().browse(payment_method_id)
        if not payment_method.exists():
            return request.redirect('/my/travel/order')

        # Traitement de la preuve de paiement
        payment_proof_data = False
        payment_proof_name = False
        
        if payment_proof and payment_proof.filename:
            try:
                # Lire le fichier et l'encoder en base64
                file_data = payment_proof.read()
                payment_proof_data = base64.b64encode(file_data)
                payment_proof_name = payment_proof.filename
                
                import logging
                _logger = logging.getLogger(__name__)
                _logger.info(f"Preuve de paiement uploadée: {payment_proof.filename}")
                
            except Exception as e:
                import logging
                _logger = logging.getLogger(__name__)
                _logger.error(f"Erreur lors de l'upload de la preuve de paiement: {str(e)}")

        # Mise à jour des commandes avec les informations de paiement
        for order in orders:
            order_vals = {
                'state': 'confirm',  # Utilise 'confirm' au lieu de 'paid' selon votre modèle
                'payment_method_id': payment_method.id,
            }
            
            # Enregistrer la preuve de paiement dans les champs appropriés
            if payment_proof_data and payment_proof_name:
                order_vals['payment_proof'] = payment_proof_data
                order_vals['payment_proof_filename'] = payment_proof_name
            
            order.sudo().write(order_vals)
            
            import logging
            _logger = logging.getLogger(__name__)
            _logger.info(f"Commande {order.id} mise à jour avec paiement - Méthode: {payment_method.name}, État: confirm")

        return request.redirect('/my/travel/order/confirmation?ids=' + ','.join(map(str, orders.ids)))
    
    @http.route('/my/travel/order/confirmation', type='http', auth='user', website=True)
    def travel_order_confirmation(self, **post):
        """Page de confirmation après paiement"""
        ids_param = request.params.get('ids')
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
        
        # Vous pouvez créer un template de confirmation séparé
        # return request.render('travel_management.travel_order_confirmation', values)
        
        # Ou rediriger vers une page existante avec un message de succès
        return request.render('travel_management.travel_booking_order', {
            'orders': orders,
            'success_message': 'Paiement enregistré avec succès!'
        })