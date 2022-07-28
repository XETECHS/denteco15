# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from datetime import timedelta
from functools import partial

import psycopg2
import pytz
import re

from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero, float_round, float_repr, float_compare
from odoo.exceptions import ValidationError, UserError
from odoo.http import request
from odoo.osv.expression import AND
import base64

_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = "pos.order"
    
    # ==== Reverse feature fields ====
    reversed_entry_id = fields.Many2one('pos.order', string="Reversal of", readonly=True, copy=False,
        check_company=True)
    reversal_move_id = fields.One2many('pos.order', 'reversed_entry_id')

    ####################################################################
    # La funcion action_pos_order_invoice ya no se utiliza en odoo15
    # Ahora se utiliza la funcion _generate_pos_order_invoice
    ####################################################################

    # def action_pos_order_invoice(self):
    #     action = super(PosOrder,self).action_pos_order_invoice()
    #     move = self.env['account.move'].search([('id','=',action['res_id'])])
    #     if move.journal_id.fel_setting_id:
    #         documento = move.getListFactura()
    #         move.firmar_factura(documento, False, False)
    #     return action

    def _generate_pos_order_invoice(self):
        action = super(PosOrder,self)._generate_pos_order_invoice()
        move = self.env['account.move'].search([('id','=',action['res_id'])])
        if move.journal_id.fel_setting_id:
            documento = move.getListFactura()
            move.firmar_factura(documento, False, False)
        return action
    
    def _prepare_invoice_vals(self):
        rst = super(PosOrder, self)._prepare_invoice_vals()                
        if  self.amount_total < 0:
            factura = None
            for pedido_origen_id in self.refunded_order_ids.ids:
                pedido_origen = self.browse(pedido_origen_id)
                factura = pedido_origen.account_move.id
            rst.update({'journal_id': self.session_id.config_id.refund_journal_id.id})
            rst.update({'reversed_entry_id': factura})
            rst.update({'fel_motivo': 'ANULACION'})
        return rst