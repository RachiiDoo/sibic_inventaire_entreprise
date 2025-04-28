from odoo import models


class SousInventaireActifs(models.Model):
    _inherit = "sibic.sous.inventaire.actifs"

    def action_voir_resultat(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Résultats de l'Inventaire",
            "res_model": "sibic.sous.inventaire.actifs.line",
            "view_mode": "tree,form",
            "domain": [("sous_inventaire_id", "=", self.id)],
            "context": {"default_sous_inventaire_id": self.id},
            "target": "current",
        }
