# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TravelRouteLine(models.Model):
    _name = 'travel.route.line'
    _description = 'Travel Route Line'
    _order = 'hour_start'

    route_id = fields.Many2one('travel.route', string='Route', required=True, ondelete='cascade')
    hour_start = fields.Float(string='Hour Start', required=True)
    hour_end = fields.Float(string='Hour End', required=True)
    duration = fields.Float(string="Duration (hours)", compute="_compute_duration", store=True)

    order_count = fields.Integer(string="Nombre de réservations", compute="_compute_order_count")

    def _compute_order_count(self):
        for line in self:
            line.order_count = self.env['travel.order'].search_count([('route_line_id', '=', line.id)])

    def action_open_orders(self):
        return {
            'name': 'Réservations',
            'type': 'ir.actions.act_window',
            'res_model': 'travel.order',
            'view_mode': 'list,form',
            'domain': [('route_line_id', '=', self.id)],
            'context': {'default_route_line_id': self.id},
        }

    @api.depends('hour_start', 'hour_end')
    def _compute_duration(self):
        for rec in self:
            if rec.hour_start is not None and rec.hour_end is not None:
                rec.duration = rec.hour_end - rec.hour_start
            else:
                rec.duration = 0.0

    @api.constrains('hour_start', 'hour_end')
    def _check_hours(self):
        for rec in self:
            if rec.hour_start >= rec.hour_end:
                raise ValidationError(_('Start hour must be before end hour.'))
