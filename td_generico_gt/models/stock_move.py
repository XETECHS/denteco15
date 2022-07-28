# -*- coding: utf-8 -*-

import logging

from odoo import fields, api, models, _
from odoo.exceptions import ValidationError


class StockMoveInherited(models.Model):
    _name = "stock.move"
    _inherit = "stock.move"

    @api.depends('product_id')
    def _compute_price_unit_move(self):
        for record in self:
            if record['product_id']:
                if record['picking_code'] == 'internal':
                    record['price_unit'] = record['product_id']['standard_price']
                else:
                    record['price_unit'] = super(StockMoveInherited, record)._get_price_unit()
            else:
                record['price_unit'] = 0.0

    price_unit = fields.Float(
        store=True,
        compute="_compute_price_unit_move"
    )
