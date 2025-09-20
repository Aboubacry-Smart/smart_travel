# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

class TravelBooking(http.Controller):
    @http.route('/my/travel', type='http', auth='user', website=True)
    def index(self):
        # Get all travel point
        travel_points = http.request.env['travel.point'].search([])

        values = {
            'travel_points': travel_points,
        }
        return http.request.render('travel_management.travel_booking_template', values)
    
    @http.route('/my/travel/search', type='http', auth='user', website=True)
    def search_route(self, **post):
        # Récupérer les IDs des points de départ et d'arrivée depuis le formulaire
        departure_id = post.get('departure_point')
        arrival_id = post.get('arrival_point')
        
        # Vérifier si les deux points sont sélectionnés
        if not departure_id or not arrival_id:
            return request.redirect('/my/travel?error=missing_points')
        
        # Convertir les IDs en entiers
        try:
            departure_id = int(departure_id)
            arrival_id = int(arrival_id)
        except (ValueError, TypeError):
            return request.redirect('/my/travel?error=invalid_points')
        
        # Vérifier si les points sont différents
        if departure_id == arrival_id:
            return request.redirect('/my/travel?error=same_points')
        
        # Rechercher une route existante entre ces deux points
        Route = request.env['travel.route']
        route = Route.search([
            ('departure_point', '=', departure_id),
            ('arrival_point', '=', arrival_id),
            ('state', '=', 'confirm')  # Uniquement les routes confirmées
        ], limit=1)
        
        # Préparer les valeurs à passer au template
        travel_points = request.env['travel.point'].search([])
        values = {
            'travel_points': travel_points,
            'departure_selected': departure_id,
            'arrival_selected': arrival_id,
        }
        
        # Si une route existe, l'ajouter aux valeurs
        if route:
            values['route_found'] = route
        else:
            values['route_not_found'] = True
            # Récupérer les noms des points pour le message
            departure_point = request.env['travel.point'].browse(departure_id)
            arrival_point = request.env['travel.point'].browse(arrival_id)
            values['departure_name'] = departure_point.name
            values['arrival_name'] = arrival_point.name
        
        return request.render('travel_management.travel_booking_template', values)

    