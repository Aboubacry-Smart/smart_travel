# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class TravelPoint(models.Model):
    _name = 'travel.point'
    _description = 'Travel Point'
    _order = 'name'

    name = fields.Char(string='Point Name', required=True)
    code = fields.Char(string='Point Code')
    

    @api.constrains('name', 'code')
    def _check_unique_name_code(self):
        for record in self:
            self._cr.execute(
                "SELECT id FROM travel_point WHERE (name = %s OR code = %s) AND id != %s",
                (record.name, record.code, record.id or 0)
            )
        res = self._cr.fetchone()
        if res:
            raise ValidationError('A travel point with the same name or code already exists')
