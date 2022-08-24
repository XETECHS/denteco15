# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    country_id = fields.Many2one(default=lambda s: s.env.ref('base.gt'))

    

    