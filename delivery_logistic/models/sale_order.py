# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderInherit(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    def _compute_can_edit_delivery_date(self):
        self.can_edit_delivery_date = self.env.user.has_group('delivery_logistic.group_delivery_logistic_manager')

    @api.depends('trip_ids')
    def _get_trip_status(self):
        """
        Computa el estado del viaje de una SO. Posibles estados:
        - new: if the SO is not in status 'sale' or 'done', we consider that there is nothing to
          invoice. This is also the default value if the conditions of no other status is met.
        - in_rute: if any SO line is 'to invoice', the whole SO is 'to invoice'
        - complete: if all SO lines are invoiced, the SO is invoiced.
        - final_incomplete: if all SO lines are invoiced or upselling, the status is upselling.
        - cancel: if all SO lines are invoiced or upselling, the status is upselling.
        """
        new_trip_orders = self.filtered(lambda so: so.trip_ids.filtered(lambda t: t.state == 'new'))
        new_trip_orders.write({'trip_status': 'new'})
        in_rute_trip_orders = self.filtered(lambda so: so.trip_ids.filtered(lambda t: t.state == 'in_rute'))
        in_rute_trip_orders.write({'trip_status': 'in_rute'})
        complete_trip_orders = self.filtered(lambda so: so.trip_ids.filtered(lambda t: t.state == 'complete'))
        complete_trip_orders.write({'trip_status': 'complete'})
        final_incomplete_trip_orders = self.filtered(lambda so: so.trip_ids.filtered(
            lambda t: t.state == 'final_incomplete'))
        final_incomplete_trip_orders.write({'trip_status': 'final_incomplete'})
        cancel_trip_orders = self.filtered(lambda so: so.trip_ids.filtered(lambda t: t.state == 'cancel'))
        cancel_trip_orders.write({'trip_status': 'cancel'})

    route_id = fields.Many2one(
        comodel_name="delivery_logistic.route",
        ondelete="cascade",
        copy=False,
        string="Ruta de entrega"
    )
    trip_ids = fields.Many2many(
        comodel_name="delivery_logistic.trip",
        relation="trip_sale_order_rel",
        column1="sale_order_id",
        column2="trip_id",
        ondelete="cascade",
        store=True,
        copy=False,
        readonly=True,
        string="Viaje(s) de entrega"
    )
    delivery_date = fields.Date(
        copy=False, required=True,
        string="Fecha de ruta"
    )
    can_edit_delivery_date = fields.Boolean(copy=False, compute='_compute_can_edit_delivery_date')
    trip_status = fields.Selection(
        selection=[
            ('new', 'Nuevo'), ('in_rute', 'En Ruta'), ('complete', 'Terminado Completo'),
            ('final_incomplete', 'Terminado Incompleto'), ('cancel', 'Cancelado')
        ], string='Estado del Viaje', compute='_get_trip_status',
        store=True, readonly=True
    )
    delivery_comment = fields.Text('Delivery Comment')

    @api.onchange('partner_shipping_id')
    def set_route(self):
        """Evalua si no existe metodo de envio ni ruta en el.
            Si la avaluacion es verdadera,
            obtener la ruta desde la direccion de entrega o bien un valor boleano False."""
        if not self.carrier_id and not self.carrier_id.route_id:
            route_id = self.partner_shipping_id.route_id.id \
                if self.partner_shipping_id and self.partner_shipping_id.route_id else False
            self.route_id = route_id

    def set_delivery_line(self, carrier, amount):
        """Herencia de metodo set_delivery_line del modulo delivery.
            Extension para obtener la ruta del metodo de entrega o de la direccion de entrega."""
        result = super(SaleOrderInherit, self).set_delivery_line(carrier, amount)
        route_id = carrier.route_id.id \
            if carrier and carrier.route_id else self.partner_shipping_id.route_id.id
        self.route_id = route_id or False
        return result

    """Falta definir como agregar el o los viajes"""
