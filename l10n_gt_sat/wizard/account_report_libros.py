# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import datetime
import json
from odoo.tools import date_utils
import io
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

TIPOS_DE_LIBROS = [
            ('all', 'Todo'),
            ('sale', 'Ventas'),
            ('purchase', 'Compras'),
        ]

MESES = [
            ('1','Enero'),
            ('2','Febrero'),
            ('3','Marzo'),
            ('4','Abril'),
            ('5','Mayo'),
            ('6','Junio'),
            ('7','Julio'),
            ('8','Agosto'),
            ('9','Septiembre'),
            ('10','Octubre'),
            ('11','Noviembre'),
            ('12','Diciembre'),
        ]
class AccountLibroFiscalReport(models.TransientModel):
    _name = "l10n_gt_sat.librofiscal.report"
    _description = "Libro Fiscal Report"

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    libro = fields.Selection(TIPOS_DE_LIBROS, string='Libro', required=True, default='all')
    tipo = fields.Selection([('detallado', 'Detallado'),
                             ('resumido', 'Resumido'),
                            ], string='Tipo', required=True, default='detallado')
    now = datetime.datetime.now()
    periodo = fields.Selection(MESES,string='Periodo',default=str(now.month))
    ejercicio = fields.Integer(string='Ejercicio', default=now.year)
    vendedor = fields.Boolean(string='Vendedor', default=True)

    def check_report(self):
        self.ensure_one()
        data = {}
        data['form'] = self.read(['libro', 'tipo', 'periodo', 'ejercicio', 'company_id'])[0]
        return self.env.ref('l10n_gt_sat.action_report_librofiscal').with_context(landscape=True).report_action(self, data=data)

    def export_xls(self):
        print("Si llego")
        self.ensure_one()
        data = {}
        data['form'] = self.read(['libro', 'tipo', 'periodo', 'ejercicio', 'company_id', 'vendedor'])[0]
        return self.env.ref('l10n_gt_sat.account_librofiscal_report_xls').report_action(self,data=data)
    
    # def export_xls(self):
    #     print("--------------------------------------- 1")
    #     self.ensure_one()
    #     data = {
    #         'ids': self.ids,
    #         'model': self._name,
    #         'form': self.read(['libro', 'tipo', 'periodo', 'ejercicio', 'company_id', 'vendedor'])[0]
    #     }
    #     return {
    #         'type': 'ir.actions.report',
    #         'data': {'model': 'l10n_gt_sat.account_librofiscal_report_xls',
    #                  'options': json.dumps(data, default=date_utils.json_default),
    #                  'output_format': 'xlsx',
    #                  'report_name': 'Current Stock History',
    #                  },
    #         'report_type': 'stock_xlsx'
    #     }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        comp = self.env.user.company_id.name
        sheet = workbook.add_worksheet(comp)
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()        