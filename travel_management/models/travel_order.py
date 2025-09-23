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
    origin = fields.Char(string='Origin', readonly=True)
    origin_id = fields.Many2one(
        'travel.order',
        string="Origin Reservation",
        readonly=True
    )
    child_order_ids = fields.One2many(
        'travel.order',
        'origin_id',
        string="Linked Reservations"
    )
    child_order_count = fields.Integer(
        string="Nombre d'enfants",
        compute='_compute_child_order_count',
        store=False
    )

    def _compute_child_order_count(self):
        for order in self:
            order.child_order_count = self.env['travel.order'].search_count([('origin', '=', order.code)])

    def action_view_origin(self):
        self.ensure_one()

        # 🔹 Si le champ relationnel est défini → priorité
        if self.origin_id:
            return {
                'name': 'Origin Reservation',
                'type': 'ir.actions.act_window',
                'res_model': 'travel.order',
                'view_mode': 'form',
                'res_id': self.origin_id.id,
            }

        # 🔹 Sinon fallback avec le champ char `origin`
        elif self.origin:
            origin_order = self.env['travel.order'].search([('code', '=', self.origin)], limit=1)
            if origin_order:
                return {
                    'name': 'Origin Reservation',
                    'type': 'ir.actions.act_window',
                    'res_model': 'travel.order',
                    'view_mode': 'form',
                    'res_id': origin_order.id,
                }

        return False

    def action_view_children(self):
        self.ensure_one()

        domain = [('origin_id', '=', self.id)]

        if not self.child_order_ids and self.code:
            domain = [('origin', '=', self.code)]

        return {
            'name': 'Linked Reservations',
            'type': 'ir.actions.act_window',
            'res_model': 'travel.order',
            'view_mode': 'list,form',
            'domain': domain,
        }

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
        # 🔹 Synchroniser origin (char) -> origin_id (Many2one)
        for vals in vals_list:
            if vals.get('origin') and not vals.get('origin_id'):
                parent = self.env['travel.order'].search([('code', '=', vals['origin'])], limit=1)
                if parent:
                    vals['origin_id'] = parent.id
                    
        records = super().create(vals_list)

        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        group = self.env.ref('travel_management.group_travel_caissier', raise_if_not_found=False)

        for record in records:
            # 🔹 1. Création d'activités pour les caissiers
            if activity_type and group:
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

            # 🔹 2. Génération automatique de facture
            try:
                record._create_invoice()
            except Exception as e:
                record.message_post(
                    body=f"⚠️ Erreur lors de la génération de la facture : {str(e)}"
                )

            # 🔹 3. Synchronisation origin <-> origin_id
            if record.origin_id and not record.origin:
                record.origin = record.origin_id.code

        return records
    
    def write(self, vals):
        res = super().write(vals)

        # Synchroniser les autres réservations liées à l'origin
        if 'state' in vals:
            for order in self:
                # 🔹 Chercher les enfants liés (via origin_id de préférence)
                linked_orders = self.sudo().search([
                    ('origin_id', '=', order.id),
                    ('date', '=', order.date)
                ])

                # 🔹 Si aucun trouvé via origin_id, on garde fallback avec origin (char)
                if not linked_orders and order.code:
                    linked_orders = self.sudo().search([
                        ('origin', '=', order.code),
                        ('date', '=', order.date)
                    ])

                if linked_orders:
                    linked_orders.sudo().with_context(skip_invoice_sync=True).write({'state': vals['state']})

                # 🔹 Synchronisation avec la facture
                invoice = order.invoice_id
                if invoice:
                    new_state = vals['state']
                    try:
                        if new_state == 'draft':
                            if invoice.state != 'draft':
                                invoice.button_draft()
                                invoice.message_post(
                                    body=f"La réservation {order.code} est repassée en brouillon."
                                )

                        elif new_state == 'confirm':
                            if invoice.state == 'draft':
                                invoice.action_post()
                                self._pay_invoice(invoice)
                                invoice.message_post(
                                    body=f"La réservation {order.code} a été confirmée et la facture validée et payée."
                                )

                        elif new_state == 'expired':
                            if invoice.state not in ['cancel']:
                                invoice.button_cancel()
                                invoice.message_post(
                                    body=f"La réservation {order.code} a expiré, facture annulée."
                                )

                    except Exception as e:
                        order.message_post(
                            body=f"⚠️ Erreur lors de la synchronisation avec la facture : {str(e)}"
                        )

        # 🔹 Synchroniser origin <-> origin_id après modification
        for rec in self:
            if rec.origin_id and not rec.origin:
                rec.origin = rec.origin_id.code

        return res

    def _pay_invoice(self, invoice, journal_id=None, amount=None):
        """Créer et valider directement le paiement d'une facture."""
        if not invoice:
            return False

        if invoice.state != 'posted':
            invoice.action_post()  # Il faut que la facture soit validée

        # Utiliser le montant restant si non précisé
        amount = amount or invoice.amount_residual

        # Choisir un journal (par défaut, le premier journal bancaire)
        if not journal_id:
            journal_id = self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id

        # Créer le wizard en mémoire (pas en BDD)
        payment_register = self.env['account.payment.register'].with_context(active_model='account.move', active_ids=invoice.ids).create({
            'amount': amount,
            'journal_id': journal_id,
            'payment_date': fields.Date.context_today(self),
            'payment_method_line_id': self.env['account.payment.method.line'].search([
                ('journal_id', '=', journal_id),
                ('payment_method_id.payment_type', '=', 'inbound')
            ], limit=1).id,
        })

        # Créer le paiement réel
        payment = payment_register.action_create_payments()
        return payment

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

