# -*- coding: utf-8 -*-

from odoo import fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'
    display_street = fields.Char('Direccion Completa', compute='_compute_street_name')

    def _compute_street_name(self):
        for record in self:
            direccion = ''
            if record.street:
                direccion += record.street
            if record.street2:
                direccion += " " + record.street2
            record.display_street = direccion
