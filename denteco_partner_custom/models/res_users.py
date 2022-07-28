# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    channel_id = fields.Many2one('account.analytic.account', string='Canal')
