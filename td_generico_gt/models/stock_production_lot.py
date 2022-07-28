# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductionLot(models.Model):
    _name = 'stock.production.lot'
    _inherit = 'stock.production.lot'

    @api.depends('product_id', 'sale_order_count')
    def _compute_available(self):
        """ Computación de disponibilidad de series de inventario.
            Si es un producto con seguimiento por series unicas;
            se evaluará si tiene ventas en las que se usó dicha serie,
            para proceder a deshabilitar dicha serie. Caso contrario, estará disponible."""
        for record in self:
            if record.product_id:
                if record.product_id.tracking == 'serial' and record.sale_order_count > 0:
                    record.write({'unavailable': True})
                else:
                    record.write({'unavailable': False})
            else:
                record.write({'unavailable': True})

    unavailable = fields.Boolean(copy=False, store=True, compute='_compute_available', string="No está disponible")
