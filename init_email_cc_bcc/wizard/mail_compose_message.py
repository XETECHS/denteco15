# -*- coding: utf-8 -*-
from odoo import _, fields, models


class MailComposer(models.TransientModel):
    _inherit = "mail.compose.message"

    cc_ids = fields.Many2many(
        'res.partner', 'mail_compose_message_res_partner_cc_rel',
        'wizard_id', 'partner_id', 'CC Contacts')

    bcc_ids = fields.Many2many(
        'res.partner', 'mail_compose_message_res_partner_bcc_rel',
        'wizard_id', 'partner_id', 'BCC Contacts')

    def get_mail_values(self, res_ids):

        cc_emails = map(lambda p: p.email, self.cc_ids)
        bcc_emails = map(lambda p: p.email, self.bcc_ids)

        result = super(MailComposer, self).get_mail_values(res_ids)
        for id in result.keys():
            result[id]["email_cc"] = ",".join(cc_emails)
            result[id]["email_bcc"] = ",".join(bcc_emails)

        return result
