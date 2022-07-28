from odoo import models, fields, api


class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = 'Product Brand'

    name = fields.Char('Nombre de Marca', required=True, translate=True)
    description = fields.Text('Descripcion', translate=True)
    partner_id = fields.Many2one(
        'res.partner',
        string='Contacto',
        help='Select a partner for this brand if it exists',
        ondelete='restrict'
    )
    logo = fields.Binary('Logo File')
    product_ids = fields.One2many(
        'product.template',
        'product_brand_id',
        string='Brand Products',
    )
    products_count = fields.Integer(
        string='Number of products',
        compute='_get_products_count',
    )
    visible_slider = fields.Boolean("Visible in Website", default=True)
    active = fields.Boolean("Active", default=True)

    @api.depends('product_ids')
    def _get_products_count(self):
        self.products_count = len(self.product_ids)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_brand_id = fields.Many2one(
        'product.brand',
        string='Marca',
        help='Select a brand for this product'
    )
