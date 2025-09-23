from odoo import http
from odoo.http import request

class TravelController(http.Controller):

    @http.route('/my/travel/place', type='http', auth='user', website=True)
    def booking(self, **post):
        # Récupérer l'ID depuis l'URL
        route_id = post.get('route_id')
        route_line_id = post.get('route_line_id')

        # Vérifier que l'ID est bien un entier
        try:
            route_id = int(route_id)
        except (TypeError, ValueError):
            return "⚠️ Erreur : ID de route invalide."

        # Charger la route
        route = request.env['travel.route'].browse(route_id)

        # Vérifier si l'enregistrement existe vraiment
        if not route.exists():
            return "⚠️ Erreur : la route demandée n'existe pas ou a été supprimée."

        # Déterminer les heures à partir de la ligne sélectionnée ou par défaut la première
        line = False
        if route_line_id:
            try:
                route_line_id_int = int(route_line_id)
                line_candidate = request.env['travel.route.line'].browse(route_line_id_int)
                if line_candidate.exists() and line_candidate.route_id.id == route.id:
                    line = line_candidate
            except (TypeError, ValueError):
                line = False
        if not line:
            line = route.route_line_ids[:1]

        hour_start = line.hour_start if line else 0.0
        hour_end = line.hour_end if line else 0.0
        selected_route_line_id = line.id if line else False

        # Préparer les valeurs pour le template
        values = {
            'route': route,
            'route_id': route.id,
            'route_line_id': selected_route_line_id,
            'route_name': route.name,
            'price': route.price,
            'currency': route.currency,
            'departure_point': route.departure_point.name if route.departure_point else "",
            'arrival_point': route.arrival_point.name if route.arrival_point else "",
            'hour_start': hour_start,
            'hour_end': hour_end,
            'bus_agency_name': route.bus_agency.name if route.bus_agency else "",
        }

        return request.render('travel_management.travel_booking_place', values)
