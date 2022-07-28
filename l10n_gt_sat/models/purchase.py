# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.osv import expression
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang


class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    def _create_picking(self):
        tiene_dai = False
        StockPicking = self.env['stock.picking']
        for order in self:

            for exp_dai in order.order_line.product_id:
                if exp_dai.product_tmpl_id.dai_id:
                    if exp_dai.product_tmpl_id.dai_id.porcentaje > 0:
                        tiene_dai = True

            if any([ptype in ['product', 'consu'] for ptype in order.order_line.mapped('product_id.type')]):
                pickings = order.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
                if not pickings:
                    if tiene_dai:
                        res = order._prepare_picking()
                        picking = StockPicking.create(res)

                        res_dai = order._prepare_picking()
                        picking_dai = StockPicking.create(res_dai)
                    else:
                        res = order._prepare_picking()
                        picking = StockPicking.create(res)
                else:
                    picking = pickings[0]

                if tiene_dai:
                    moves = order.order_line._create_stock_moves_sin_dai(picking)#------------------------------------------------------
                    moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                    seq = 0
                    for move in sorted(moves, key=lambda move: move.date_expected):
                        seq += 5
                        move.sequence = seq
                    moves._action_assign()

                    moves_dai = order.order_line._create_stock_moves_con_dai(picking_dai)#------------------------------------------------------
                    moves_dai = moves_dai.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                    seq = 0
                    for move in sorted(moves_dai, key=lambda move: move.date_expected):
                        seq += 5
                        move.sequence = seq
                    moves_dai._action_assign()
                else:
                    moves = order.order_line._create_stock_moves(picking)#------------------------------------------------------
                    moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
                    seq = 0
                    for move in sorted(moves, key=lambda move: move.date_expected):
                        seq += 5
                        move.sequence = seq
                        moves._action_assign()
                picking.message_post_with_view('mail.message_origin_link',
                    values={'self': picking, 'origin': order},
                    subtype_id=self.env.ref('mail.mt_note').id)
        return True

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _create_stock_moves(self, picking):
        #print("-------------------------------------------------------------Llego al piking")
        #print(picking)
        values = []
        for line in self.filtered(lambda l: not l.display_type):
            for val in line._prepare_stock_moves(picking):
                values.append(val)
        return self.env['stock.move'].create(values)

    def _create_stock_moves_sin_dai(self, picking):
        #print("-------------------------------------------------------------Llego al piking sin dai")
        #print(picking)
        values = []
        for line in self.filtered(lambda l: not l.display_type and (not l.product_id.product_tmpl_id.dai_id or l.product_id.product_tmpl_id.dai_id.porcentaje == 0)):
            for val in line._prepare_stock_moves(picking):
                values.append(val)
        return self.env['stock.move'].create(values)

    def _create_stock_moves_con_dai(self, picking):
        #print("-------------------------------------------------------------Llego al piking con dai")
        #print(picking)
        values = []
        for line in self.filtered(lambda l: not l.display_type and l.product_id.product_tmpl_id.dai_id and l.product_id.product_tmpl_id.dai_id.porcentaje > 0):
            for val in line._prepare_stock_moves(picking):
                values.append(val)
        return self.env['stock.move'].create(values)
