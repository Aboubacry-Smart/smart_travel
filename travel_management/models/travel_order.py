# Suggestion pour votre modèle travel.order

from odoo import fields, models, api
from io import BytesIO
import random
import string
import base64


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
    state = fields.Selection([
        ('draft', 'Draft'), 
        ('confirm', 'Confirm'),
        ('expired', 'Expired')
    ], default='draft')
    payment_date = fields.Datetime(string='Payment Date', readonly=True)
    paid_by_user_id = fields.Many2one('res.users', string='Paid by', readonly=True)
    code = fields.Char(string='Code', readonly=True, default=lambda self: ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6)))
    qr_code = fields.Binary(string='QR Code', compute='_compute_qr_code')
    

    @api.depends('code')
    def _compute_qr_code(self):
        for record in self:
            if record.code:
                try:
                    import qrcode
                    # Build an absolute URL to be embedded in the QR code
                    base_url = record.env['ir.config_parameter'].sudo().get_param('web.base.url') or ''
                    ticket_url = f"{base_url}/my/travel/ticket/{record.code}"
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(ticket_url)
                    qr.make(fit=True)
                    img = qr.make_image(fill='black', back_color='white')
                    buffer = BytesIO()
                    img.save(buffer)
                    record.qr_code = base64.b64encode(buffer.getvalue())
                except ImportError:
                    record.qr_code = False