# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


from datetime import timedelta
import re
import uuid


class AccountMoveInherited(models.Model):
    _inherit = "account.move"

    # campo para calculo de fecha de pago segun configuracion de dias
    @api.depends('invoice_date', 'invoice_date_due')
    def _compute_invoice_date(self):
        """
        Actualización del 21.05.2021
        Mejora a código de computación de los campos:
            credit_days
            payment_date
        Reducción de código y mejora en la legibilidad del mismo.
        Aparte solución a fallo al no ingresar una fecha de factura de forma manual,
        ya que esto impedia calcular los dias credito y la fecha de pago.
        :return:
        """
        for record in self:
            day = record.invoice_date or fields.Date.today()
            record.credit_days = (record.invoice_date_due - day).days if record.invoice_date_due else 0
            payment_day = record.env.company.payment_day or 4
            if payment_day - day.weekday() <= 0:
                date = day - timedelta(days=day.weekday()) + timedelta(days=payment_day, weeks=1)
            else:
                date = day - timedelta(days=day.weekday()) + timedelta(days=payment_day)
            record.payment_date = date.strftime("%d/%m/%Y")

    #  Campos para busqueda por NIT y Razon Social en Contabilidad, Ventas y CRM
    nit = fields.Char(related="partner_id.vat", string="NIT")
    legal_name = fields.Char(related="partner_id.legal_name", string="Razón Social")

    """Cambio para llevar control de dias de credito para la factura."""
    credit_days = fields.Integer(store=True, compute='_compute_invoice_date', string="Días crédito")

    invoice_doc_type = fields.Many2one(
        'l10n_latam.document.type', string='Tipo Documento', copy=False, index=True,
    )  # states={'posted': [('readonly', True)]}
    invoice_doc_serie = fields.Char("Serie", copy=False)  # , states={'posted': [('readonly', True)]}
    invoice_doc_number = fields.Char("Numero", copy=False)  # , states={'posted': [('readonly', True)]}
    amount_tax_total = fields.Monetary(string='Total Impuestos',
                                       store=True, readonly=True, compute='_compute_amount')
    amount_retained_tax_total = fields.Monetary(string='Total Impuesto Retenido',
                                                store=True, readonly=True, compute='_compute_amount')
    amount_retained_vat_total = fields.Monetary(string='IVA Retenido',
                                                store=True, readonly=True, compute='_compute_amount')
    amount_retained_isr_total = fields.Monetary(string='ISR Retenido',
                                                store=True, readonly=True, compute='_compute_amount')
    invoice_ref = fields.Char(string="Referencia", compute="_set_reference")

    # Necesario para Coversion segun tasa de cambio
    amount_total_signed_2 = fields.Monetary(string="Total segun Tasa de Cambio", readonly=True)
    rate_invoice = fields.Float(string='Tasa de Cambio', readonly=True, digits=(1, 6), compute='_compute_rate_invoice')

    # campo para calculo de fecha de pago segun configuracion de dias
    payment_date = fields.Char(
        compute='_compute_invoice_date',
        help='Aquí va la fecha de la entrega del pago del pedido de compra, '
             'de formma estandar se traslada al siguiente viernes de la fecha de confirmacion de la compra.',
        string="Fecha Entrega de Pago"
    )

    @api.model
    @api.depends('currency_id')
    def _compute_rate_invoice(self):
        for record in self:
            rate_invoice = [r['rate'] for r in record['currency_id']['rate_ids']
                            if record['invoice_date'] == r['name']]
            if rate_invoice:
                record.rate_invoice = rate_invoice[0]
            elif record['company_id']['currency_id']['rate_ids']:
                rate_invoice = [r['rate'] for r in record['company_id']['currency_id']['rate_ids']
                                if record['invoice_date'] == r['name']]
                if rate_invoice:
                    record.rate_invoice = rate_invoice[0]
                else:
                    record.rate_invoice = record['company_id']['currency_id']['rate']
            else:
                record.rate_invoice = record['currency_id']['rate']

    # Necesario para Coversion segun tasa de cambio

    def _set_reference(self):
        for rec in self:
            if rec.invoice_doc_serie:
                rec.invoice_ref = '%s %s-%s' % (
                    rec.invoice_doc_type.name, rec.invoice_doc_serie, rec.invoice_doc_number)
            else:
                rec.invoice_ref = '%s %s' % (rec.invoice_doc_type.name, rec.invoice_doc_number)

    def post(self):
        for move in self:
            if not move.line_ids.filtered(lambda line: not line.display_type):
                raise UserError(_('You need to add a line before posting.'))
            if move.auto_post and move.date > fields.Date.today():
                date_msg = move.date.strftime(self.env['res.lang']._lang_get(self.env.user.lang).date_format)
                raise UserError(_("This move is configured to be auto-posted on %s" % date_msg))

            if not move.partner_id:
                if move.is_sale_document():
                    raise UserError(
                        _("The field 'Customer' is required, please complete it to validate the Customer Invoice."))
                elif move.is_purchase_document():
                    raise UserError(
                        _("The field 'Vendor' is required, please complete it to validate the Vendor Bill."))

            if move.is_invoice(include_receipts=True) and float_compare(move.amount_total, 0.0,
                                                                        precision_rounding=move.currency_id.rounding) < 0:
                raise UserError(_(
                    "You cannot validate an invoice with a negative total amount. You should create a credit note instead. Use the action menu to transform it into a credit note or refund."))

            # Handle case when the invoice_date is not set. In that case, the invoice_date is set at today and then,
            # lines are recomputed accordingly.
            # /!\ 'check_move_validity' must be there since the dynamic lines will be recomputed outside the 'onchange'
            # environment.
            if not move.invoice_date and move.is_invoice(include_receipts=True):
                move.invoice_date = fields.Date.context_today(self)
                move.with_context(check_move_validity=False)._onchange_invoice_date()

            # When the accounting date is prior to the tax lock date, move it automatically to the next available date.
            # /!\ 'check_move_validity' must be there since the dynamic lines will be recomputed outside the 'onchange'
            # environment.
            if (move.company_id.tax_lock_date and move.date <= move.company_id.tax_lock_date) and (
                    move.line_ids.tax_ids or move.line_ids.tag_ids):
                move.date = move.company_id.tax_lock_date + timedelta(days=1)
                move.with_context(check_move_validity=False)._onchange_currency()

        # Create the analytic lines in batch is faster as it leads to less cache invalidation.
        self.mapped('line_ids').create_analytic_lines()
        for move in self:
            if move.auto_post and move.date > fields.Date.today():
                raise UserError(_("This move is configured to be auto-posted on {}".format(
                    move.date.strftime(self.env['res.lang']._lang_get(self.env.user.lang).date_format))))

            move.message_subscribe([p.id for p in [move.partner_id, move.commercial_partner_id] if
                                    p not in move.sudo().message_partner_ids])

            to_write = {'state': 'posted'}

            if move.name == '/':
                # Get the journal's sequence.
                sequence = move._get_sequence()
                if not sequence:
                    raise UserError(_('Please define a sequence on your journal.'))

                # Consume a new number.
                if move.type == 'out_invoice' or move.type == "out_refund":
                    to_write['invoice_doc_type'] = sequence.l10n_latam_document_type_id
                    to_write['invoice_doc_serie'] = \
                        sequence._get_prefix_suffix(date=move.invoice_date or fields.Date.today(),
                                                    date_range=move.invoice_date)[0][:-1]
                    to_write[
                        'invoice_doc_number'] = '%%0%sd' % sequence.padding % sequence._get_current_sequence().number_next_actual
                to_write['name'] = sequence.next_by_id(sequence_date=move.date)

            move.write(to_write)

            # Compute 'ref' for 'out_invoice'.
            if move.type == 'out_invoice' and not move.invoice_payment_ref:
                to_write = {
                    'invoice_payment_ref': move._get_invoice_computed_reference(),
                    'line_ids': []
                }
                for line in move.line_ids.filtered(
                        lambda line: line.account_id.user_type_id.type in ('receivable', 'payable')):
                    to_write['line_ids'].append((1, line.id, {'name': to_write['invoice_payment_ref']}))
                move.write(to_write)

            if move == move.company_id.account_opening_move_id and not move.company_id.account_bank_reconciliation_start:
                # For opening moves, we set the reconciliation date threshold
                # to the move's date if it wasn't already set (we don't want
                # to have to reconcile all the older payments -made before
                # installing Accounting- with bank statements)
                move.company_id.account_bank_reconciliation_start = move.date

    @api.constrains('invoice_doc_serie', 'invoice_doc_number')
    def _check_duplicate_supplier_reference(self):
        for invoice in self:
            # refuse to validate a vendor bill/credit note if there already exists one with the same reference for
            # the same partner, because it's probably a double encoding of the same bill/credit note only if the two
            # invoices are validated.
            self.ensure_one()
            if invoice.type in ('in_invoice', 'in_refund') and invoice.invoice_doc_number and invoice.invoice_doc_serie:
                res = self.env['account.move'].search([
                    ('type', '=', invoice.type),
                    ('invoice_doc_serie', '=', invoice.invoice_doc_serie),
                    ('invoice_doc_number', '=', invoice.invoice_doc_number),
                    ('company_id', '=', invoice.company_id.id),
                    ('partner_id', '=', invoice.partner_id.id),
                    ('invoice_doc_type', '=', invoice.invoice_doc_type.id),
                    ('id', '!=', invoice.id),
                    ('state', 'in', ('draft', 'posted'))])
                if res:
                    raise UserError(
                        "Se ha detectado una referencia duplicada para la factura de proveedor. "
                        "Es probable que tengas más de un documento con los mismos datos.")

    def invoice_validate(self):
        for invoice in self.filtered(lambda invoice: invoice.partner_id not in invoice.message_partner_ids):
            invoice.message_subscribe([invoice.partner_id.id])

            # Auto-compute reference, if not already existing and if configured on company
            # if not invoice.reference and invoice.type == 'out_invoice':
            invoice.ref = invoice._get_computed_reference()

            # DO NOT FORWARD-PORT.
            # The reference is copied after the move creation because we need the move to get the invoice number but
            # we need the invoice number to get the reference.
            if invoice.name:
                self.ref = invoice.name
            else:
                desc = ''
                if invoice.type == 'out_invoice':
                    desc = 'Venta a '
                if invoice.type == 'out_refund':
                    desc = 'Nota Credito a '
                if invoice.type == 'in_invoice':
                    desc = 'Compra a '
                if invoice.type == 'in_refund':
                    desc = 'Devolucion de '
                self.ref = desc + invoice.partner_id.legal_name + ' con documento ' \
                           + invoice.invoice_doc_type.name + ' ' + invoice.ref
        self._check_duplicate_supplier_reference()

        return self.write({'state': 'open'})

    def action_invoice_draft(self):
        if not self.env.user.has_group('account.group_account_user'):
            pass
        else:
            super(AccountMoveInherited, self).action_invoice_draft()


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    line_total = fields.Monetary(string='Importe', store=True, readonly=True, compute='_compute_price')
    # Necesario para Coversion segun tasa de cambio
    price_subtotal_signed_2 = fields.Monetary(string="Subtotal segun Tasa de Cambio", readonly=True)

    # Necesario para Coversion segun tasa de cambio

    @api.depends('price_unit', 'discount', 'quantity',
                 'product_id', 'move_id.partner_id', 'move_id.currency_id', 'move_id.company_id',
                 'move_id.invoice_date', 'move_id.date')
    def _compute_price(self):
        for rec in self:
            price = rec.price_unit * (1 - (rec.discount or 0.0) / 100.0)
            rec.line_total = price * rec.quantity

    def name_get(self):
        names = []
        for line in self:
            order = line.sale_line_ids.mapped('order_id')
            pickings = order.picking_ids.filtered(lambda x: x.state == 'done')
            series_list = [move_line.lot_id.name for pick in pickings
                           for move_line in pick.move_line_ids_without_package
                           if move_line.product_id == line.product_id and move_line.lot_id
                           ]
            names.append((line.id, '%s %s' % (line.name, series_list or '')))
        return names
