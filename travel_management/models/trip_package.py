# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TripPackage(models.Model):
    _name = 'trip.package'
    _description = 'Trip Package'
    _order = 'name'

    name = fields.Char(string='Package Name', required=True)
    code = fields.Char(string='Package Code', required=True)
    travel_route = fields.Many2one('travel.route', string='Travel Route', required=True)
    driver_id = fields.Many2one('res.partner', string='Driver', required=True)
    owner_id = fields.Many2one('res.partner', string='Owner', required=True)