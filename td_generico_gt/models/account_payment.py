# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
from odoo.exceptions import ValidationError
from odoo.tools import config


class AccountPaymentInherited(models.Model):
    _inherit = "account.payment"

    reference = fields.Char("Referencia")

    method = fields.Selection(
        [
            ("E", "Efectivo"),
            ("C", "Cheque"),
            ("T", "Transferencia"),
            ("TC", "Tarjeta de Credito"),
            ("DE", "Deposito"),
        ],
        string="Forma de Pago"
    )
    """Campo para ingresar referencia de banco en transferencias de pagos. 
           Campo único, no pueden haber más de un registro con los mismos datos."""
    bank_reference = fields.Char(
        copy=False,
        help="Campo para ingresar referencia de banco en transferencias de pagos. "
             "Campo único, no pueden haber más de un registro con los mismos datos.",
        string="Referencia de banco"
    )
    """Campo para ingresar cuenta contable personalizada de destino. 
        Si no existe valor en el campo, seguirá el curso normal de odoo"""
    custom_destination_account_id = fields.Many2one(
        comodel_name='account.account',
        ondelete="cascade",
        domain="[('is_custom_payment_account', '=', True)]",
        index=True,
        help="Campo útil para ingresar cuenta contable personalizada de destino. "
             "Si no existe valor en el campo, seguirá el curso normal de odoo",
        string="Cuenta contable de destino"
    )

    @api.depends('invoice_ids', 'payment_type', 'partner_type', 'partner_id')
    def _compute_destination_account_id(self):
        for record in self:
            if record.custom_destination_account_id:
                record.destination_account_id = record.custom_destination_account_id.id
            else:
                super(AccountPaymentInherited, record)._compute_destination_account_id()

    _sql_constraints = [
        ('bank_reference_unique', 'UNIQUE(bank_reference)', 'La referencia de banco ingresada ya existe!')
    ]

    """Actualizacion 22/03/2021 para agregar numero de cheque a nombre de pago"""
    def name_get(self):
        names = []
        for record in self:
            names.append(
                (record.id, '%s %s' % (record.name, '- ' + str(record.check_number) if record.check_number else ''))
            )
        return names
    """Actualizacion 22/03/2021 para agregar numero de cheque a nombre de pago"""
