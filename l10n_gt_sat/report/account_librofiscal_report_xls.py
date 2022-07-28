# -*- coding: utf-8 -*-
from odoo import models,api
from datetime import datetime
import io
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

class LibroFiscalReportXls(models.AbstractModel):
    _name = 'report.l10n_gt_sat.account_librofiscal_report_xls'
    _description = 'Reporte Fiscal XLS'
    _inherit = 'report.report_xlsx.abstract'

    workbook = None

    def _get_libro_ventas(self, libro, sheet_libro, fila, columna, format1, date_format, vendedor, workbook, workbook_format):
        bold = workbook_format['bold']
        fnumerico = workbook_format['fnumerico']
        money = workbook_format['money']

        sheet_libro.set_column(columna,columna,4)
        sheet_libro.set_column(columna + 1,columna + 1,8)
        sheet_libro.set_column(columna + 2,columna + 2,12)
        sheet_libro.set_column(columna + 3,columna + 3,12)
        sheet_libro.set_column(columna + 4,columna + 4,12)
        sheet_libro.set_column(columna + 5,columna + 5,19)
        sheet_libro.set_column(columna + 6,columna + 6,15)
        sheet_libro.set_column(columna + 7,columna + 7,55)
        sheet_libro.set_column(columna + 8,columna + 8,12)
        sheet_libro.set_column(columna + 9,columna + 9,12)
        sheet_libro.set_column(columna + 10,columna + 10,12)
        sheet_libro.set_column(columna + 11,columna + 11,12)
        sheet_libro.set_column(columna + 12,columna + 12,12)
        sheet_libro.set_column(columna + 13,columna + 13,12)
        sheet_libro.set_column(columna + 14,columna + 14,12)
        sheet_libro.set_column(columna + 15,columna + 15,12)
        if vendedor:
            sheet_libro.set_column(columna + 16,columna + 16,30)


        sheet_libro.write(fila, columna, "No.", format1)
        sheet_libro.write(fila, columna + 1, "Cod.", format1)
        sheet_libro.write(fila, columna + 2, "# Interno", format1)
        sheet_libro.write(fila, columna + 3, "Fecha", format1)
        sheet_libro.write(fila, columna + 4, "Serie", format1)
        sheet_libro.write(fila, columna + 5, "No. Factura", format1)
        sheet_libro.write(fila, columna + 6, "Nit", format1)
        sheet_libro.write(fila, columna + 7, "Nombre", format1)
        sheet_libro.write(fila, columna + 8, "Exenta", format1)
        sheet_libro.write(fila, columna + 9, "Exp. Fuera CA.", format1)
        sheet_libro.write(fila, columna + 10, "Exp. Centro A.", format1)
        sheet_libro.write(fila, columna + 11, "Servicios", format1)
        sheet_libro.write(fila, columna + 12, "Ventas", format1)
        sheet_libro.write(fila, columna + 13, "Subtotal", format1)
        sheet_libro.write(fila, columna + 14, "Iva", format1)
        sheet_libro.write(fila, columna + 15, "Total", format1)
        if vendedor:
            sheet_libro.write(fila, columna + 16, "Vendedor", format1)

        fila += 1

        for f in libro['facturas']:
            sheet_libro.write(fila, columna, f.no_linea)
            sheet_libro.write(fila, columna + 1, f.journal_id.code)
            sheet_libro.write(fila, columna + 2, f.name)
            sheet_libro.write(fila, columna + 3, f.invoice_date, date_format)
            sheet_libro.write(fila, columna + 4, f.sat_fac_serie)
            sheet_libro.write(fila, columna + 5, f.sat_fac_numero)
            sheet_libro.write(fila, columna + 6, f.partner_id.vat if f.state not in ('cancel') else '')
            sheet_libro.write(fila, columna + 7, f.partner_id.name if f.state not in ('cancel') else 'Anulado')
            sheet_libro.write(fila, columna + 8, f.sat_exento, fnumerico)
            sheet_libro.write(fila, columna + 9, 0, fnumerico)
            sheet_libro.write(fila, columna + 10, f.sat_exportacion_in_ca, fnumerico)
            sheet_libro.write(fila, columna + 11, f.sat_servicio, fnumerico)
            sheet_libro.write(fila, columna + 12, f.sat_bien, fnumerico)
            sheet_libro.write(fila, columna + 13, f.sat_subtotal, fnumerico)
            sheet_libro.write(fila, columna + 14, f.sat_iva, fnumerico)
            sheet_libro.write(fila, columna + 15, f.sat_amount_total, fnumerico)
            if vendedor:
                sheet_libro.write(fila, columna + 16, f.invoice_user_id.name)
            fila += 1

        r = libro['resumen']
        sheet_libro.write(fila, columna + 8, r['sat_exento'], money)
        sheet_libro.write(fila, columna + 10, r['sat_exportacion_in_ca'], money)
        sheet_libro.write(fila, columna + 11, r['servicio'], money)
        sheet_libro.write(fila, columna + 12, r['bien'], money)
        sheet_libro.write(fila, columna + 13, r['sat_subtotal_total'], money)
        sheet_libro.write(fila, columna + 14, r['sat_iva_total'], money)
        sheet_libro.write(fila, columna + 15, r['amount_total_total'], money)
        fila += 1

        return sheet_libro

    def _get_libro_compras(self, libro, sheet_libro, fila, columna, format1, date_format, workbook, workbook_format):
        bold = workbook_format['bold']
        fnumerico = workbook_format['fnumerico']
        money = workbook_format['money']

        sheet_libro.set_column(columna,columna,4)
        sheet_libro.set_column(columna + 1,columna + 1,8)
        sheet_libro.set_column(columna + 2,columna + 2,12)
        sheet_libro.set_column(columna + 3,columna + 3,12)
        sheet_libro.set_column(columna + 4,columna + 4,12)
        sheet_libro.set_column(columna + 5,columna + 5,12)
        sheet_libro.set_column(columna + 6,columna + 6,12)
        sheet_libro.set_column(columna + 7,columna + 7,55)
        sheet_libro.set_column(columna + 8,columna + 8,10)
        sheet_libro.set_column(columna + 9,columna + 9,10)
        sheet_libro.set_column(columna + 10,columna + 10,10)
        sheet_libro.set_column(columna + 11,columna + 11,10)
        sheet_libro.set_column(columna + 12,columna + 12,12)
        sheet_libro.set_column(columna + 13,columna + 13,12)
        sheet_libro.set_column(columna + 14,columna + 14,12)
        sheet_libro.set_column(columna + 15,columna + 15,12)
        sheet_libro.set_column(columna + 16,columna + 16,12)
        sheet_libro.set_column(columna + 17,columna + 17,12)
        sheet_libro.set_column(columna + 18,columna + 18,12)



        sheet_libro.write(fila, columna, "No.", format1)
        sheet_libro.write(fila, columna + 1, "Cod.", format1)
        sheet_libro.write(fila, columna + 2, "Interno", format1)
        sheet_libro.write(fila, columna + 3, "Fecha", format1)
        sheet_libro.write(fila, columna + 4, "Serie", format1)
        sheet_libro.write(fila, columna + 5, "No. Factura", format1)
        sheet_libro.write(fila, columna + 6, "Nit", format1)
        sheet_libro.write(fila, columna + 7, "Nombre", format1)
        sheet_libro.write(fila, columna + 8, "Exenta", format1)
        sheet_libro.write(fila, columna + 9, "Importacion fuera CA", format1)
        sheet_libro.write(fila, columna + 10, "Importacion CA", format1)
        sheet_libro.write(fila, columna + 11, "Servicios", format1)
        sheet_libro.write(fila, columna + 12, "Compra de activos fijos", format1)
        sheet_libro.write(fila, columna + 13, "Pequeño Contrib.", format1)
        sheet_libro.write(fila, columna + 14, "Bienes", format1)
        sheet_libro.write(fila, columna + 15, "Combust.", format1)
        sheet_libro.write(fila, columna + 16, "Base para Compras", format1)
        sheet_libro.write(fila, columna + 17, "IVA", format1)
        sheet_libro.write(fila, columna + 18, "Total", format1)

        fila += 1

        for f in libro['facturas']:
            sheet_libro.write(fila, columna, f.no_linea)
            sheet_libro.write(fila, columna + 1, f.journal_id.code)
            sheet_libro.write(fila, columna + 2, f.name)
            sheet_libro.write(fila, columna + 3, f.invoice_date, date_format)
            sheet_libro.write(fila, columna + 4, f.sat_fac_serie)
            sheet_libro.write(fila, columna + 5, f.sat_fac_numero)
            sheet_libro.write(fila, columna + 6, f.partner_id.vat)
            sheet_libro.write(fila, columna + 7, f.partner_id.name)
            sheet_libro.write(fila, columna + 8, f.sat_exento, fnumerico)
            sheet_libro.write(fila, columna + 9, f.sat_importa_out_ca, fnumerico)
            sheet_libro.write(fila, columna + 10, f.sat_importa_in_ca, fnumerico)
            sheet_libro.write(fila, columna + 11, f.sat_servicio, fnumerico)
            sheet_libro.write(fila, columna + 12, 0, fnumerico)
            sheet_libro.write(fila, columna + 13, f.sat_peq_contri, fnumerico)
            sheet_libro.write(fila, columna + 14, f.sat_bien, fnumerico)
            sheet_libro.write(fila, columna + 15, f.sat_combustible, fnumerico)
            sheet_libro.write(fila, columna + 16, f.sat_base, fnumerico)
            sheet_libro.write(fila, columna + 17, f.sat_iva, fnumerico)
            sheet_libro.write(fila, columna + 18, f.sat_amount_total, fnumerico)
            #sheet_libro.write(fila, columna + 19, f.sat_servicio * (f.sat_iva_porcentaje/100), fnumerico)
            #sheet_libro.write(fila, columna + 20, f.sat_bien * (f.sat_iva_porcentaje/100), fnumerico)
            fila += 1

        r = libro['resumen']
        sheet_libro.write(fila, columna + 8, r['sat_exento'], money)
        sheet_libro.write(fila, columna + 9, r['sat_importa_out_ca'], money)
        sheet_libro.write(fila, columna + 10, r['sat_importa_in_ca'], money)
        sheet_libro.write(fila, columna + 11, r['servicio'], money)
        sheet_libro.write(fila, columna + 13, r['sat_peq_contri'], money)
        sheet_libro.write(fila, columna + 14, r['bien'], money)
        sheet_libro.write(fila, columna + 15, r['sat_combustible'], money)
        sheet_libro.write(fila, columna + 16, r['sat_base'], money)
        sheet_libro.write(fila, columna + 17, r['sat_iva_total'], money)
        sheet_libro.write(fila, columna + 18, r['amount_total_total'], money)
        fila += 1

        sheet_libro = workbook.add_worksheet("Resumen " + libro['descripcion'])

        fila = 0
        sheet_libro.set_column(columna,columna,15)
        sheet_libro.set_column(columna + 1,columna + 1,12)
        sheet_libro.set_column(columna + 2,columna + 2,12)
        sheet_libro.set_column(columna + 3,columna + 3,12)

        sheet_libro.write(fila, columna, "Concepto", bold)
        sheet_libro.write(fila, columna + 1, "Base Imponible", bold)
        sheet_libro.write(fila, columna + 2, "IVA", bold)
        sheet_libro.write(fila, columna + 3, "Total", bold)

        fila += 1
        sheet_libro.write(fila, columna, "Servicio")
        sheet_libro.write(fila, columna + 1, r['servicio'], fnumerico)
        sheet_libro.write(fila, columna + 2, r['servicio_iva'], fnumerico)
        sheet_libro.write(fila, columna + 3, r['servicio_total'], fnumerico)

        fila += 1
        sheet_libro.write(fila, columna, "Bienes")
        sheet_libro.write(fila, columna + 1, r['bien'], fnumerico)
        sheet_libro.write(fila, columna + 2, r['bien_iva'], fnumerico)
        sheet_libro.write(fila, columna + 3, r['bien_total'], fnumerico)

        fila += 1
        sheet_libro.write(fila, columna, "Pequeño Contribuyente")
        sheet_libro.write(fila, columna + 1, r['sat_peq_contri'], fnumerico)
        sheet_libro.write(fila, columna + 2, 0, fnumerico)
        sheet_libro.write(fila, columna + 3, r['sat_peq_contri'], fnumerico)

        fila += 1
        sheet_libro.write(fila, columna, "Combustible")
        sheet_libro.write(fila, columna + 1, r['sat_combustible'], fnumerico)
        sheet_libro.write(fila, columna + 2, r['sat_combustible_iva'], fnumerico)
        sheet_libro.write(fila, columna + 3, r['sat_combustible_total'], fnumerico)

        fila += 1
        sheet_libro.write(fila, columna, "Importacion CA")
        sheet_libro.write(fila, columna + 1, r['sat_importa_in_ca'], fnumerico)
        sheet_libro.write(fila, columna + 2, r['sat_importa_in_ca_iva'], fnumerico)
        sheet_libro.write(fila, columna + 3, r['sat_importa_in_ca_total'], fnumerico)

        fila += 1
        sheet_libro.write(fila, columna, "Importacion Fuera CA")
        sheet_libro.write(fila, columna + 1, r['sat_importa_out_ca'], fnumerico)
        sheet_libro.write(fila, columna + 2, r['sat_importa_out_ca_iva'], fnumerico)
        sheet_libro.write(fila, columna + 3, r['sat_importa_out_ca_total'], fnumerico)

        fila += 1
        sheet_libro.write(fila, columna, "Total")
        sheet_libro.write_formula(fila, columna + 1, '=SUM(B2:B7)', fnumerico)
        sheet_libro.write(fila, columna + 2, '=SUM(C2:C7)', fnumerico)
        sheet_libro.write(fila, columna + 3, '=SUM(D2:D7)', fnumerico)

        sheet_libro = workbook.add_worksheet("Top 10 " + libro['descripcion'])

        fila = 0
        sheet_libro.set_column(columna,columna,12)
        sheet_libro.set_column(columna + 1,columna + 1,55)
        sheet_libro.set_column(columna + 2,columna + 2,12)
        sheet_libro.set_column(columna + 3,columna + 3,12)


        sheet_libro.write(fila, columna, "Nit", bold)
        sheet_libro.write(fila, columna + 1, "Cliente", bold)
        sheet_libro.write(fila, columna + 2, "Cantidad", bold)
        sheet_libro.write(fila, columna + 3, "Monto Base", bold)
        fila = 1
        for t in libro['top10_documentos']:
            sheet_libro.write(fila, columna, t['partner'].vat)
            sheet_libro.write(fila, columna + 1, t['partner'].name)
            sheet_libro.write(fila, columna + 2, t['cant_docs'], fnumerico)
            sheet_libro.write(fila, columna + 3, t['sat_base'], fnumerico)
            fila += 1

        sheet_libro.write(fila, columna, '')
        sheet_libro.write(fila, columna + 1, 'Diferencia')
        sheet_libro.write(fila, columna + 2, libro['top10_documentos_diferencia']['cant_docs'], fnumerico)
        sheet_libro.write(fila, columna + 3, libro['top10_documentos_diferencia']['sat_base'], fnumerico)

        fila += 1
        sheet_libro.write(fila, columna, "")
        sheet_libro.write(fila, columna + 1, "Total", fnumerico)
        sheet_libro.write(fila, columna + 2, libro['top10_documentos_total']['cant_docs'], fnumerico)
        sheet_libro.write(fila, columna + 3, libro['top10_documentos_total']['sat_base'], fnumerico)


        return sheet_libro

    def generate_xlsx_report(self, workbook, data, data_report):
        #self.workbook = workbook

        format1 = workbook.add_format({'font_size': 12, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'vcenter', 'bold': True})
        format1.set_align('center')

        bold = workbook.add_format({'bold': True})
        fnumerico = workbook.add_format({'num_format': '#,##0.00'})
        money = workbook.add_format({'font_size': 12, 'bottom': True, 'right': True, 'left': True, 'top': True, 'align': 'vcenter', 'bold': True, 'num_format': '#,##0.00'})
        date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})

        workbook_format = {
            'bold': bold,
            'fnumerico': fnumerico,
            'money': money,
        }
        libros_fiscales = self.env["report.l10n_gt_sat.librofiscal"].get_libro(data)
        for libro in libros_fiscales:
            sheet_libro = workbook.add_worksheet(libro['descripcion'])


            sheet_libro.write(0, 0, data['form']['company_id'][1], bold)
            sheet_libro.write(1, 0, "Libro de " + libro['descripcion'], bold)
            sheet_libro.write(2, 0, "Del: " + libro['del'] + "Al: " + libro['del'], bold)

            vendedor = data['form']['vendedor']

            fila = 5
            columna = 0

            if libro['libro'] == 'sale':
                sheet_libro = self._get_libro_ventas(libro, sheet_libro, fila, columna, format1, date_format, vendedor, workbook, workbook_format)
            else:
                sheet_libro = self._get_libro_compras(libro, sheet_libro, fila, columna, format1, date_format, workbook, workbook_format)
