# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    #seller_code = fields.Char('Seller Code', related="user_id.seller_code")
    
    @api.onchange("user_id")
    def _onchange_user_id(self):
        for order in self:
            order.analytic_account_id = order.user_id.channel_id
