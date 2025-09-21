# Suggestion pour votre modèle travel.order

from odoo import fields, models
import random
import string

class TravelOrder(models.Model):
    _name = 'travel.order'
    _description = 'Travel Order' 
    
    route_id = fields.Many2one('travel.route', string='Route', required=True)
    passenger_id = fields.Many2one('res.partner', string='Passenger', required=True)
    passenger_name = fields.Char(related='passenger_id.name')
    passenger_phone = fields.Char(related='passenger_id.phone')
    passenger_sexe = fields.Selection(related='passenger_id.sexe')
    place = fields.Integer(string='Place', required=True)
    payment_method_id = fields.Many2one('payment.method', string='Payment Method')
    payment_proof = fields.Binary(string='Payment Proof')
    payment_proof_filename = fields.Char(string='Payment Proof Filename')
    code = fields.Char(string='Code', readonly=True, default=lambda self: ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6)))
    state = fields.Selection([
        ('draft', 'Draft'), 
        ('confirm', 'Confirm'),
        ('expired', 'Expired')
    ], default='draft')
    payment_date = fields.Datetime(string='Payment Date', readonly=True)
    paid_by_user_id = fields.Many2one('res.users', string='Paid by', readonly=True)
    
