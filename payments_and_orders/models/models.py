# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountPaymentInherited(models.Model):
    _inherit = 'account.payment'
    _description = 'Pagos a Facturas/Pedidos'

    @api.depends('order_ids')
    def _compute_order_count(self):
        for record in self:
            record.order_count = len(record.order_ids)

    order_ids = fields.Many2many(
        'sale.order',
        'sale_order_payment_rel',
        'account_payment_id',
        'sale_order__id',
        string='Pedidos',
        ondelete='cascade'
    )
    order_count = fields.Integer(
        compute='_compute_order_count',
        string="Contar pedidos"
    )

    def action_orders(self):
        return {
            'name': f'Pedidos relacionados a {self.name}',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'view_id': False,
            'views': [(self.env.ref('sale.view_quotation_tree').id, 'tree'),
                      (self.env.ref('sale.view_order_form').id, 'form')],
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', [o.id for o in self.order_ids])],
            'context': {'create': False},
        }

    def post(self):
        res = super(AccountPaymentInherited, self).post()
        active_model = self._context.get('active_model', False)
        print(self._context, 'CONTEXT')
        if res and active_model == 'sale.order':
            order_id = self._context['active_id']
            self.env.cr.execute(
                f'INSERT INTO sale_order_payment_rel (account_payment_id, sale_order__id)'
                f'VALUES ({self.id}, {order_id})'
            )
        return res


class SaleOrderInherited(models.Model):
    _inherit = 'sale.order'
    _description = 'Pedidos y sus pagos'

    @api.depends('payment_ids')
    def _compute_payment_count(self):
        for record in self:
            record.payment_count = len(record.payment_ids)

    payment_ids = fields.Many2many(
        'account.payment',
        'sale_order_payment_rel',
        'sale_order__id',
        'account_payment_id',
        string='Pagos',
        ondelete='cascade'
    )
    payment_count = fields.Integer(
        compute='_compute_payment_count',
        string="Contar pagos"
    )

    def action_receive_payment(self):
        default_type = self._context.get('default_type', False)
        if default_type not in ['in_invoice', 'in_refund']:
            return self.env['account.payment'] \
                .with_context(active_ids=self.ids, active_model='sale.order', active_id=self.id,
                              default_payment_type='inbound', default_partner_type='customer',
                              default_partner_id=self.partner_id.id) \
                .action_register_payment()

    def action_payments(self):
        return {
            'name': f'Pagos de {self.name}',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'view_id': False,
            'views': [(self.env.ref('account.view_account_payment_tree').id, 'tree'),
                      (self.env.ref('account.view_account_payment_form').id, 'form')],
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', [p.id for p in self.payment_ids])],
            'context': {'create': False},
        }
