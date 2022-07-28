# -*- coding: utf-8 -*-
from odoo import http
from odoo import api,models,fields

class account_payment(models.Model):
    _inherit = "account.payment"

    def month_to_text(self, month):
        return {
            1: "Enero",
            2: "Febrero",
            3: "Marzo",
            4: "Abril",
            5: "Mayo",
            6: "Junio",
            7: "Julio",
            8: "Agosto",
            9: "Septiembre",
            10: "Octubre",
            11: "Noviembre",
            12: "Diciembre",
        }
