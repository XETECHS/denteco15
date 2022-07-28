# -*- coding: utf-8 -*-

from odoo import models, api, fields


class ResPartnerBankInherited(models.Model):
    _inherit = 'res.partner.bank'

    @api.model
    def name_get(self):
        result = []
        for record in self:
            bank = (record.bank_id.name or '')
            account = (record.acc_number or '')
            name = bank + ' - ' + account
            result.append((record.id, name))
        return result


class AccountJournalInherited(models.Model):
    _inherit = 'account.journal'

    account_check_printing_layout = fields.Selection([('action_print_check_voucher', 'Formato'),
            ('action_print_check_format', 'Predeterminado'),
        ],
        string="Formato Cheque", required=True,
        help="Seleccione el formato que desea utilizar para imprimir sus cheques."\
             "Para deshabilitar la funci�n, seleccione 'Ninguno'.",
        default="action_print_check_format"
    )
    cheque_formate_id = fields.Many2one('cheque.setting', string='Reporte Cheque')


class AccountPaymentInherited(models.Model):
    _inherit = "account.payment"

    @api.model
    @api.depends('journal_id')
    def _get_check_formate(self):
        return self.journal_id.cheque_formate_id.id

    document_reference = fields.Char(compute='_get_document_reference', string="Referencia", store=True)
    cheque_formate_id = fields.Many2one('cheque.setting', string='Reporte Cheque', default=_get_check_formate)
    name_to = fields.Char(string="A nombre de", tracking=True)
    # cheque_no = fields.Char('Cheque No')
    text_free = fields.Char(string='Descripción')

    # partner_text = fields.Char('Partner Title')

    @api.onchange("partner_id")
    def compute_name_to(self):
        if self.partner_id:
            self.name_to = self.partner_id.legal_name

    @api.onchange('payment_method_id')
    def _payment_method_change(self):
        if self.payment_method_id.code == 'TRA':
            self.show_partner_bank_account = True

    @api.depends('check_number')
    def _get_document_reference(self):
        for record in self:
            record.document_reference = record.check_number

    @api.model
    def do_print_checks(self):
        print('imprimir')
        self.cheque_formate_id = self._get_check_formate()
        print(self.cheque_formate_id, 'FORMATO DENTRO DE PAGOS')
        if self:
            if self.journal_id.account_check_printing_layout:
                # Si no hay definido formato en el journal, buscar el predeterminado para la empresa
                check_layout = self.journal_id.account_check_printing_layout
            else:
                check_layout = self[0].company_id.account_check_printing_layout
            print(check_layout, 'LAYOUT OBTENIDO DENTRO DE PAGOS')
            if check_layout and self[0].journal_id.company_id.country_id.code == 'GT':
                self.write({'state': 'sent'})
                if self.journal_id.account_check_printing_layout == 'action_print_check_voucher':
                    return self.env.ref('l10n_gt_check_printing.action_print_check_voucher').report_action(self)
                else:
                    return self.env.ref('l10n_gt_check_printing.action_print_check_format').report_action(self)
                # return self.env.ref('l10n_gt_check_printing.%s' % check_layout).report_action(self)
                # #este es el external id del reporte.
        return super(AccountPaymentInherited, self).do_print_checks()
