# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PaymentRegisterInherited(models.TransientModel):
    _inherit = 'account.payment.register'

    communication = fields.Char(
        string='Circular',
        help='Ingrese la circular que desea para los pago(s) que serán registrado(s).'
    )
    text_free = fields.Char(
        string='Nota',
        help='Ingrese la nota que desea para los pago(s) que serán registrado(s).'
    )

    def _prepare_payment_vals(self, invoices):
        res = super(PaymentRegisterInherited, self)._prepare_payment_vals(invoices)
        res['communication'] = self.communication
        res['text_free'] = self.text_free
        return res
