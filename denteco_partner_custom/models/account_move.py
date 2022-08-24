# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, tools, _

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    #seller_code = fields.Char('Seller Code', related="user_id.seller_code")

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_equipment = fields.Boolean("Equipment", compute='_compute_is_equipment', store=True)
    
    @api.depends('product_id.categ_id')
    def _compute_is_equipment(self):
        for record in self:
            record.write({
                "is_equipment": False
            })
            equipment = self.env.ref("denteco_partner_custom.equipment_denteco")
            if record.product_id.categ_id == equipment:
                record.write({
                    "is_equipment": True
                })
                continue
            parent_categ = record.product_id.categ_id.parent_id
            while parent_categ:
                if parent_categ == equipment:
                    record.write({
                        "is_equipment": True
                    })
                parent_categ = parent_categ.parent_id




