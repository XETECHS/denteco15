# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartnerInherit(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    route_id = fields.Many2one(
        comodel_name="delivery_logistic.route",
        ondelete="cascade",
        copy=False,
        string="Ruta de entrega"
    )
    is_driver = fields.Boolean(
        default=False,
        copy=False,
        string="Es piloto"
    )

    @api.onchange('is_driver')
    def unlink_route(self):
        """Evalua si el contacto es un piloto.
            De resultar verdadera la evaluacion, a la ruta se le coloca el valor boleano False."""
        if self.is_driver:
            self.route_id = False
