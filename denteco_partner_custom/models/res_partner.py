# -*- coding: utf-8 -*-
from datetime import date, timedelta
import logging

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class ResPartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    category_from  = fields.Float('Category from')
    category_to  = fields.Float('Category to')

    @api.constrains('category_from', 'category_to')
    def _constrains_category_from_category_to(self):
        if self.category_from >= self.category_to:
            raise UserError(_("Select a correct range"))

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    client_type_id = fields.Many2one('res.partner.client.type', string='Client Type')
    specialties_id = fields.Many2one('res.partner.specialties', string='Specialties')
    billing_type = fields.Selection([
        ('customer', 'Customer'),
        ('supplier', 'Supplier'),
        ('user', 'User')
    ], string='Billing Type')
    seller_code = fields.Char('Seller Code')
    category_id = fields.Many2many(compute='_compute_category_id', store=True)
    sold_annual = fields.Monetary( string='Sold Annual')
    
    @api.depends('sold_annual')
    def _compute_category_id(self):
        category = self.env["res.partner.category"].search([])
        for record in self:
            category_id = category.filtered(lambda c: record.sold_annual>=c.category_from and record.sold_annual<=c.category_to)
            record.write({"category_id": [(6, 0, category_id.ids)]})

    def update_historical_billing(self):
        today = date.today()
        year_ago = today - timedelta(days=365)
        SQL = """
            SELECT SUM(aml.price_total)
            FROM account_move_line aml
            WHERE aml.exclude_from_invoice_tab=False AND NOT aml.is_equipment
            AND aml.partner_id=%s AND aml.date BETWEEN %s AND %s;
        """
        for record in self:
            self.env.cr.execute(SQL, [self.id, year_ago, today])
            sold_annual = self.env.cr.fetchall()[0][0]
            record.write({
                "sold_annual": sold_annual
            })
    
    def _cron_update_historical_billing(self):
        partners = self
        if not partners:
            partners = self.search([])
        for partner in partners:
            partner.update_historical_billing()
            self.env.cr.commit()


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    channel_id = fields.Many2one('account.analytic.account', string='Canal')


class ResPartnerClientType(models.Model):
    _name = 'res.partner.client.type'
    _description = 'Client Type'
    
    name = fields.Char(string="Name", required=True)

class ResPartnerSpecialties(models.Model):
    _name = 'res.partner.specialties'
    _description = 'Partner Specialties'

    name = fields.Char(string="Name", required=True)
