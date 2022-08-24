# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# class ProductProduct(models.Model):
#     _inherit = 'product.product'

#     is_equipment = fields.Boolean("Equipment")

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_equipment = fields.Boolean("Equipment")

    