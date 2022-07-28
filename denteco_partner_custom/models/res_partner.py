# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    client_type_id = fields.Many2one('client.type', string='Tipo de Cliente')
    

class ResPartner(models.Model):
    _inherit = 'res.users'
    
    channel_id = fields.Many2one('account.analytic.account', string='Canal')


class ClientType(models.Model):
    _name = 'client.type'
    _description = 'Client Type'
    
    name = fields.Char(string="Nombre")
