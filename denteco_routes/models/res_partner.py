
import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'
    _description = 'Res Partner'
    
    tracking_route_id = fields.Many2one('sale.route', string='Route')