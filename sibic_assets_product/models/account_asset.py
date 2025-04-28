from odoo import models, fields, api
from odoo.osv import expression
from odoo.exceptions import ValidationError


class AccountAsset(models.Model):
    _inherit = "account.asset"

    _rec_names_search = ["code"]

    code = fields.Char(string="Code")

    product_id = fields.Many2one("product.product", string="Produit")

    location_id = fields.Many2one(
        "stock.location",
        string="Emplacement",
        domain=[("usage", "=", "internal")],
    )

    # La fonction qui fait la recherche uniquement sur le champ code, et que cette recherche soit exacte (=), et non floue (ilike).

    @api.model
    def _name_search(self, name, domain=None, operator="ilike", limit=None, order=None):
        domain = domain or []
        if name:
            domain = expression.AND(
                [
                    domain,
                    [("code", "=", name)],
                ]
            )
        return self._search(domain, limit=limit, order=order)

    # Contrainte pour que le produit et l'emplacement sont obligatoires dans l'immobilisation

    @api.constrains(product_id, location_id)
    def _check_required_fields(self):
        for record in self:
            if (
                record.product_id is None
                or record.location_id is None
                or record.code in None
                and record.state == "model"
            ):
                raise ValidationError(
                    "Produit et Emplacement sont obligatoires pour une immobilisation."
                )
