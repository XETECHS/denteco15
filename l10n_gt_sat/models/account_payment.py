# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang, format_date
from odoo.addons.l10n_gt_sat.models import letras

from . import letras

class AccountPayment(models.Model):
    _inherit = "account.payment"

    check_no_negociable = fields.Boolean(string="No Negociable", default=False, tracking=True, readonly=True, states={'draft': [('readonly', False)]},)

    #@api.onchange('amount', 'currency_id')
    #def _onchange_amount(self):

        #res = super(AccountPayment, self)._onchange_amount()

    #    enletras = letras
    #    cantidadenletras = enletras.to_word(self.amount)
    #    if self.currency_id.name == 'USD':
    #        cantidadenletras = cantidadenletras.replace('QUETZALES','DOLARES')
    #    elif self.currency_id.name == 'EUR':
    #        cantidadenletras = cantidadenletras.resultado('QUETZALES','EUROS')
    #    self.check_amount_in_words = cantidadenletras
        #return
    def numeros_a_letras(self, numero):
        return letras.to_word(numero)

    def _check_fill_line(self, amount_str):
            return amount_str and (amount_str + ' ').ljust(65, '*') or ''

    def check_sent(self):
        for payment in self:
            if payment.state == 'posted':
                payment.write({'state':'posted'})

    def do_print_checks(self):
        for payment in self:
            if payment.state == 'posted':
                payment.write({'state':'posted'})
        papel = self.journal_id.papel_cheque
        return self.env.ref(papel).report_action(self)
