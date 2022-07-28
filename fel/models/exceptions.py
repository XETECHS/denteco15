

class InvalidOrderError(Exception):
    """

    """

    def __init__(self, message="Error en los datos de FEL en el documento.", document="", partner="", vat=""):
        self.document = document
        self.message = message
        self.partner = partner
        self.vat = vat
        super().__init__(self.message,self.document, self.partner, self.vat)

        def __str__(self):
            return self.message