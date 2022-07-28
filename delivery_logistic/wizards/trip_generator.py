# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class TripGenerator(models.TransientModel):
    _name = 'delivery_logistic.trip_generator'
    _description = "Generador de Viajes"

    route_id = fields.Many2one(
        comodel_name="delivery_logistic.route",
        ondelete="cascade",
        required=True,
        readonly=True,
        string="Ruta"
    )
    driver_id = fields.Many2one(
        comodel_name="res.partner",
        ondelete="cascade",
        domain=[('is_driver', '=', True)],
        string="Piloto"
    )
    vehicle_id = fields.Many2one(
        comodel_name="fleet.vehicle",
        ondelete="cascade",
        string="Vehículo"
    )
    initial_date = fields.Date(
        string="Fecha salida"
    )
    line_ids = fields.One2many(
        comodel_name="delivery_logistic.trip_generator_line",
        inverse_name="trip_generator_id",
        string="Líneas"
    )

    def create_trip(self):
        """Accion para confirmar la creacion de un viaje con sus lineas de entrega.
            Se evaluara inicialmente si tiene entregas, ya que no puede crearse un viaje sin entregas.
            Si la evauacion es verdadera, entonces se creara el viaje y se le asignará a cada entrega.
            """
        if self.line_ids:
            tree_view = self.env.ref('delivery_logistic.tree_view_delivery_trip')
            form_view = self.env.ref('delivery_logistic.form_view_delivery_trip')
            Trip = self.env['delivery_logistic.trip']
            picks = [line.picking_id.id for line in self.line_ids]
            values = {
                'route_id': self.route_id.id, 'driver_id': self.driver_id.id,
                'vehicle_id': self.vehicle_id.id, 'initial_date': self.initial_date,
                'sale_order_ids': [(6, 0, self.env.context.get('sale_ids'))], 'picking_ids': picks,
                'name': self.env['ir.sequence'].next_by_code('delivery_logistic.trip.sequence') or 'Nuevo'
            }
            Trip.create(values)
            return {
                'name': _('Viaje de entrega'),
                'view_mode': 'tree,form',
                'res_model': 'delivery_logistic.trip',
                'view_id': tree_view.id,
                'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
                'type': 'ir.actions.act_window'
            }
        else:
            raise ValidationError('No puede crear un viaje de entrega sin entregas. '
                                  'Seleccione entregas para proceder a crear el viaje que desea.')


class TripGeneratorlINE(models.TransientModel):
    _name = 'delivery_logistic.trip_generator_line'
    _description = "Línea de Generador de Viajes"

    trip_generator_id = fields.Many2one(
        comodel_name="delivery_logistic.trip_generator",
        ondelete="cascade",
        readonly=True,
        string="Generador de Viaje para entrega"
    )
    picking_id = fields.Many2one(
        comodel_name="stock.picking",
        ondelete="cascade",
        copy=False,
        readonly=True,
        string="Entrega"
    )
    name = fields.Char(
        related="picking_id.name",
        string="Referencia"
    )
    location_id = fields.Char(
        related="picking_id.location_id.name",
        string="Desde"
    )
    location_dest_id = fields.Char(
        related="picking_id.location_dest_id.name",
        string="Hasta"
    )
    partner_id = fields.Char(
        related="picking_id.partner_id.name",
        string="Contacto"
    )
    scheduled_date = fields.Datetime(
        related="picking_id.scheduled_date",
        string="Fecha"
    )
    origin = fields.Char(
        related="picking_id.origin",
        string="Documento origen"
    )
