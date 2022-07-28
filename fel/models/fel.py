import base64
from lxml import etree
import json
import requests #pip3 install requests
from datetime import timedelta, datetime

NSMAP = {
    "ds": "http://www.w3.org/2000/09/xmldsig#",
    "dte": "http://www.sat.gob.gt/dte/fel/0.2.0",
}

NSMAP_REF = {
    "cno": "http://www.sat.gob.gt/face2/ComplementoReferenciaNota/0.1.0",
}

NSMAP_ABONO = {
    "cfc": "http://www.sat.gob.gt/dte/fel/CompCambiaria/0.1.0",
}

NSMAP_EXP = {
    "cex": "http://www.sat.gob.gt/face2/ComplementoExportaciones/0.1.0",
}

NSMAP_FE = {
    "cfe": "http://www.sat.gob.gt/face2/ComplementoFacturaEspecial/0.1.0",
}

DTE_NS = "{http://www.sat.gob.gt/dte/fel/0.2.0}"
DS_NS = "{http://www.w3.org/2000/09/xmldsig#}"
CNO_NS = "{http://www.sat.gob.gt/face2/ComplementoReferenciaNota/0.1.0}"
CFE_NS = "{http://www.sat.gob.gt/face2/ComplementoFacturaEspecial/0.1.0}"
CEX_NS = "{http://www.sat.gob.gt/face2/ComplementoExportaciones/0.1.0}"
CFC_NS = "{http://www.sat.gob.gt/dte/fel/CompCambiaria/0.1.0}"

