# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from io import BytesIO
import base64
import random
import string


class TripPackage(models.Model):
    _name = 'trip.package'
    _description = 'Trip Package'
    _order = 'name'

    name = fields.Char(string='Package Name', required=True)
    code = fields.Char(string='Package Code', readonly=True, copy=False, index=True, default=lambda self: ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6)))
    qr_code = fields.Binary(string='QR Code', compute='_compute_qr_code', store=False)
    state = fields.Selection([
        ('pending', 'En attente'),
        ('boarded', 'Embarqué'),
        ('arrived', 'Arrivé'),
    ], string='State', default='pending', tracking=True)
    travel_route = fields.Many2one('travel.route', string='Travel Route', required=True)
    driver_id = fields.Many2one('res.partner', string='Driver', required=True)
    owner_id = fields.Many2one('res.partner', string='Owner', required=True)

    @api.depends('code')
    def _compute_qr_code(self):
        for record in self:
            if record.code:
                try:
                    import qrcode
                    # Build absolute URL for public package page
                    base_url = record.env['ir.config_parameter'].sudo().get_param('web.base.url') or ''
                    package_url = f"{base_url}/my/package/{record.code}"
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(package_url)
                    qr.make(fit=True)
                    img = qr.make_image(fill='black', back_color='white')
                    buffer = BytesIO()
                    img.save(buffer)
                    record.qr_code = base64.b64encode(buffer.getvalue())
                except Exception:
                    record.qr_code = False

    def action_print_package(self):
        self.ensure_one()
        return self.env.ref('travel_management.action_travel_trip_ticket').report_action(self)