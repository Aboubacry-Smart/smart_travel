# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    sexe = fields.Selection([('male','Male'),('female','Female')], string='Sexe')
    is_driver = fields.Boolean(string='Is Driver', default=False)
    is_passenger = fields.Boolean(string='Is Passenger', default=False)
    is_trip_owner = fields.Boolean(string='Is Trip Owner', default=False)
    