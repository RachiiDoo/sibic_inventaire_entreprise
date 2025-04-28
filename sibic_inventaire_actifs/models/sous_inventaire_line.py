from odoo import models, fields, api


class SousInventaireLine(models.Model):
    _name = "sibic.sous.inventaire.actifs.line"

    sous_inventaire_id = fields.Many2one(
        "sibic.sous.inventaire.actifs", string="Sous Inventaire"
    )

    # Cette fonction surcharge la méthode create du modèle Odoo (probablement sibic.sous.inventaire.actifs.line) pour préremplir automatiquement le champ found_location_id lorsqu'une ligne de sous-inventaire est créée.

    @api.model
    def create(self, vals):
        if "sous_inventaire_id" in vals:
            sous_inv = self.env["sibic.sous.inventaire.actifs"].browse(
                vals["sous_inventaire_id"]
            )
            if sous_inv.location_id:
                vals["found_location_id"] = sous_inv.location_id.id
        return super().create(vals)
