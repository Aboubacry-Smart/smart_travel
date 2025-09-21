# -*- coding: utf-8 -*-

from odoo import models, fields


class PaymentMethod(models.Model):
    _inherit = 'payment.method'

    qr_code = fields.Image(string='QR Code', max_width=480, max_height=480) 