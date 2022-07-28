# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def get_picking(self):
        for rec in self:
            if rec.picking_ids:
                picking = rec.picking_ids.filtered(lambda x: x.state in ('confirmed', 'assigned', 'waiting'))
                if picking:
                    picking.sorted(key=lambda x: x.id)
                    return picking[0]
    