# -*- coding: utf-8 -*-

from odoo import models, fields


class PaymentMethod(models.Model):
    _name = 'payment.method'
    _description = 'Payment Method'

    qr_code = fields.Image(string='QR Code', max_width=1024, max_height=1024)