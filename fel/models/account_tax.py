# -*- coding: utf-8 -*-
from odoo import fields,models, api, _
from odoo.exceptions import UserError

class account_tax(models.Model):

    _inherit = "account.tax"

    @api.model
    def _get_default_unidad_grabable(self):
        unidad = self.env['fel.unidadgravable'].search([], limit=1)
        return unidad

    fel_unidad_gravable = fields.Many2one('fel.unidadgravable', string='Unidad Gravable', help="Catalogo de Unidades Gravables para el IVA.", default=_get_default_unidad_grabable)
