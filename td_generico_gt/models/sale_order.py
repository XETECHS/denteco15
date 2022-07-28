# -*- coding: utf-8 -*-

from odoo import fields, api, models


class SaleOrderInherit(models.Model):
    _name = "sale.order"
    _inherit = "sale.order"

    nit = fields.Char(related="partner_id.vat", string="NIT")
    legal_name = fields.Char(related="partner_id.legal_name", string="Razón Social")
