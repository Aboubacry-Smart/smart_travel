# -*- coding: utf-8 -*-

from odoo import models, fields


class TravelOrder(models.Model):
    _name = 'travel.order'
    _description = 'Travel Order'
    
    route_id = fields.Many2one('travel.route', string='Route', required=True)
    passenger_id = fields.Many2one('res.partner', string='Passenger', required=True)
    passenger_name = fields.Char(related='passenger_id.name')
    passenger_phone = fields.Char(related='passenger_id.phone')
    passenger_sexe = fields.Selection(related='passenger_id.sexe')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')], default='draft')