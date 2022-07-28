# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models, _
from odoo.tools import float_is_zero, float_round, float_repr, float_compare

from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

from .exceptions import InvalidOrderError

from odoo.addons import decimal_precision as dp
from odoo.tools import float_is_zero
from . import fel
from . import letras
from datetime import date,timedelta
import logging
import pytz
try:
    import qrcode
except ImportError:
    qrcode = None
try:
    import base64
except ImportError:
    base64 = None
from io import BytesIO

_logger = logging.getLogger(__name__)
import datetime
import dateutil.relativedelta

class AccountMove(models.Model):
    _inherit = "account.move"

    fel_setting_id = fields.Many2one('fel.setting', string='Facturacion FEL', copy=False, readonly=True)
    fel_firma = fields.Char('Firma FEL', copy=False, readonly=True)
    fel_motivo = fields.Char('Motivo', copy=False, readonly=False)
    # ==== Reverse feature fields ====
    journals_devolucion = fields.Many2many('account.journal', string='Diarios de devolucion', domain=[('tipo_documento','not in',['NCRE','NDEB','NDAB'])])
    fel_factura_referencia_id = fields.Many2one('account.move', string="Factura Referencia", help="Factura de referencia para ligar la nota de debito con la factura",
                                    domain="[('company_id', '=', company_id),('state', '=', 'posted'),('move_type', '=', 'out_invoice'),('partner_id', '=', partner_id)]",)
    fel_factura_devolucion_id = fields.Many2one('account.move', copy=False ,string="Factura Devolución", help="Factura de referencia para ligar la devolución",
                                    domain=lambda self : self.dominio_devolucion(),)

    fecha_certificacion = fields.Char(string='Fecha certificacion',copy=False,readonly=True)

    fel_url = fields.Char(string='Url FEL', help="URL FEL")

    regimen = fields.Char(string='Regimen', help="Regimen")
    
    def dominio_devolucion(self):
        journal_ids = [ id.id for id in self.env['account.journal'].search([('tipo_documento','not in',['NCRE','NDEB','NDAB']),('fel_setting_id','!=',False)])]
        hoy = datetime.datetime.now()
        menos_2_meses = hoy - dateutil.relativedelta.relativedelta(months=2)
        fecha_factura = date(year=menos_2_meses.year, month=menos_2_meses.month, day=menos_2_meses.day)
        dominio = """[('company_id', '=', company_id),('state', '=', 'posted'),('move_type', '=', 'out_invoice'),('partner_id', '=', partner_id),
                                   ('invoice_date','>=','%s'),('journal_id','in',%s)]""" % (str(fecha_factura),journal_ids)
        return dominio
        
    
    def fecha(self):
        if self.invoice_date:
            EndDate = self.invoice_date + timedelta(days=30)
            return '{}/{}/{}'.format(EndDate.day,EndDate.month,EndDate.year)
        else:
            return False
    
    

    def getNitFelFormat(self, nit):
        if nit:
            nit = nit.upper()
            if nit == 'C/F':
                return 'CF'
            if nit == '':
                return 'CF'
            nit = nit.replace('-','')
            return nit
        return 'CF'

    def getListFactura(self):
        factura = self
        
        fel_setting = factura.journal_id.fel_setting_id
        tipo_documento = factura.journal_id.tipo_documento
        
        documento = {}
        documento["factura_id"] = "220418" + str(factura.id)
        documento["CodigoMoneda"] = factura.currency_id.name
        documento["FechaHoraEmision"] = fields.Date.from_string(factura.invoice_date).strftime('%Y-%m-%dT%H:%M:%S')
        documento["Tipo"] = tipo_documento
        documento["AfiliacionIVA"] = factura.journal_id.afiliacion_iva
        documento["CodigoEstablecimiento"] = fel_setting.cod_establecimiento
        documento["NITEmisor"] = factura.company_id.vat.replace('-','')
        documento["NombreComercial"] = fel_setting.nombre_comercial


        #DireccionEmisor
        documento["ECorreoEmisor"] = fel_setting.emisor.email or ''
        documento["ENombreEmisor"] = fel_setting.company_id.name
        documento["EDireccionEmisor"] = fel_setting.emisor.street or 'Ciudad'
        documento["ECodigoPostal"] = fel_setting.emisor.zip or '01001'
        documento["EMunicipio"] = fel_setting.emisor.city or 'Guatemala'
        documento["EDepartamento"] = fel_setting.emisor.state_id.name or 'Guatemala'
        documento["EPais"] = fel_setting.emisor.country_id.code or 'GT'

        #Receptor
        documento["IDReceptor"] = self.getNitFelFormat(factura.partner_id.vat) if factura.partner_id.vat else 'CF'
        documento["NombreReceptor"] = factura.partner_id.name
        documento["CorreoReceptor"] = factura.partner_id.email or ''

        if factura.journal_id.tipo_documento == "FESP":
            documento["IDReceptor"] = factura.partner_id.cui
            documento["TipoEspecial"] = "CUI"

        documento["ReceptorDireccion"] = factura.partner_id.street or 'Ciudad'
        documento["ReceptorCodigoPostal"] = factura.partner_id.zip or '01009'
        documento["ReceptorMunicipio"] = factura.partner_id.city or 'Guatemala'
        documento["ReceptorDepartamento"] = factura.partner_id.state_id.name if factura.partner_id.state_id else 'Guatemala'
        documento["ReceptorPais"] = factura.partner_id.country_id.code or 'GT'

        #Frases
        frases = []
        existen_frases = False
        for frase_escenario in factura.journal_id.fel_frases_ids:
            existen_frases = True
            escenario = {}
            escenario["TipoFrase"] = frase_escenario.fel_tipofrase.code
            escenario["CodigoEscenario"] = frase_escenario.fel_escenario.code
            frases.append(escenario)
        if existen_frases:
            documento["Frases"] = frases

        #Items
        items = []
        gran_total = gran_subtotal = gran_total_impuestos = 0

        get_fac_doc = self.get_detalle_factura()
        for linea_factura in get_fac_doc['detalle']:
            detalle = linea_factura['dato_linea']
            if detalle['price_unit'] > 0 and detalle['quantity'] > 0:
                linea = {}
                linea["BienOServicio"] = "S"  if detalle.product_id.type == "service" else "B"
                linea["Cantidad"] = detalle.quantity
                linea["UnidadMedida"] = detalle.product_uom_id.name
                linea["Descripcion"] = detalle.name

                
                linea["PrecioUnitario"] = '{:.6f}'.format(linea_factura['precio_sin_descuento'])
                linea["Precio"] = '{:.6f}'.format(linea_factura['total_linea_sin_descuento'])
                linea["Descuento"] = '{:.6f}'.format(linea_factura['descuento'])

                if tipo_documento not in ("NABN","RECI","RDON"):
                    linea["NombreCorto"] = "IVA"
                    #Codigo gravable, en el caso de que en la venta se requiera facturar con iva 0 o exento de iva.
                    codigo_unidad_gravable ="1"
                    if detalle.tax_ids:
                        for impuesto_detalle in detalle.tax_ids:
                            codigo_unidad_gravable = str(impuesto_detalle.fel_unidad_gravable.code)
                    linea["CodigoUnidadGravable"] = codigo_unidad_gravable
                    linea["MontoGravable"] = '{:.6f}'.format(linea_factura['total_linea_base'])
                    linea["MontoImpuesto"] = '{:.6f}'.format(linea_factura['total_linea_impuestos'])
                linea["Total"] = '{:.6f}'.format(linea_factura['total_con_descuento'])

                items.append(linea)
        documento["Items"] = items
        tot = get_fac_doc['totales']
        documento["gran_total_impuestos"] = '{:.6f}'.format(tot['total_impuestos'])
        documento["TotalMontoImpuesto"] = '{:.6f}'.format(tot['total_impuestos'])
        documento["GranTotal"] = '{:.6f}'.format(tot['total_total'])

        documento["Adenda"] = factura.name

        #Complementos
        documento["Complementos"] = False
        #Notas de credito o debito
        if tipo_documento in ['NDEB', 'NCRE']:
            documento["Complementos"] = True
            factura_referencia = None
            if tipo_documento in ['NDEB']:
                if factura.fel_factura_referencia_id:
                    factura_referencia = factura.fel_factura_referencia_id
                    documento["RegimenAntiguo"] = "Actual"
                    documento["FechaEmisionDocumentoOrigen"] = str(factura_referencia.invoice_date)
                    factura.regimen = documento["RegimenAntiguo"]
            if tipo_documento in ['NCRE']:
                if factura.reversed_entry_id or factura.fel_factura_devolucion_id:
                    factura_referencia = factura.reversed_entry_id if factura.reversed_entry_id else factura.fel_factura_devolucion_id
                    if factura.fel_factura_devolucion_id and not factura.reversed_entry_id:
                        factura.reversed_entry_id = factura.fel_factura_devolucion_id.id
                    documento["RegimenAntiguo"] = "Antiguo"
                    documento["FechaEmisionDocumentoOrigen"] = str(factura_referencia.invoice_date)
                    factura.regimen = documento["RegimenAntiguo"]
                    #Este if es para identificar si no tiene firma, es del regimen anterior, se realiza por medio de buscar FACE en la descripcion de la serie.
                    
                    no_error = False
                    str_error = 'Documento invalido, falta:\n'
                    
                    if not factura.reversed_entry_id.fac_serie:
                        str_error += '- Número de serie\n'
                        no_error = True
                    if not factura.reversed_entry_id.fac_numero:
                        str_error += '- Número de factura\n'
                        no_error = True
                    if not factura.reversed_entry_id.fel_firma:
                        str_error += '- Firma FEL\n'
                        no_error = True
                    
                    if no_error:
                        str_error += 'Imposible realizar la operación en la orden:'
                        pos_order = self.env['pos.order'].search([('account_move', '=', factura.id)])
                        if pos_order and len(pos_order) == 1:
                            order_id = pos_order[0].pos_reference.split(' ')[1]
                            raise InvalidOrderError(str_error, order_id, "Cliente: " + pos_order.partner_id.name, "Nit: " +  pos_order.partner_id.vat)
                        else:
                            raise InvalidOrderError(str_error)
                        
                    if factura.reversed_entry_id.fac_serie.find("FACE")>=0:
                        documento["RegimenAntiguo"] = "Antiguo"
                        documento["FechaEmisionDocumentoOrigen"] = fields.Date.from_string(factura.invoice_date).strftime('%Y-%m-%dT%H:%M:%S')
                        factura.regimen = documento["RegimenAntiguo"]
                    else:
                        documento["RegimenAntiguo"] = "Actual"
                        documento["FechaEmisionDocumentoOrigen"] = str(factura_referencia.invoice_date)
                        factura.regimen = documento["RegimenAntiguo"]
            documento["MotivoAjuste"] = factura.fel_motivo
            documento["NumeroAutorizacionDocumentoOrigen"] = factura_referencia.fel_firma
            documento["NumeroDocumentoOrigen"] = factura_referencia.fac_numero
            documento["SerieDocumentoOrigen"] = factura_referencia.fac_serie

        #Factura CompCambiaria
        elif tipo_documento in ['FCAM']:
            documento["Complementos"] = True
            documento["FCAM_NumeroAbono"] = "1"
            documento["FCAM_FechaVencimiento"] = str(factura.invoice_date)
            documento["FCAM_MontoAbono"] = '{:.2f}'.format(factura.currency_id.round(gran_total))

        #Factura Especial
        elif tipo_documento in ['FESP']:
            documento["Complementos"] = True
            complemento_especial = factura.get_impuestos_factura_especial()


            documento["FESP_RetencionISR"] = str(complemento_especial['isr'])
            documento["FESP_RetencionIVA"] = str(complemento_especial['iva'])
            documento["FESP_TotalMenosRetenciones"] = str(complemento_especial['totalmenosretenciones'])

        return documento

    def firmar_factura(self, documento, batch, anulacion):
        factura = self

        fel_setting = factura.journal_id.fel_setting_id

        factura.fel_setting_id = fel_setting.id

        fel_dte = fel.Fel()
        if anulacion:
            fel_dte.anular(documento)
        else:
            fel_dte.getXmlFormat(documento)

        fel_dte.setDatosConexion(
            fel_setting.token,
            fel_setting.clave,
            fel_setting.usuario,
            documento["NITEmisor"],
            documento["ECorreoEmisor"],
            documento["factura_id"],
        )
        try:
            firmado = fel_dte.firmar_xml(anulacion)
            logging.info(firmado)
        except IOError as e:
            _logger.exception("\n\n Error de Conexion-------------------------------")

            error_msg = _("Something went wrong during your conexion\n``%s``") % str(e)
            _logger.exception("\n\n" + error_msg)
            raise self.env['res.config.settings'].get_config_warning(error_msg)

        if not firmado["resultado"]:
            _logger.exception("\n\n Error de Factura(%s)-------------------------------" % (factura.id))
            _logger.exception("\n\n" + str(fel_dte.xmls_file))
            _logger.exception("\n\n Error de Firma de Factura(%s)-------------------------------" % (factura.id))
            _logger.exception("\n\n" + fel_dte.xmls_file_firmado)
            if not batch:
                raise UserError(firmado["descripcion"])

        fel_certificacion_response = fel_dte.certificar_xml(anulacion)

        if not fel_certificacion_response["resultado"]:
            mensaje_error = ''
            for m in fel_certificacion_response["descripcion_errores"]:
                mensaje_error = str(m)
            _logger.exception("\n\nFactura(%s)-------------------------------" % (factura.id))
            _logger.exception("\n\n" + str(fel_dte.xmls))
            _logger.exception("\n\nError de Certificado de Factura(%s)-------------------------------" % (factura.id))
            _logger.exception("\n\n" + fel_dte.xmls_file_certificado)
            if not batch:
                str_error = ''
                print(mensaje_error)
                if (
                    "' is not accepted by the pattern '" in mensaje_error
                    or " this exceeds the allowed maximum length of " in mensaje_error
                    or "El NIT del Receptor no existe en las fuentes de datos conectadas a SAT" in mensaje_error
                    or "is not a valid value of the atomic type" in mensaje_error
                 ):
                    str_error = 'Los datos del cliente son incorrectos, por favor revisar antes de generar una nueva orden al cliente, imposible realizar la operación en la orden:'
                else:
                    str_error = mensaje_error
                pos_order = self.env['pos.order'].search([('account_move', '=', factura.id)])
                if pos_order and len(pos_order) == 1:
                    order_id = pos_order[0].pos_reference.split(' ')[1]
                    raise InvalidOrderError(str_error, order_id, "Cliente: " + pos_order.partner_id.name, "Nit: " +  pos_order.partner_id.vat + "\n\n\n\n" + mensaje_error)
                else:
                    raise InvalidOrderError(str_error + "\n\n\n\n" + mensaje_error)
                #raise InvalidOrderError(mensaje_error, "", "", "")

        if not firmado["resultado"] or not fel_certificacion_response["resultado"]:
            msg="Error generando Factura Electronica FEL"
            attachments = [('Factura.xml', fel_dte.xmls_file),('Firmado.json', fel_dte.xmls_file_firmado),('Certificado.json', fel_dte.xmls_file_certificado)]
            factura.message_post(subject='FEL', body=mensaje_error, attachments=attachments)

        if factura.journal_id.fel_setting_id:
            if factura.journal_id.fel_setting_id.attach_xml:
                msg="Generando Factura Electronica FEL"
                attachments = [('Factura.xml', fel_dte.xmls_file),('Firmado.json', fel_dte.xmls_file_firmado),('Certificado.json', fel_dte.xmls_file_certificado)]
                self.message_post(subject='FEL', body=msg, attachments=attachments)
        if fel_certificacion_response["resultado"]:
            logging.info(fel_certificacion_response)
            #Se actualizan los campos siempre y cuando no sea una anulacion.
            if not anulacion:
                factura.fel_firma = fel_certificacion_response["uuid"]
                #factura.name = str(fel_certificacion_response["serie"])+"-"+str(fel_certificacion_response["numero"])
                factura.fac_serie = fel_certificacion_response["serie"]
                factura.fac_numero = fel_certificacion_response["numero"]
                factura.fecha_certificacion = fel_certificacion_response["fecha"]
                msg = "https://report.feel.com.gt/ingfacereport/ingfacereport_documento?uuid="+fel_certificacion_response["uuid"]
                factura.fel_url = msg
                factura.message_post(subject='FEL', body=msg)
        print(fel_certificacion_response)

    def action_post_firmar(self):
        move = self
        if move.journal_id.fel_setting_id:
            if move.fel_factura_devolucion_id and move.journal_id.tipo_documento not in ['NCRE']:
                raise UserError(_("No se puede generar una devolucion con este diario, seleccione un diario de nota de credito."))
            if move.journal_id.tipo_documento in ['FESP']:
                if not move.invoice_payment_term_id:
                    raise UserError(_("Debe ingresar las condiciones de pago."))
                if not move.partner_id.cui:
                    raise UserError(_("El cliente tiene que tener DPI/CUI."))
            if move.journal_id.tipo_documento in ['NABN']:
                if not move.invoice_payment_term_id:
                    raise UserError(_("Debe ingresar las condiciones de pago."))
            if move.journal_id.tipo_documento in ['NDEB']:
                if not move.fel_factura_referencia_id:
                    raise UserError(_("Para operar una nota de debito debe seleccionar una factura referencia."))
            if move.journal_id.tipo_documento in ['NDEB']:
                if not move.fel_motivo:
                    raise UserError(_("Debe ingresar un motivo para el documento."))
            if not move.invoice_payment_term_id and move.journal_id.tipo_documento not in ['NCRE','FACT']:
                raise UserError(_("Debe ingresar las condiciones de pago."))
        if move.journal_id.fel_setting_id and move.state == 'posted':
            if not move.invoice_date:
                raise UserError(_("No puede utilizar este diario, solo se puede utilizar desde una venta."))
            documento = move.getListFactura()
            move.firmar_factura(documento, False, False)

    def action_post(self):
        #try:
        move = super(AccountMove,self).action_post()
        self.action_post_firmar()
        #except Exception as e:
        #    print("Error: ",str(e))
        #    raise UserError(_(str(e)))
        return move

    def button_draft_fel(self):
        move = super(AccountMove,self).button_draft()
        move = super(AccountMove,self).button_cancel()
        fel_dte = fel.Fel()
        for factura in self:
            if factura.fel_setting_id:
                documento = {}
                documento["FechaHoraAnulacion"] = fields.datetime.now(pytz.timezone(self.env.user.tz or 'UTC')).strftime('%Y-%m-%dT%H:%M:%S')
                documento["DatosAnulacion"] = "DatosAnulacion"
                documento["NITEmisor"] = factura.company_id.vat.replace('-','')
                documento["ECorreoEmisor"] = factura.company_id.email or ''
                documento["FechaEmisionDocumentoAnular"] = factura.invoice_date.strftime('%Y-%m-%dT%H:%M:%S')
                documento["IDReceptor"] = self.getNitFelFormat(factura.partner_id.vat) if factura.partner_id.vat else 'CF'
                if factura.journal_id.tipo_documento == "FESP":
                    documento["IDReceptor"] = factura.partner_id.cui
                documento["NumeroDocumentoAAnular"] = factura.fel_firma
                documento["MotivoAnulacion"] = "Cancelacion de Factura"
                documento["factura_id"] = str(factura.id)

                factura.firmar_factura(documento, False, True)

    #INFO FACTURA
    def get_fecha(self):
        fecha = {'dia':'','mes':'','año':''}
        fecha_doc = ""
        if self.invoice_date:
            fecha_doc = self.invoice_date
            fecha['dia'] = fecha_doc.day
            fecha['mes'] = fecha_doc.month
            fecha['año'] = fecha_doc.year
        return fecha

    def get_impuestos_factura_especial(self):
        result = {'isr':0,'iva':0,'totalmenosretenciones':0}
        if self.line_ids:
            for detalle in self.line_ids:
                if detalle.tax_line_id:
                    if detalle.tax_line_id.impuesto_sat and detalle.tax_line_id.impuesto_sat == 'isr':
                        result['isr'] +=  abs(detalle.balance)
                    elif detalle.tax_line_id.impuesto_sat and detalle.tax_line_id.impuesto_sat == 'iva':
                        result['iva'] += abs(detalle.balance)
            result['totalmenosretenciones'] = self.amount_total - result['iva']
        return result

    def generate_qr(self):
        if qrcode and base64:
            if self.fel_url:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(self.fel_url)
                qr.make(fit=True)

                img = qr.make_image()
                temp = BytesIO()
                img.save(temp, format="PNG")
                qr_image = base64.b64encode(temp.getvalue())
                return qr_image
            else:
                return False
        else:
            return False

    def get_info_document(self):
        resultado = {'fecha_emision':'','numero_autorizacion':'','motivo':'','no_origen':'','regimen':''}
        factura_referencia = None
        if self.journal_id.tipo_documento in ['NDEB']:
            factura_referencia = self.fel_factura_referencia_id
        else:
            factura_referencia = self.reversed_entry_id

        if factura_referencia:
            subcadena = factura_referencia.fecha_certificacion[:10]
            fecha_formato = factura_referencia.fecha_certificacion
            resultado['fecha_emision'] = fecha_formato
            resultado['numero_autorizacion'] = factura_referencia.fel_firma
            resultado['motivo'] = self.fel_motivo
            resultado['no_origen'] = factura_referencia.fac_numero
            resultado['serie_origen'] = factura_referencia.fac_serie
            if self.regimen:
                if self.regimen == 'Actual':
                    resultado['regimen'] = "Regimen Actual(FEL)"
                else:
                    resultado['regimen'] = "Regimen Antiguo(FACE)"
        return resultado

    def get_detalle_factura(self):
        factura = {}
        factura_detalle = []
        decimal_price = self.env.ref('product.decimal_price').sudo().digits
        decimal_discount = self.env.ref('product.decimal_discount').sudo().digits

        total_total = total_base = total_impuestos  = total_descuento = total_sin_descuento = 0
        for detalle in self.invoice_line_ids:

            precio_sin_descuento = detalle.price_unit
            desc = (100-detalle.discount) / 100
            precio_con_descuento = precio_sin_descuento * desc

            

            # Lineas innecesarias
            # precio_sin_descuento = precio_sin_descuento
            # precio_con_descuento = precio_con_descuento

            # print("desc: ",desc)
            # print("descuento: ",detalle.discount)

            precio_con_descuento_x_cantidad = precio_con_descuento * detalle.quantity
            #precio_con_descuento_x_cantidad = float_is_zero(precio_con_descuento_x_cantidad, self.currency_id.rounding)
            
            precio_con_descuento_x_cantidad = float_round(precio_con_descuento_x_cantidad, precision_rounding=self.currency_id.rounding)
            
            descuento = (precio_sin_descuento * detalle.quantity) - ((precio_sin_descuento * desc) * detalle.quantity)
            descuento = round(descuento, decimal_discount)
            
            
            
            
            #print("precio_sin_descuento = %s | precio_con_descuento = %s | descuento = %s | precio_con_descuento_x_cantidad = %s" % 
            #      (precio_sin_descuento, precio_con_descuento, descuento,precio_con_descuento_x_cantidad))

            total_descuento += descuento
            total_linea_sin_descuento = precio_sin_descuento * detalle.quantity
            total_sin_descuento += total_linea_sin_descuento

            total_con_descuento = precio_con_descuento_x_cantidad
            total_linea_base = round(total_con_descuento / (self.sat_iva_porcentaje/100+1),6)
            total_linea_impuestos = round(total_linea_base * (self.sat_iva_porcentaje/100),6)

            total_total += precio_con_descuento_x_cantidad
            total_base += total_linea_base
            total_impuestos += total_linea_impuestos

            linea = {
            'precio_sin_descuento': precio_sin_descuento,
            'precio_con_descuento': precio_con_descuento,
            'descuento': descuento,
            'total_con_descuento': total_con_descuento,
            'total_linea_sin_descuento': total_linea_sin_descuento,
            'total_linea_base': total_linea_base,
            'total_linea_impuestos': total_linea_impuestos,
            'dato_linea': detalle,
            }

            # print("linea",linea)

            factura_detalle.append(linea)

        totales = {
            'total_sin_descuento': total_sin_descuento,
            'total_descuento': total_descuento,
            'total_total': total_total,
            'total_base': total_base,
            'total_impuestos': total_impuestos,
        }

        factura = {
            'detalle': factura_detalle,
            'totales': totales,
        }
        return factura

    def totales(self):
        total = {'gran_total':'','gran_subtotal':'','gran_total_total':'','gran_total_total_letras':'','moneda':self.currency_id.symbol}
        get_fac_doc = self.get_detalle_factura()
        tot = get_fac_doc['totales']
        total['gran_total'] = tot['total_sin_descuento']
        total['gran_subtotal'] = tot['total_descuento']
        total['gran_total_total'] = tot['total_total']
        enletras = letras
        cantidadenletras = enletras.to_word(total['gran_total_total'])
        if self.currency_id.name == 'USD':
            cantidadenletras = cantidadenletras.replace('QUETZALES','DOLARES')
        elif self.currency_id.name == 'EUR':
            cantidadenletras = cantidadenletras.resultado('QUETZALES','EUROS')
        total_letras = cantidadenletras
        total['gran_total_total_letras'] = total_letras
        return total

    def detalle_factura(self):
        lineas = []
        o = self
        get_fac_doc = self.get_detalle_factura()

        for linea_detalle in get_fac_doc['detalle']:
            l = linea_detalle['dato_linea']
            if l['price_total'] > 0 and l['quantity'] > 0:
                linea = {}
                linea['quantity'] = '{0:,.2f}'.format(l.quantity)
                linea['name'] = l.name
                linea['default_code'] = l.product_id.default_code
                linea['discount'] = '{0:,.2f}'.format(l.discount) 
                linea['price_unit'] =  linea_detalle['precio_sin_descuento']
                linea['price_total'] =  linea_detalle['total_linea_sin_descuento']

                linea['precio_sin_descuento']=  linea_detalle['precio_sin_descuento']
                linea['total_linea_sin_descuento']=  linea_detalle['total_linea_sin_descuento']
                
                linea['descuento']=  '{0:,.2f}'.format(linea_detalle['descuento'])
                linea['precio_con_descuento']=  linea_detalle['precio_con_descuento']
                linea['total_con_descuento']=  linea_detalle['total_con_descuento']
                lineas.append(linea)
            else:
                if l['display_type']:
                    linea = {}
                    linea['quantity'] = ''
                    linea['name'] = l.name
                    linea['discount'] = ''
                    linea['price_unit'] =  ''
                    linea['price_total'] =  ''
                    lineas.append(linea)
        return lineas

    def get_pos_formas_de_pago(self):
        facturas = self
        pedido = None
        for factura in facturas:
            pedido = self.env['pos.order'].search([('account_move','=',factura.id)])
        forma_pagos = []
        for pagos in pedido.payment_ids:
            pago = {
                'payment_method_id': pagos.payment_method_id,
                'importe': pagos.amount,
                'moneda': pagos.currency_id.id,
            }
            forma_pagos.append(pagos)
        return forma_pagos
            
        

    def action_invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        if any(not move.is_invoice(include_receipts=True) for move in self):
            raise UserError(_("Only invoices could be printed."))

        self.filtered(lambda inv: not inv.is_move_sent).write({'is_move_sent': True})

        if self.user_has_groups('account.group_account_invoice'):
            return self.env.ref('fel.reporte_factura').report_action(self)
        else:
            return self.env.ref('fel.reporte_factura').report_action(self)

class AccountMoveConfirmFEL(models.TransientModel):
    """
    Timbrar facturas en FEL
    """

    _name = "account.move.confirm.fel"
    _description = "Confirm the selected invoices in FEL"

    def invoice_confirm_fel(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for factura in self.env['account.move'].browse(active_ids):
            if factura.state in ['open'] and factura.journal_id.fel_setting_id and not factura.fel_firma:
                documento = factura.getListFactura()
                factura.firmar_factura(documento, True, False)

        return {'type': 'ir.actions.act_window_close'}