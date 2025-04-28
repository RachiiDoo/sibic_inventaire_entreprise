from odoo import models, fields, api
import json


class FillAsset(models.Model):
    _inherit = "sibic.sous.inventaire.actifs.line"
    _rec_name = "asset_code"

    _sql_constraints = [
        (
            "unique_asset_per_sous_inventaire",
            "unique(sous_inventaire_id, asset_id)",
            "Un asset ne peut être ajouté qu'une seule fois dans un même sous-inventaire.",
        ),
    ]

    asset_id = fields.Many2one(
        "account.asset",
        string="Immobilisation",
    )

    asset_code = fields.Char(string="Réference", related="asset_id.code")

    product_id = fields.Many2one(
        "product.product", string="Produit", related="asset_id.product_id"
    )

    location_id = fields.Many2one(
        "stock.location",
        string="Emplacement",
        related="asset_id.location_id",
        readonly=False,
        domain=[("usage", "=", "internal")],
    )

    asset_id_domain = fields.Char(related="sous_inventaire_id.asset_id_domain")

    found_location_id = fields.Many2one("stock.location", string="Emplacement trouvé")

    has_location_error = fields.Boolean(
        string="Erreur d'emplacement", compute="_compute_location_error", store=True
    )

    location_error_count = fields.Integer(
        string="Nombre d'erreurs d'emplacement",
        related="sous_inventaire_id.location_error_count",
        readonly=True,
        store=True,
    )

    @api.depends("found_location_id", "location_id")
    def _compute_location_error(self):
        for line in self:
            if not line.found_location_id or line.found_location_id != line.location_id:
                line.has_location_error = True
            else:
                line.has_location_error = False

    def action_open_relocate_wizard(self):
        return {
            "name": "Relocation",
            "type": "ir.actions.act_window",
            "res_model": "relocate.assets.wizard",
            "view_mode": "form",
            "target": "new",
            "context": "{'default_line_ids': active_ids}",
        }
