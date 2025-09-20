# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BusAgency(models.Model):
    _name = 'bus.agency'
    _description = 'Bus Agency'
    _order = 'name'

    name = fields.Char(string='Bus Name', required=True)
    code = fields.Char(string='Bus Code', required=True)
    active = fields.Boolean(string='Active', default=True)
    row_layout = fields.Selection([
        ('2-3', '2-3'),
        ('2-2', '2-2'),
        ('1-1', '1-1'),
        ('2-1', '2-1'),
        ('1-2', '1-2'),
        ('3-2', '3-2'),
    ], string="Row Layout", required=True,tracking=True)
    total_row = fields.Integer(string="Total Rows", required=True,tracking=True)
    maximum = fields.Integer(string="Maximum Seats", compute='_compute_maximum', store=True,tracking=True)

    @api.depends('row_layout', 'total_row')
    def _compute_maximum(self):
        layout_map = {
            '2-3': 5,
            '2-2': 4,
            '1-1': 2,
            '2-1': 3,
            '1-2': 3,
            '3-2': 5,
        }
        for rec in self:
            layout_value = layout_map.get(rec.row_layout, 0)
            rec.maximum = layout_value * rec.total_row
    
    @api.constrains('name', 'code')
    def _check_unique_name_code(self):
        for record in self:
            if record.name:
                existing_name = self.search([('name', '=', record.name), ('id', '!=', record.id)])
                if existing_name:
                    raise ValidationError('A bus agency with the same name already exists')
            if record.code:
                existing_code = self.search([('code', '=', record.code), ('id', '!=', record.id)])
                if existing_code:
                    raise ValidationError('A bus agency with the same code already exists')
