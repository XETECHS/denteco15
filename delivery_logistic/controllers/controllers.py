# -*- coding: utf-8 -*-

import io
import re
from PyPDF2 import PdfFileReader, PdfFileWriter

from odoo.http import request, route, Controller
from odoo.tools.safe_eval import safe_eval


class DeliveryLogisticTrip(Controller):

    @route(["/print/trips"], type='http', auth='user')
    def get_trip_report_print(self, list_ids='', **post):
        if not request.env.user.has_group('delivery_logistic.group_delivery_logistic_manager') \
                or not list_ids or re.search("[^0-9|,]", list_ids):
            return request.not_found()

        ids = [int(s) for s in list_ids.split(',')]
        trips = request.env['delivery_logistic.trip'].browse(ids)

        pdf_writer = PdfFileWriter()

        for trip in trips:
            report = request.env.ref('delivery_logistic.action_report_trip')
            pdf_content, _ = report.render_qweb_pdf(trip.id)
            reader = PdfFileReader(io.BytesIO(pdf_content), strict=False, overwriteWarnings=False)

            for page in range(reader.getNumPages()):
                pdf_writer.addPage(reader.getPage(page))

        _buffer = io.BytesIO()
        pdf_writer.write(_buffer)
        merged_pdf = _buffer.getvalue()
        _buffer.close()

        report_name = 'Viajes de entrega'

        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(merged_pdf)),
            ('Content-Disposition', 'attachment; filename=' + report_name + '.pdf;')
        ]

        return request.make_response(merged_pdf, headers=pdfhttpheaders)
