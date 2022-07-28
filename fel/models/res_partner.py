# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
class res_partner(models.Model):
    _inherit = 'res.partner'

    cui = fields.Char(string="CUI")
    display_street = fields.Char('Direccion Completa', compute='_compute_street_name')

    def _compute_street_name(self):
        for record in self:
            direccion = ''
            if record.street:
                direccion += record.street
            if record.street2:
                direccion += " " + record.street2
            if record.state_id:
                direccion += " " + record.state_id.name
            if direccion == '':
                direccion = "Ciudad"
            record.display_street = direccion
