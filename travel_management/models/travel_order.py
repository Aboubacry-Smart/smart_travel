# Suggestion pour votre modèle travel.order

from odoo import fields, models, api
from io import BytesIO
import random
import string
import base64


class TravelOrder(models.Model):
    _name = 'travel.order'
    _description = 'Travel Order' 
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    route_id = fields.Many2one('travel.route', string='Route', required=True)
    route_line_id = fields.Many2one('travel.route.line', string='Route Line', help="Selected departure for this order")
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
    ], default='draft', tracking=True)
    payment_date = fields.Datetime(string='Payment Date', readonly=True)
    paid_by_user_id = fields.Many2one('res.users', string='Paid by', readonly=True)
    code = fields.Char(string='Code', readonly=True, default=lambda self: ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6)))
    qr_code = fields.Binary(string='QR Code', compute='_compute_qr_code')
    date = fields.Datetime(string='Date',)
    invoice_id = fields.Many2one('account.move', string="Invoice", readonly=True, copy=False, tracking=True)

    def write(self, vals):
        res = super().write(vals)

        if 'state' in vals:
            for order in self:
                invoice = order.invoice_id
                if invoice:
                    new_state = vals['state']
                    try:
                        if new_state == 'draft':
                            # Remettre la facture en brouillon
                            if invoice.state != 'draft':
                                invoice.button_draft()
                                invoice.message_post(body=f"La réservation {order.code} est repassée en brouillon.")

                        elif new_state == 'confirm':
                            # Valider la facture si elle est en brouillon
                            if invoice.state == 'draft':
                                invoice.action_post()
                                invoice.message_post(body=f"La réservation {order.code} a été confirmée et la facture validée.")

                        elif new_state == 'expired':
                            # Annuler la facture
                            if invoice.state not in ['cancel']:
                                invoice.button_cancel()
                                invoice.message_post(body=f"La réservation {order.code} a expiré, facture annulée.")
                    
                    except Exception as e:
                        # Log l'erreur sans bloquer le processus
                        order.message_post(body=f"Erreur lors de la synchronisation avec la facture: {str(e)}")
                        
        return res

    def action_view_invoice(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': self.invoice_id.id,
        }

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

    @api.model_create_multi
    def create(self, vals_list):
        records = super(TravelOrder, self).create(vals_list)
        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        group = self.env.ref('travel_management.group_travel_caissier', raise_if_not_found=False)

        if activity_type and group:
            for record in records:
                for user in group.users:
                    try:
                        record.activity_schedule(
                            activity_type_id=activity_type.id,
                            summary="Nouvelle réservation",
                            note=f"Réservation {record.code or record.id} créée. Merci de traiter.",
                            user_id=user.id,
                            date_deadline=fields.Date.today(),
                        )
                    except Exception:
                        continue

        # 🔥 Génération automatique de facture après création
        for record in records:
            record._create_invoice()

        return records


    def _create_invoice(self):
        """Créer une facture client automatiquement à partir de la réservation"""
        for order in self:
            if not order.passenger_id or not order.route_id:
                continue

            # Utiliser le produit associé à la route
            product = order.route_id.product_id
            if not product:
                # fallback : créer un produit si la route n’en a pas
                product = self.env['product.product'].create({
                    'name': f"Billet {order.route_id.name or ''}",
                    'type': 'service',
                    'list_price': order.route_id.price or 0.0,
                })
                order.route_id.product_id = product.id  # lier le produit à la route

            # Créer la facture
            invoice_vals = {
                'move_type': 'out_invoice',
                'partner_id': order.passenger_id.id,
                'invoice_origin': order.code,
                'invoice_date': fields.Date.context_today(self),
                'invoice_line_ids': [(0, 0, {
                    'product_id': product.id,
                    'name': f"Billet {order.route_id.name or ''}",
                    'quantity': 1,
                    'price_unit': order.route_id.price,
                })]
            }
            invoice = self.env['account.move'].create(invoice_vals)

            # Lier la facture à la réservation
            order.invoice_id = invoice.id

