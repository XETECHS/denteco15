
import logging
from opcode import opname

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)

class SaleRoute(models.Model):
    _name = 'sale.route'
    _description = 'Sale Route'
    
    name = fields.Char('Name', required=True)


class SaleRouteTracking(models.Model):
    _name = 'sale.route.tracking'
    _description = 'Sale Route Tracking'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_begin'

    date_begin = fields.Datetime(string='Start Date', required=True, tracking=True)
    date_end = fields.Datetime(string='End Date', required=True, tracking=True)
    tracking_line_ids = fields.One2many('sale.route.tracking.line', 'tracking_id', string='Tracking Line')

    def get_invoices(self):
        self.ensure_one()
        account_move = self.env["account.move"]
        tracking_line = self.env["sale.route.tracking.line"]
        self.tracking_line_ids.unlink()
        lines = []
        
        invoice_id = account_move.search([
            ("move_type", "in", ["in_invoice", "out_invoice"]),
            ("invoice_date", ">=", self.date_begin.date()),
            ("invoice_date", "<=", self.date_end.date()),
        ])
        for invoice in invoice_id:
            line = tracking_line.create({"invoice_id": invoice.id})
            lines.append(line.id)
        self.write({"tracking_line_ids": [(6, 0, lines)]})

class SaleRouteTrackingLine(models.Model):
    _name = 'sale.route.tracking.line'
    _description = 'Sale Route Tracking Line'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name = "invoice_id"

    invoice_id = fields.Many2one('account.move', string='Invoice', required=True, index=True)
    invoice_date = fields.Date(string='Invoice/Bill Date', related="invoice_id.invoice_date")
    invoice_date_due = fields.Date(string='Due Date', related="invoice_id.invoice_date_due")
    partner_invoice_id = fields.Many2one('res.partner', string='Customer', related="invoice_id.partner_id")
    partner_street = fields.Char(string='Customer Street', related="invoice_id.partner_id.street")
    currency_id = fields.Many2one('res.currency', string='Currency', default= lambda s: s.env.company.currency_id)
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, related='invoice_id.amount_total')
    partner_id = fields.Many2one('res.partner', string='Partner')
    route_id = fields.Many2one('sale.route', string='Route')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('done', 'Done'),
        ('nc', 'Credit Note')
    ], string='status', default="pending")
    tracking_id = fields.Many2one('sale.route.tracking', string='tracking')
    signature = fields.Image('Signature', help='Signature received through the portal.', copy=False, attachment=True, max_width=1024, max_height=1024)
    signed_by = fields.Char('Signed By', help='Name of the person that signed the Tracking.', copy=False)
    signed_on = fields.Datetime('Signed On', help='Date of the signature.', copy=False)
    notes = fields.Text('Notes')
    tracking_invoices = fields.One2many('sale.route.tracking.invoice', 'line_id', string="Tracking Invoices", copy=False, store=True)
    is_partial = fields.Boolean(compute='_compute_is_partial', string='Is Partial', store=True)
    route_comission_id = fields.Many2one('sale.route.comission', string='Route Comission')

    @api.depends('tracking_invoices.status')
    def _compute_is_partial(self):
        for record in self:
            status_of_line = record.tracking_invoices.mapped("status")
            is_partial = any( [status=='partial' for status in status_of_line] )
            record.write({"is_partial": is_partial})

    def search_tracking_invoices(self):
        for record in self:
            record.tracking_invoices.unlink()
            invoice_lines = record.invoice_id.mapped("invoice_line_ids")
            lines = []
            for line in invoice_lines:
                lines.append(
                    (0, 0, {
                        "invoice_line_id": line.id
                    })
                )
            record.write({"tracking_invoices": lines})


    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.route_id = self.partner_id.tracking_route_id

    @api.constrains('invoice_id')
    def _check_description(self):
        if self.search_count([("invoice_id", "=", self.invoice_id.id)]) > 2:
            raise ValidationError(_("Invoice already has a tracking"))

    def _compute_access_url(self):
        super(SaleRouteTrackingLine, self)._compute_access_url()
        for traking in self:
            traking.access_url = '/tracking_route/%s' % (traking.id)

    def preview_tracking_web(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }

    def _get_portal_return_action(self):
        """ Return the action used to display tracking when returning from customer portal. """
        self.ensure_one()
        return self.env.ref('denteco_routes.sale_route_tracking_line_action')

    def action_confirm(self):
        return self.write({"status": "done"})

    @api.constrains('invoice_id')
    def _constrains_invoice_id(self):
        if self.search_count([("invoice_id", "=", self.invoice_id.id)]) > 1:
            raise UserError(_("%s invoice already has a tracking"%self.invoice_id.name))