class Fel():

    def __init__(self):
        self.xmls = ''
        self.xmls_base64 = ''
        self.UrlFirma = ''
        self.llave_firma = ''
        self.alias_pfx = ''
        self.correo_copia = ''
        self.xml_firmado = ''
        self.factura_id = ''

    def setDatosConexion(self, llave_firma, clave, alias_pfx, codigo, correo_copia, factura_id):
        self.UrlFirma = 'https://signer-emisores.feel.com.gt/sign_solicitud_firmas/firma_xml'
        self.llave_firma = llave_firma
        self.clave = clave
        self.alias_pfx = alias_pfx
        self.codigo = codigo
        self.correo_copia = correo_copia
        self.factura_id = factura_id

    def getXmlFormat(self, documento):
        d = documento
        schemaLocation = etree.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")
        # TODO: ELIMINAR LAS SIGUIENTES LINEAS
        tmp_date = d["FechaHoraEmision"].replace('T', ' ')
        date_time_obj = datetime.strptime(tmp_date, '%Y-%m-%d %H:%M:%S')
        new_date = date_time_obj + timedelta(0.9)
        d["FechaHoraEmision"] = new_date.strftime('%Y-%m-%dT%H:%M:%S')
        # ----------------------------------------------

        GTDocumento = etree.Element(DTE_NS+"GTDocumento", {schemaLocation: "http://www.sat.gob.gt/dte/fel/0.2.0"}, Version="0.1", nsmap=NSMAP)
        SAT = etree.SubElement(GTDocumento, DTE_NS+"SAT", ClaseDocumento="dte")
        DTE = etree.SubElement(SAT, DTE_NS+"DTE", ID="DatosCertificados")
        DatosEmision = etree.SubElement(DTE, DTE_NS+"DatosEmision", ID="DatosEmision")

        DatosGenerales = etree.SubElement(DatosEmision, DTE_NS+"DatosGenerales", CodigoMoneda=d["CodigoMoneda"], FechaHoraEmision=d["FechaHoraEmision"], Tipo=d["Tipo"])
        Emisor = etree.SubElement(DatosEmision, DTE_NS+"Emisor", AfiliacionIVA=d["AfiliacionIVA"], CodigoEstablecimiento=d["CodigoEstablecimiento"], CorreoEmisor=d["ECorreoEmisor"], NITEmisor=d["NITEmisor"], NombreComercial=d["NombreComercial"], NombreEmisor=d["ENombreEmisor"])
        DireccionEmisor = etree.SubElement(Emisor, DTE_NS+"DireccionEmisor")
        Direccion = etree.SubElement(DireccionEmisor, DTE_NS+"Direccion")
        Direccion.text = d["EDireccionEmisor"]
        CodigoPostal = etree.SubElement(DireccionEmisor, DTE_NS+"CodigoPostal")
        CodigoPostal.text = d["ECodigoPostal"]
        Municipio = etree.SubElement(DireccionEmisor, DTE_NS+"Municipio")
        Municipio.text = d["EMunicipio"]
        Departamento = etree.SubElement(DireccionEmisor, DTE_NS+"Departamento")
        Departamento.text = d["EDepartamento"]
        Pais = etree.SubElement(DireccionEmisor, DTE_NS+"Pais")
        Pais.text = d["EPais"]

        #Receptor
        Receptor = etree.SubElement(DatosEmision, DTE_NS+"Receptor", IDReceptor=d["IDReceptor"], NombreReceptor=d["NombreReceptor"])
        Receptor.attrib['CorreoReceptor'] = d["CorreoReceptor"]
        if "TipoEspecial" in d:
            Receptor.attrib['TipoEspecial'] = d["TipoEspecial"]
        DireccionReceptor = etree.SubElement(Receptor, DTE_NS+"DireccionReceptor")
        Direccion = etree.SubElement(DireccionReceptor, DTE_NS+"Direccion")
        Direccion.text = d["ReceptorDireccion"]
        CodigoPostal = etree.SubElement(DireccionReceptor, DTE_NS+"CodigoPostal")
        CodigoPostal.text = d["ReceptorCodigoPostal"]
        Municipio = etree.SubElement(DireccionReceptor, DTE_NS+"Municipio")
        Municipio.text = d["ReceptorMunicipio"]
        Departamento = etree.SubElement(DireccionReceptor, DTE_NS+"Departamento")
        Departamento.text = d["ReceptorDepartamento"]
        Pais = etree.SubElement(DireccionReceptor, DTE_NS+"Pais")
        Pais.text = d["ReceptorPais"]

        #Frases
        if "Frases" in d:
            Frases = etree.SubElement(DatosEmision, DTE_NS+"Frases")
            for frase in d["Frases"]:
                Frase = etree.SubElement(Frases, DTE_NS+"Frase", CodigoEscenario=frase["CodigoEscenario"], TipoFrase=frase["TipoFrase"])

        #Items
        Items = etree.SubElement(DatosEmision, DTE_NS+"Items")
        NumeroLinea = 0
        for item in d["Items"]:
            NumeroLinea += 1
            Item = etree.SubElement(Items, DTE_NS+"Item", BienOServicio=item["BienOServicio"], NumeroLinea=str(NumeroLinea))
            Cantidad = etree.SubElement(Item, DTE_NS+"Cantidad")
            Cantidad.text = str(item["Cantidad"])
            UnidadMedida = etree.SubElement(Item, DTE_NS+"UnidadMedida")
            UnidadMedida.text = item["UnidadMedida"][0:3]
            Descripcion = etree.SubElement(Item, DTE_NS+"Descripcion")
            Descripcion.text = item["Descripcion"]
            PrecioUnitario = etree.SubElement(Item, DTE_NS+"PrecioUnitario")
            PrecioUnitario.text = item["PrecioUnitario"]
            Precio = etree.SubElement(Item, DTE_NS+"Precio")
            Precio.text = item["Precio"]
            Descuento = etree.SubElement(Item, DTE_NS+"Descuento")
            Descuento.text = item["Descuento"]

            #Impuestos
            if "NombreCorto" in item:
                Impuestos = etree.SubElement(Item, DTE_NS+"Impuestos")
                Impuesto = etree.SubElement(Impuestos, DTE_NS+"Impuesto")
                NombreCorto = etree.SubElement(Impuesto, DTE_NS+"NombreCorto")
                NombreCorto.text = item["NombreCorto"]
                CodigoUnidadGravable = etree.SubElement(Impuesto, DTE_NS+"CodigoUnidadGravable")
                CodigoUnidadGravable.text = item["CodigoUnidadGravable"]
                MontoGravable = etree.SubElement(Impuesto, DTE_NS+"MontoGravable")
                MontoGravable.text = item["MontoGravable"]
                MontoImpuesto = etree.SubElement(Impuesto, DTE_NS+"MontoImpuesto")
                MontoImpuesto.text = item["MontoImpuesto"]
            Total = etree.SubElement(Item, DTE_NS+"Total")
            Total.text = item["Total"]

        Totales = etree.SubElement(DatosEmision, DTE_NS+"Totales")
        if d["Tipo"] not in ['NABN']:
            TotalImpuestos = etree.SubElement(Totales, DTE_NS+"TotalImpuestos")
            TotalImpuesto = etree.SubElement(TotalImpuestos, DTE_NS+"TotalImpuesto", NombreCorto="IVA", TotalMontoImpuesto=d["TotalMontoImpuesto"])
        GranTotal = etree.SubElement(Totales, DTE_NS+"GranTotal")
        GranTotal.text = d["GranTotal"]

        Adenda = etree.SubElement(SAT, DTE_NS+"Adenda")
        NumeroInterno = etree.SubElement(Adenda, DTE_NS+"NumeroInterno")
        NumeroInterno.text = d["Adenda"]

        if d["Complementos"]:
            Complementos = etree.SubElement(DatosEmision, DTE_NS+"Complementos")
            if d["Tipo"] in ['NDEB', 'NCRE']:
                Complemento = etree.SubElement(Complementos, DTE_NS+"Complemento", IDComplemento="ReferenciasNota", NombreComplemento="GT_Complemento_Referencia_Nota-0.1.0", URIComplemento="GT_Complemento_Referencia_Nota-0.1.0.xsd")
                if d["RegimenAntiguo"] == "Actual":
                    ReferenciasNota = etree.SubElement(Complemento, CNO_NS+"ReferenciasNota",
                        FechaEmisionDocumentoOrigen = d["FechaEmisionDocumentoOrigen"],
                        MotivoAjuste = d["MotivoAjuste"],
                        NumeroAutorizacionDocumentoOrigen = d["NumeroAutorizacionDocumentoOrigen"],
                        NumeroDocumentoOrigen = d["NumeroDocumentoOrigen"],
                        SerieDocumentoOrigen = d["SerieDocumentoOrigen"],
                        Version="0.0", nsmap=NSMAP_REF)
                else:
                    ReferenciasNota = etree.SubElement(Complemento, CNO_NS+"ReferenciasNota",
                        RegimenAntiguo="Antiguo",
                        FechaEmisionDocumentoOrigen = d["FechaEmisionDocumentoOrigen"],
                        MotivoAjuste = d["MotivoAjuste"],
                        NumeroAutorizacionDocumentoOrigen = d["NumeroAutorizacionDocumentoOrigen"],
                        NumeroDocumentoOrigen = d["NumeroDocumentoOrigen"],
                        SerieDocumentoOrigen = d["SerieDocumentoOrigen"],
                        Version="0.0", nsmap=NSMAP_REF)

            #Factura Cambiaria
            elif d["Tipo"] in ['FCAM']:
                Complemento = etree.SubElement(Complementos, DTE_NS+"Complemento", IDComplemento="FCAM", NombreComplemento="GT_Complemento_Cambiaria-0.1.0", URIComplemento="GT_Complemento_Cambiaria-0.1.0.xsd")
                AbonosFacturaCambiaria = etree.SubElement(Complemento, CFC_NS+"AbonosFacturaCambiaria", Version="1", nsmap=NSMAP_ABONO)
                Abono = etree.SubElement(AbonosFacturaCambiaria, CFC_NS+"Abono")
                NumeroAbono = etree.SubElement(Abono, CFC_NS+"NumeroAbono")
                NumeroAbono.text = d["FCAM_NumeroAbono"]
                FechaVencimiento = etree.SubElement(Abono, CFC_NS+"FechaVencimiento")
                FechaVencimiento.text = d["FCAM_FechaVencimiento"]
                MontoAbono = etree.SubElement(Abono, CFC_NS+"MontoAbono")
                MontoAbono.text = d["FCAM_MontoAbono"]

            #Factura Especial
            elif d["Tipo"] in ['FESP']:
                Complemento = etree.SubElement(Complementos, DTE_NS+"Complemento", IDComplemento="FESP", NombreComplemento="GT_Complemento_Fac_Especial", URIComplemento="GT_Complemento_Fac_Especial.xsd")
                RetencionesFacturaEspecial = etree.SubElement(Complemento, CFE_NS+"RetencionesFacturaEspecial", Version="1", nsmap=NSMAP_FE)
                RetencionISR = etree.SubElement(RetencionesFacturaEspecial, CFE_NS+"RetencionISR")
                RetencionISR.text = d["FESP_RetencionISR"]
                RetencionIVA = etree.SubElement(RetencionesFacturaEspecial, CFE_NS+"RetencionIVA")
                RetencionIVA.text = d["FESP_RetencionIVA"]
                TotalMenosRetenciones = etree.SubElement(RetencionesFacturaEspecial, CFE_NS+"TotalMenosRetenciones")
                TotalMenosRetenciones.text = d["FESP_TotalMenosRetenciones"]




        xmls = etree.tostring(GTDocumento, encoding="UTF-8")
        print(xmls)
        self.xmls = xmls.decode("utf-8").replace("&amp;", "&").encode("utf-8")
        self.xmls_base64 = base64.b64encode(xmls)
        self.xmls_file = etree.tostring(GTDocumento, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        print(self.xmls_file)
        print(self.xmls)

    def firmar_xml(self, anulacion):
        es_anulacion = anulacion
        headers = { "Content-Type": "application/json" }
        data = {
            "llave": self.llave_firma,
            "archivo": self.xmls_base64.decode("utf-8"),
            "codigo": self.factura_id,
            "alias": self.alias_pfx,
            "es_anulacion": "S" if anulacion else "N"
        }

        r = requests.post(url = self.UrlFirma, json = data, headers=headers)

        self.xmls_file_firmado = r.text

        self.xml_firmado =  json.loads(r.text)
        print("XML: ", self.xmls_file_firmado)

        return self.xml_firmado

    def certificar_xml(self, anulacion):
        UrlFirma = 'https://certificador.feel.com.gt/fel/certificacion/v2/dte/'
        if (anulacion):
            UrlFirma = 'https://certificador.feel.com.gt/fel/anulacion/v2/dte'
        
        data = {
            "nit_emisor" : self.codigo,
            "correo_copia": self.correo_copia,
            "xml_dte": self.xml_firmado["archivo"],
        }

        headers = {
            'usuario': self.alias_pfx ,
            'llave': self.clave,
            'identificador': self.factura_id,
            'Content-Type': 'application/json',
        }
        r = requests.post(url = UrlFirma, json=data, headers = headers)
        fel_certificacion_response =  json.loads(r.text)
        self.xmls_file_certificado = r.text

        return fel_certificacion_response

    def anular(self, documento):
        d = documento
        schemaLocation = etree.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")

        NSMAP = {
            "ds": "http://www.w3.org/2000/09/xmldsig#",
            "dte": "http://www.sat.gob.gt/dte/fel/0.1.0",
        }
        DTE_NS = "{http://www.sat.gob.gt/dte/fel/0.1.0}"

        GTDocumento = etree.Element(DTE_NS+"GTDocumento", {schemaLocation: "http://www.sat.gob.gt/dte/fel/0.1.0"}, Version="0.1", nsmap=NSMAP)
        GTAnulacionDocumento = etree.Element(DTE_NS+"GTAnulacionDocumento", {}, Version="0.1", nsmap=NSMAP)
        SAT = etree.SubElement(GTAnulacionDocumento, DTE_NS+"SAT")
        AnulacionDTE = etree.SubElement(SAT, DTE_NS+"AnulacionDTE", ID="DatosCertificados")
        DatosGenerales = etree.SubElement(AnulacionDTE, DTE_NS+"DatosGenerales",
                        FechaHoraAnulacion=d["FechaHoraAnulacion"],
                        ID=d["DatosAnulacion"],
                        NITEmisor=d["NITEmisor"],
                        FechaEmisionDocumentoAnular=d["FechaEmisionDocumentoAnular"],
                        IDReceptor=d["IDReceptor"],
                        NumeroDocumentoAAnular=d["NumeroDocumentoAAnular"],
                        MotivoAnulacion=d["MotivoAnulacion"])
        #xmls = etree.tostring(GTAnulacionDocumento, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        xmls = etree.tostring(GTAnulacionDocumento, encoding="UTF-8")
        self.xmls = xmls.decode("utf-8").replace("&amp;", "&").encode("utf-8")
        self.xmls_base64 = base64.b64encode(xmls)
        self.xmls_file = etree.tostring(GTAnulacionDocumento, pretty_print=True, xml_declaration=True, encoding='UTF-8')
