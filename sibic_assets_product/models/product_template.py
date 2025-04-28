from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    asset_ids = fields.One2many("account.asset", "product_id", string="Actifs liés")
