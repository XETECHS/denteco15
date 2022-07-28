# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class ChequeSetting(models.Model):
    _name = 'cheque.setting'
    _description = 'Cheque Setting'

    name = fields.Char('Nombre', required="1")
    font_size_check = fields.Float('Tamaño de Letra Cheque', default="18", required="1")
    font_size = fields.Float('Tamaño de Letra Diario / Asiento', default="15", required="1")
    color = fields.Char('Color', default="#000", required="1")
    # set_default = fields.Boolean('Default Template', copy=False) company_id = fields.Many2one('res.company',
    # string='Company', default=lambda self:self.env.user.company_id.id, required="1")

    is_partner = fields.Boolean('_Imprimir', default=True)
    is_partner_bold = fields.Boolean('Letra en Negrita')
    partner_text = fields.Selection([('prefix', 'Prefix'), ('suffix', 'Suffix')], string='Título a Contacto')
    partner_m_top = fields.Float('Desde Arriba', default=130)
    partner_m_left = fields.Float('Desde Izquierda', default=75)

    is_date = fields.Boolean('Imprimir', default=True)
    date_formate = fields.Selection([('dd_mm', 'DD MM'), ('mm_dd', 'MM DD')], string='Formato Fecha', default='dd_mm')
    year_formate = fields.Selection([('yy', 'YY'), ('yyyy', 'YYYY')], string='Formato Año', default='yy')
    date_m_top = fields.Float('Desde Arriba', default=101.24)
    gt_left = fields.Float('País', default=75)
    f_d_m_left = fields.Float('Primer Dígito', default=150)
    s_d_m_left = fields.Float('Segundo Dígito', default=160)
    t_d_m_left = fields.Float('Tercer Dígito', default=190)
    fo_d_m_left = fields.Float('Cuatro Dígito', default=200)
    fi_d_m_left = fields.Float('Quinto Dígito', default=225)
    si_d_m_left = fields.Float('Sexto Dígito', default=235)
    se_d_m_left = fields.Float('Séptimo Dígito', default=245)
    e_d_m_left = fields.Float('Octavo Dígito', default=255)
    
    date_seprator = fields.Char('Separador')

    is_amount = fields.Boolean('Imprimir', default=True)
    amt_m_top = fields.Float('Desde Arriba', default=101.24)
    amt_m_left = fields.Float('Desde Izquierda', default=650)
    is_star = fields.Boolean('Imprimir Asteríco',
                             help="Si es seleccionado imprimirá 3 asteríscos antes y después del monto.", default=True)

    is_currency = fields.Boolean('Imprimir Moneda')

    is_amount_word = fields.Boolean('Imprimir', default=True)
    is_word_bold = fields.Boolean('Letra en Negrita')
    word_in_f_line = fields.Float('Palabras en primera línea', default=5,
                                  help="Cuántas palabras desea imprimir en la primera línea, "
                                       "El resto ira en la segunga línea")
    amt_w_m_top = fields.Float('Desde Arriba antes', default=158.76)
    amt_w_m_left = fields.Float('Desde Izquierdo antes', default=70)
    is_star_word = fields.Boolean('Imprimir Asteríco',
                                  help="Si es seleccionado imprimirá 3 asteríscos antes y después del monto.",
                                  default=True)

    amt_w_s_m_top = fields.Float('Desde Arriba después', default=185)
    amt_w_s_m_left = fields.Float('Desde Izquierdo después', default=70)

    is_company = fields.Boolean('Impimir')
    c_margin_top = fields.Float('Desde Arriba', default=380)
    c_margin_left = fields.Float('Desde Izquierda', default=75)

    print_journal = fields.Boolean('Imprimir')
    journal_margin_top = fields.Float('Desde Arriba', default=300)
    standard_accounting_entry = fields.Boolean('Estándar', default=True)
    journal_margin_left = fields.Float('Desde Izquierda', default=10)
    date_margin_left = fields.Float('Fecha desde Izquierda', default=10)
    date_title_margin_top = fields.Float('Título Fecha desde Arriba', default=0)
    date_column_margin_top = fields.Float('Fecha desde Arriba', default=30)
    account_margin_left = fields.Float('Cuenta desde Izquierda', default=120)
    account_title_margin_top = fields.Float('Título Cuenta desde Arriba', default=0)
    account_column_margin_top = fields.Float('Cuenta desde Arriba', default=30)
    debit_margin_left = fields.Float('Debe desde Izquierda', default=250)
    debit_title_margin_top = fields.Float('Título Debe desde Arriba', default=0)
    debit_column_margin_top = fields.Float('Debe desde Arriba', default=30)
    credit_margin_left = fields.Float('Haber desde Izquierda', default=300)
    credit_title_margin_top = fields.Float('Título Haber desde Arriba', default=0)
    credit_column_margin_top = fields.Float('Haber desde Arriba', default=30)

    is_stub = fields.Boolean('Imprimir')
    stub_margin_top = fields.Float('Desde Arriba', default=700)
    stub_margin_left = fields.Float('Desde Izquierda', default=10)

    is_cheque_no = fields.Boolean('Imprimir')
    cheque_margin_top = fields.Float('Desde Arriba', default=408.46)
    cheque_margin_left = fields.Float('Desde Izquierda', default=75)

    is_free_one = fields.Boolean('Imprimir')
    f_one_margin_top = fields.Float('Desde Arriba', default=758.46)
    f_one_margin_left = fields.Float('Desde Izquierda', default=75)

    is_communication = fields.Boolean('Imprimir')
    f_two_margin_top = fields.Float('Desde Arriba', default=730.00)
    f_two_margin_left = fields.Float('Desde Izquierda', default=75)

    is_non_negotiable = fields.Boolean('Imprimir')
    non_n_margin_top = fields.Float('Desde Arriba', default=213)
    non_n_margin_left = fields.Float('Desde Izquierda', default=75)

    is_acc_pay = fields.Boolean('Imprimir A/C PAY', default=True)
    acc_pay_m_top = fields.Float('Desde Arriba', default=50)
    acc_pay_m_left = fields.Float('Desde Izquierda', default=50)
    
    is_f_line_sig = fields.Boolean('Imprimir')
    f_sig_m_top = fields.Float('Desde Arriba', default=960)
    f_sig_m_left = fields.Float('Desde Izquierda', default=100)
    
    is_s_line_sig = fields.Boolean('Imprimir')
    s_sig_m_top = fields.Float('Desde Arriba', default=960)
    s_sig_m_left = fields.Float('Desde Izquierda', default=530)

    # @api.constrains('set_default', 'company_id') def _check_description(self): for line in self: if
    # line.set_default: line_ids = self.env['cheque.setting'].search([('set_default','=',True),('company_id','=',
    # line.company_id.id)]) if len(line_ids) > 1: raise ValidationError("One Company have one default cheque template")

# vim:expandtab:smartindent:tabstop=4:4softtabstop=4:shiftwidth=4:
