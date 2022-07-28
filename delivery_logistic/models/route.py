# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Route(models.Model):
    _name = 'delivery_logistic.route'
    _description = 'Ruta de entrega'

    name = fields.Char(
        copy=False,
        store=True,
        string="Nombre"
    )

