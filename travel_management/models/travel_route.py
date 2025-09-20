# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TravelRoute(models.Model):
    _inherit = "mail.thread"
    _name = 'travel.route'
    _description = 'Travel Route'
    _order = 'name'
    
    name = fields.Char(string='Route Name', compute='_compute_name', store=True)
    departure_point = fields.Many2one('travel.point', string='Departure Point', required=True)
    arrival_point = fields.Many2one('travel.point', string='Arrival Point', required=True)
    bus_agency = fields.Many2one('bus.agency', string='Bus Name', required=True)
    driver_id = fields.Many2one('res.partner', string='Driver', required=True)
    hour_start = fields.Float(string='Hour Start', required=True)
    hour_end = fields.Float(string='Hour End', required=True)
    duration = fields.Char(string="Duration", compute="_compute_duration", store=True)
    state = fields.Selection([('draft','Draft'),('confirm','Confirm'),('cancel','Cancel')],default='draft',string="Status",tracking=True)
    price = fields.Float(string='Price', required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.user.company_id.currency_id)
    currency = fields.Char(related='currency_id.symbol', string='Currency')
    travels_ids = fields.One2many('travel.order', 'route_id', string='Travels')

    def action_move_confirm(self):
        if self.price > 0 and self.hour_start < self.hour_end:
            self.state ='confirm'
        else:
            raise ValidationError('Le prix doit etre superieur a 0 et l\'heure de depart doit etre inferieur a l\'heure de fin')
    
    def action_move_cancel(self):
        self.state ='cancel'

    def action_move_draft(self):
        self.state='draft'

    @api.depends('hour_start', 'hour_end')
    def _compute_duration(self):
        for record in self:
            record.duration = record.hour_end - record.hour_start
    
    @api.depends('departure_point', 'arrival_point')
    def _compute_name(self):
        for record in self:
            record.name = '{} - {}'.format(record.departure_point.name, record.arrival_point.name)

    @api.constrains('name')
    def _check_unique_name(self):
        self._cr.execute("SELECT id FROM travel_route WHERE name = %s", (self.name,))
        if self._cr.fetchone() and not self.env.context.get('import_file'):
            raise ValidationError('A route with the same name already exists')

    @api.constrains('departure_point', 'arrival_point')
    def _check_departure_arrival(self):
        for record in self:
            if record.departure_point == record.arrival_point:
                raise ValidationError('Departure point and arrival point cannot be the same')