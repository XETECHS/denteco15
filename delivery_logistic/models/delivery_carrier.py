# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DeliveryCarrierInherit(models.Model):
    _name = 'delivery.carrier'
    _inherit = 'delivery.carrier'

    route_id = fields.Many2one(
        comodel_name="delivery_logistic.route",
        ondelete="cascade",
        copy=False,
        string="Ruta de entrega"
    )