class SaleRouteTrackingInvoice(models.Model):
    _name = 'sale.route.tracking.invoice'
    _description = 'Sale Route Tracking Invoice'
    _rec_name = "invoice_line_id"

    invoice_line_id = fields.Many2one('account.move.line', string='Invoice Line', required=True, readonly=True)
    quantity = fields.Float(string='Quantity', related="invoice_line_id.quantity")
    product_id = fields.Many2one('product.product', string='Product', related="invoice_line_id.product_id")
    status = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('partial', 'Partial')
    ], string='Status', default="draft")
    qty_done = fields.Float(string='Qty Done')
    line_id = fields.Many2one('sale.route.tracking.line', string='Line')
    
class SaleRouteComission(models.Model):
    _name = 'sale.route.comission'
    _description = 'Sale Route Comission'
    _order = 'date_begin'

    date_begin = fields.Datetime(string='Start Date', required=True)
    date_end = fields.Datetime(string='End Date', required=True)
    partner_id = fields.Many2one('res.partner', string='Partner')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda s: s.env.company.currency_id)
    comission_rate = fields.Many2one('sale.route.comission.rate', string='Commision Rate', readonly=True)
    tracking_line_ids = fields.One2many('sale.route.tracking.line', 'route_comission_id', string='Tracking Line')
    total_tracking_line = fields.Integer('Total Lines')
    amount_base = fields.Monetary(string="Amount Base", default=350)
    amount_rate = fields.Monetary(string="Amount Rate", compute='_compute_field_name')
    amount_total = fields.Monetary(string="Amount Total", compute='_compute_field_name')
    
    @api.depends('tracking_line_ids', 'comission_rate', 'amount_base')
    def _compute_field_name(self):
        for record in self:
            amount_rate = record.total_tracking_line * record.comission_rate.rate
            record.write({
                "amount_rate": amount_rate,
                "amount_total": amount_rate + record.amount_base
            })

    def get_tracking_lines(self):
        comission_rate = self.env["sale.route.comission.rate"].search([])
        tracking_line = self.env['sale.route.tracking.line']
        tracking_line_ids = tracking_line.search([
            ("partner_id", "=", self.partner_id.id),
            ("invoice_date", ">=", self.date_begin.date()),
            ("invoice_date", "<=", self.date_end.date()),
            ("status", "=", "done")
        ])
        lines = len( tracking_line_ids )
        comission_rate_id = comission_rate.filtered(lambda c: lines>=c.rate_from and lines<=c.rate_to)
        self.write({
            "tracking_line_ids": [(6, 0, tracking_line_ids.ids)],
            "comission_rate": comission_rate_id.id,
            "total_tracking_line": lines
        })


        
    

class SaleRouteComissionRate(models.Model):
    _name = 'sale.route.comission.rate'
    _description = 'Sale Route Comission Rate'

    name = fields.Char('Name', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda s: s.env.company.currency_id)
    rate_from  = fields.Integer('Rate from')
    rate_to  = fields.Integer('Rate to')
    rate = fields.Monetary('Rate', required=True)

    @api.constrains('rate_from', 'rate_to')
    def _constrains_rate_from_rate_to(self):
        if self.rate_from >= self.rate_to:
            raise UserError(_("Select a correct range"))





