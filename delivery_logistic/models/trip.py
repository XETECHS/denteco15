# -*- coding: utf-8 -*-

import base64

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Trip(models.Model):
    _name = 'delivery_logistic.trip'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Viaje de entregas'

    def _evaluate_returns_trip(self):
        """Evaluacion de las devoluciones en un viaje.
            Si el viaje en cuestion tiene devoluciones, se procede a revisar:
                Si se ha hecho una devolucion completa o parcial de los productos a entregar.
                    Si es una devolucion completa,
                        se retorna el valor False, para indicar que debe ser cancelado el viaje.
                Caso contrario se devuelve el valor True, para continuar con el proceso normal del viaje."""
        self.ensure_one()
        if self.has_returns:
            moves = self.mapped('picking_ids').mapped('move_ids_without_package')
            return_qtys = {move: 0 for move in moves}
            for move in moves.filtered(lambda m: m.returned_move_ids):
                for return_move in move.returned_move_ids.filtered(lambda r_move: r_move.state == 'done'):
                    return_qtys[move] += return_move.product_qty
            comparative_qty_return_moves = [move.product_qty == return_qty for move, return_qty in return_qtys.items()]
            if len(moves) == len(moves.filtered(lambda m: m.returned_move_ids)) and all(comparative_qty_return_moves):
                return False
            else:
                return True
        else:
            return True

    @api.depends('return_picking_ids')
    def _compute_has_returns(self):
        """Computacion que tiene como fin evaluar si existen devoluciones no canceladas de las posibles entregas.
                Unido a eso, se llamara al metodo _evaluate_returns_trip
                para saber si el viaje debe ser cancelado,
                en dependencia si existen aun cantidades por entregar, luego de la(s) devolucion(es)."""
        for record in self:
            if record.return_picking_ids:
                record.write({
                    'has_returns': False
                    if all([pick.state == 'cancel' for pick in record.return_picking_ids]) else True
                })
                evaluation = record._evaluate_returns_trip()
                if not evaluation:
                    record.write({'has_full_returns': True})
            else:
                record.write({'has_returns': False})

    def _compute_can_edit_dates(self):
        """Computacion para evaluar si el usuario que use la vista de este modelo,
            tiene permisos administrativos para poder editar o modificar valores de fechas."""
        self.can_edit_dates = self.env.user.has_group('delivery_logistic.group_delivery_logistic_manager')

    name = fields.Char(
        copy=False,
        index=True,
        store=True,
        string="Referencia"
    )
    state = fields.Selection(
        selection=[
            ('new', 'Nuevo'), ('in_rute', 'En Ruta'), ('complete', 'Terminado Completo'),
            ('final_incomplete', 'Terminado Incompleto'), ('cancel', 'Cancelado')
        ],
        copy=False,
        index=True,
        store=True,
        default='new',
        string="Estado"
    )
    route_id = fields.Many2one(
        comodel_name="delivery_logistic.route",
        ondelete="cascade",
        copy=False,
        readonly=True,
        string="Ruta"
    )
    driver_id = fields.Many2one(
        comodel_name="res.partner",
        ondelete="cascade",
        domain=[('is_driver', '=', True)],
        readonly=True,
        copy=False,
        string="Piloto"
    )
    vehicle_id = fields.Many2one(
        comodel_name="fleet.vehicle",
        ondelete="cascade",
        readonly=True,
        copy=False,
        string="Vehículo"
    )
    initial_date = fields.Date(
        copy=False,
        string="Fecha salida"
    )
    final_date = fields.Date(
        copy=False,
        string="Fecha regreso"
    )
    picking_ids = fields.One2many(
        comodel_name="stock.picking",
        inverse_name="trip_id",
        domain=[('is_return_picking', '=', False)],
        copy=False,
        string="Entregas"
    )
    return_picking_ids = fields.One2many(
        comodel_name="stock.picking",
        inverse_name="trip_id",
        domain=[('is_return_picking', '=', True), ('state', '!=', 'cancel')],
        copy=False,
        string="Retornos de entregas"
    )
    has_returns = fields.Boolean(
        default=False,
        copy=False,
        store=True,
        compute="_compute_has_returns",
        string="Con devolución"
    )
    has_full_returns = fields.Boolean(
        default=False,
        copy=False,
        store=True,
        string="Con devolución total"
    )
    sale_order_ids = fields.Many2many(
        comodel_name="sale.order",
        relation="trip_sale_order_rel",
        column1="trip_id",
        column2="sale_order_id",
        ondelete="cascade",
        store=True,
        copy=False,
        string="Pedido(s) de venta"
    )
    company_id = fields.Many2one(
        'res.company', string='Compañía',
        store=True, readonly=True, default=lambda self: self.env.company
    )
    can_edit_dates = fields.Boolean(copy=False, compute='_compute_can_edit_dates')

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        """Extension de message_post para poder enviar notificaciones chatter en los viajes de entrega."""
        return super(Trip, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)

    def action_start_trip(self):
        """Accion para iniciar un viaje de entrega.
            Se evaluara que este en estado nuevo para poder avanzar al estado en ruta.
                Si fue correcta la validacion, entonces se evaluara que el viaje no tenga devoluciones,
                se procedera a evaluar mediante _evaluate_returns_trip
                para saber si el viaje debe ser cancelado o permitir iniciar,
                en dependencia si existen aun cantidades por entregar, luego de la devolucion.
            Si el estado no es nuevo, se mostrara un mensaje de restriccion, haciendo mencion del problema."""
        if self.state == 'new':
            if self._evaluate_returns_trip():
                self.write({'state': 'in_rute', 'final_date': fields.Date.today()})
            else:
                self.write({'has_full_returns': True})
        else:
            raise ValidationError(
                'El viaje debe estar en el estado nuevo para poder ser puesto en ruta.'
            )

    @api.model
    def _final_state_trip(self, trip, state):
        """Metodo de evaluacion para finalizar o terminar un viaje, ya sea completo o incompleto, segun parametros.
            Se evalua si el viaje esta en ruta para poder avanzar.
                Si la validacion fue exitosa, entonces cambiara de estado, segun parametro enviado.
                Y se agregara la fecha actual, para finalizar el viaje.
                Se creara un reporte adjunto tipo binario del viaje, almacenado en la tabla ir.attachment.
            Si la evaluacion de estado no es correcta, entonces se mostrara un mensaje de restriccion."""
        if trip.state == 'in_rute':
            trip.write({'state': state, 'final_date': fields.Date.today()})
            report = self.env.ref('delivery_logistic.action_report_trip')
            pdf_content, content_type = report.render_qweb_pdf(trip.id)
            pdf_name = _('Viaje de entrega %s' % trip.name)
            self.env['ir.attachment'].create({
                'name': pdf_name,
                'type': 'binary',
                'datas': base64.encodestring(pdf_content),
                'res_model': trip._name,
                'res_id': trip.id
            })
        else:
            raise ValidationError(
                'El o los viaje(s) debe(n) estar en ruta para poder ser marcado(s) como terminado(s).'
            )

    def action_final_complete(self):
        """Accion de terminar completo incompleto desde treeview.
            Enlace entre el boton y la funcion _final_state_trip que realiza el proceso de finalizacion"""
        for record in self:
            record._final_state_trip(record, 'complete')

    def action_final_incomplete(self):
        """Accion de terminar incompleto desde treeview.
            Enlace entre el boton y la funcion _final_state_trip que realiza el proceso de finalizacion"""
        for record in self:
            record._final_state_trip(record, 'final_incomplete')

    def action_singleton_final_complete_trip(self):
        """Accion de terminar completo incompleto desde formview.
            Enlace entre el boton y la funcion _final_state_trip que realiza el proceso de finalizacion"""
        self._final_state_trip(self, 'complete')

    def action_singleton_final_incomplete_trip(self):
        """Accion de terminar incompleto desde formview.
            Enlace entre el boton y la funcion _final_state_trip que realiza el proceso de finalizacion"""
        self._final_state_trip(self, 'final_incomplete')

    def unlink_from_trip(self):
        """Elimina entregas y genera una notificacion tanto para el viaje
            como para la(s) transferencia(s) de inventario."""
        msg = """El viaje ha sufrido cambios. 
                <br/>"""
        action_cancel = self.env.context.get('action_cancel')
        picks = self.picking_ids.filtered(lambda p: not p.return_picking_ids) \
            if action_cancel else self.picking_ids.filtered(lambda p: not p.return_picking_ids and p.delete_delivery)
        if picks:
            msg += """La(s) entrega(s): 
                            <br/>
                            <ol>"""
        else:
            raise ValidationError('No hay entregas para eliminar.')
        for record in picks:
            msg += """<li>""" + str(record.name) + """</li>"""
            display_msg = """La entrega ha sido eliminada del viaje """ + """<b>""" + record.trip_id.name + """</b>.
                           <br/> """
            display_msg += """<b>Por favor proceder a reprogramar la entrega.</b> <br/>"""
            record.trip_id.write({'sale_order_ids': [(3, record.sale_id.id)]})
            record.write({'reschedule': True, 'trip_id': False, 'delete_delivery': False})
            followers = record.message_partner_ids.ids
            channels = record.message_channel_ids.ids
            record.message_post(body=display_msg, message_type='notification', subject="Reprogramación de entrega",
                                partner_ids=followers, channel_ids=channels, starred=True)
        msg += """</ol>
                  <br/>"""
        msg += """Ha(n) sido eliminada(s).
               <br/>"""
        followers = self.sudo().message_partner_ids.ids
        channels = self.sudo().message_channel_ids.ids
        self.sudo().message_post(body=msg, message_type='notification', subject="Entrega(s) eliminada(s).",
                                 partner_ids=followers, channel_ids=channels, starred=True)
        if not self.picking_ids and not action_cancel:
            self.write({'has_full_returns': True})

    def action_cancel(self):
        """Accion para cancelar un viaje.
            Se evaluan los estados posibles en los que beneria estar, si la evaluacion es correcta,
            se cancela y se manda a llamar el metodo unlink_from_trip para notificar
            y hacer el proceso de eliminacion de la entregas enlazadas.
            Se envia el contexto action_cancel=True lo que hara es indicar que el llamado proviene desde esta accion."""
        if self.state in ['new', 'in_rute']:
            self.write({'state': 'cancel'})
            self.with_context(action_cancel=True).unlink_from_trip()
        else:
            raise ValidationError(
                'El viaje debe estar en los estados nuevo o en ruta para poder ser cancelado.'
            )

    def action_add_deliveries(self):
        """Accion para agregar entrega(s) al viaje.
                Abre el TreeView vpicktree_add_delivery_logistic para que se seleccionen las entregas deseadas."""
        view = self.env.ref('delivery_logistic.vpicktree_add_delivery_logistic')
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'tree',
            'view_mode': 'tree',
            'res_model': 'stock.picking',
            'view_id': view.id,
            'views': [(view.id, 'tree')],
            'domain': [
                ('route_id', '=', self.route_id.id), ('trip_id', '=', False), ('is_return_picking', '=', False),
                ('state', '!=', 'cancel'), ('is_delivery', '=', True), ('delivery_date', '=', self.initial_date)
            ],
            'target': 'new'
        }
