# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class StockPickingInherit(models.Model):
    _name = 'stock.picking'
    _inherit = 'stock.picking'

    @api.depends('carrier_id', 'move_ids_without_package')
    def _compute_return_picking(self):
        """Extension de metodo _compute_return_picking presente en modulo delivery
            Fue necesario eliminar del metodo las siguiente seccion
                if picking.carrier_id and picking.carrier_id.can_generate_return:
            Ya que el campo can_generate_return del modelo delivery.carrier nunca era verdadero segun core de odoo.
            Y esto impedia que el campo is_return_picking fuera colocado como verdadero
            cuando existian devoluciones de transferencias de inventario."""
        for picking in self:
            picking.is_return_picking = any(m.origin_returned_move_id for m in picking.move_ids_without_package)

    @api.depends('carrier_id')
    def _compute_is_delivery(self):
        """Método computado en dependencia del campo carrier_id.
            Necesario para evaluar si una transferencia de inventario es para entrega a domicilio o no,
            en dependencia de si tiene metodo de envio agregado o no y si hibiera, este tenga una ruta ingresada."""
        for picking in self:
            picking.is_delivery = bool(picking.carrier_id.route_id) if picking.carrier_id else False

    carrier_id = fields.Many2one(
        comodel_name="delivery.carrier",
        ondelete="cascade",
        related="sale_id.carrier_id",
        store=True,
        check_company=True,
        copy=False,
        readonly=True,
        string="Método de envío"
    )
    route_id = fields.Many2one(
        comodel_name="delivery_logistic.route",
        ondelete="cascade",
        related="sale_id.route_id",
        store=True,
        readonly=True,
        copy=False,
        string="Ruta"
    )
    trip_id = fields.Many2one(
        comodel_name="delivery_logistic.trip",
        ondelete="cascade",
        readonly=True,
        copy=False,
        string="Viaje de entrega"
    )
    is_delivery = fields.Boolean(
        default=False,
        copy=False,
        store=True,
        compute="_compute_is_delivery",
        string="A domicilio"
    )
    reschedule = fields.Boolean(
        default=False,
        copy=False,
        string="Entrega por reprogramar"
    )
    is_return_picking = fields.Boolean(
        default=False,
        copy=False,
        store=True,
        compute='_compute_return_picking',
        string="Es albarán de devolución"
    )
    delete_delivery = fields.Boolean(
        default=False,
        copy=False,
        string="Quitar.",
        help="Quitar entrega del viaje al que ha sido asignada.."
    )
    source_picking_id = fields.Many2one(
        comodel_name="stock.picking",
        store=True,
        copy=False,
        string="Albarán origen"
    )
    return_picking_ids = fields.One2many(
        comodel_name="stock.picking",
        inverse_name="source_picking_id",
        store=True,
        copy=False,
        string="Retornos"
    )
    delivery_date = fields.Date(
        copy=False,
        related="sale_id.delivery_date",
        store=True,
        string="Fecha de ruta"
    )

    # @api.model
    # def create(self, vals):
    #     """Herencia de creacion de una transferencia de inventario.
    #         Extension para evaluar si una transferencia de inventario es para entrega a domicilio o no,
    #         en dependencia de si tiene metodo de envio agregado o no."""
    #     carrier = self.env['delivery.carrier'].browse(vals.get('carrier_id'))
    #     vals.update({'is_delivery': bool(carrier.route_id)} if carrier else {'is_delivery': False})
    #     return super(StockPickingInherit, self).create(vals)

    def get_pickings(self):
        """Filtro para obtener las entregas validas y disponibles para ser agregadas a un nuevo viaje.
            Si las entregas estan marcadas para domicilio y no tienen viaje enlazado,
            unido que hayan sido validadas como hechas, estaran disponibles para ser tomadas para un nuevo viaje."""
        picks = self.filtered(lambda pick: pick.is_delivery and pick.delivery_date and not pick.trip_id).\
            filtered(lambda p: p.route_id and p.carrier_id)
        if picks:
            picks = picks.filtered(lambda pick: pick.state == 'done')
            if picks:
                routes = [record.route_id for record in picks]
                if all(pick.route_id == routes[0] for pick in picks):
                    route_id = routes[0].id
                else:
                    raise ValidationError('Las entregas no tienen la misma ruta. '
                                          'Por favor asegurese que sean de la misma ruta '
                                          'para crear un viaje de entrega.')
                delivery_dates = [record.delivery_date for record in picks]
                if all(pick.delivery_date == delivery_dates[0] for pick in picks):
                    date = delivery_dates[0]
                else:
                    raise ValidationError('Las entregas no tienen la misma fecha de entrega. '
                                          'Por favor asegurese que sean para entregar la misma fecha '
                                          'y de esa manera crear un viaje de entrega.')
                result = {'picking_ids': picks.ids, 'route_id': route_id, 'initial_date': date,
                          'sale_ids': [pick.sale_id.id for pick in picks if pick.sale_id]}
                return result
            else:
                raise ValidationError(
                    'Debe seleccionar únicamente entregas en estado Hecho, '
                    'de lo contrario no podrá generar un viaje de entrega.'
                )
        else:
            raise ValidationError(
                'Todas las entregas seleccionados deben ser designadas para hacer uso de envío a '
                'domicilio, no tener ya un Viaje enlazado, tener ingresada la misma ruta y metodo de envio. '
                'Por favor verifique sus entregas, '
                'ya que no todas cumplen con alguno de los requerimientos mencionados.'
            )

    def action_trip_generator(self):
        """Accion para generar lista temporal de entregas a realizar para un viaje.
            Abre un wizard para confirmar las entregas adheridas."""
        result = self.get_pickings()
        view = self.env.ref('delivery_logistic.wizard_trip_generator_form_view')

        lines = []
        for pick in result.get('picking_ids'):
            line = (0, 0, {'picking_id': pick})
            lines.append(line)

        vals = ({'route_id': result.get('route_id'), 'initial_date': result.get('initial_date'), 'line_ids': lines})
        trip_generator_obj = self.env['delivery_logistic.trip_generator']
        trip_generator = trip_generator_obj.create(vals)

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': trip_generator.id,
            'res_model': 'delivery_logistic.trip_generator',
            'view_id': view.id,
            'views': [(view.id, 'form')],
            'target': 'new',
            'context': {'sale_ids': result.get('sale_ids')}
        }

    def action_add_delivery(self):
        """Accion para aplicar la(s) entrega(s) al viaje activo.
             Redirige al viaje con las entregas agregadas."""
        view = self.env.ref('delivery_logistic.form_view_delivery_trip')
        trip = self.env[self.env.context.get('active_model')].browse(self.env.context.get('active_id'))
        pick_ids = [pick_id for pick_id in self.ids] + [pick for pick in trip.picking_ids.ids]
        sale_order_ids = [pick.sale_id.id for pick in self if pick.sale_id]
        trip.write({
            'sale_order_ids': [(6, 0, sale_order_ids)], 'picking_ids': pick_ids
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'delivery_logistic.trip',
            'res_id': trip.id,
            'view_id': view.id,
            'views': [(view.id, 'form')],
            'target': 'current'
        }

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        """Extension de message_post para poder enviar notificaciones chatter en las transferencias de inventario."""
        return super(StockPickingInherit, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)
