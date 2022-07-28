from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    municipio_id = fields.Many2one('res.state.municipio', string='Municipio')
    zona = fields.Char(string='Zona')

    @api.onchange('municipio_id')
    def _onchange_municipio_id(self):
        if self.municipio_id:
            self.state_id = self.municipio_id.state_id.id
            self.country_id = self.state_id.country_id.id