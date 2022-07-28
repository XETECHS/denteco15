# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round


class ReturnPickingInherited(models.TransientModel):
    _name = 'stock.return.picking'
    _inherit = 'stock.return.picking'

    def _create_returns(self):
        """Extension de metodo generico de odoo para devoluciones de transferencias de inventario.
            Extension realizada para poder agregar valores necesarios en modulo delivery_logistic
            valores necesarios:
                'route_id': self.picking_id.route_id.id or False,
                'source_picking_id': self.picking_id.id,
                self.picking_id.write({'return_picking_ids': [new_picking.id]})
                self.picking_id.trip_id.write({'return_picking_ids': [new_picking.id]})
                """
        new_picking_id, picking_type_id = super(ReturnPickingInherited, self)._create_returns()
        new_picking = self.env['stock.picking'].browse([new_picking_id])
        new_picking.write({
            'route_id': self.picking_id.route_id.id or False,
            'source_picking_id': self.picking_id.id
        })
        if not new_picking.is_return_picking:
            new_picking._compute_return_picking()
        if self.picking_id.trip_id:
            return_picks = [new_picking.id]
            self.picking_id.trip_id.write({
                'return_picking_ids': return_picks + list(self.picking_id.trip_id.return_picking_ids.ids)
                if self.picking_id.trip_id.return_picking_ids
                else return_picks
            })
        """"-----Fin de la extension------"""
        return new_picking_id, picking_type_id
