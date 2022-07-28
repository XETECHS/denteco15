# -*- coding: utf-8 -*-

from collections import Counter

from odoo import api, fields, models, tools, _


class StockMoveLine(models.Model):
    _name = "stock.move.line"
    _inherit = "stock.move.line"

    lot_id = fields.Many2one(
        comodel_name='stock.production.lot', string='Número Lote/Serie',
        domain="[('product_id', '=', product_id), ('company_id', '=', company_id), ('unavailable', '=', False)]",
        check_company=True
    )
