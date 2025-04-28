from odoo import models, fields, api
from odoo.exceptions import UserError
import json


class SousInventaire(models.Model):
    _inherit = "sibic.sous.inventaire.actifs"

    asset_id_domain = fields.Char(compute="_compute_asset_id_domain", store=False)

    resultat_line_ids = fields.One2many(
        "sibic.sous.inventaire.actifs.line",
        "sous_inventaire_id",
        string="Lignes de résultat",
    )

    location_error_count = fields.Integer(string="Nombre d'erreurs d'emplacement")

    # La fonction qui calcule le nombre d'erreurs d'emplacement dans le sous inventaire

    @api.depends("resultat_line_ids.has_location_error")
    def _compute_location_error_count(self):
        for rec in self:
            rec.location_error_count = sum(
                1 for line in rec.resultat_line_ids if line.has_location_error
            )
    
    # La fonction qui filtre les assets tel que l'asset qui est deja dans le sous-inventaire ne s'affiche pas si on clique sur ajouter une ligne

    @api.depends("line_ids")
    def _compute_asset_id_domain(self):
        for record in self:
            domain = []
            if record.line_ids:
                # Récupérer tous les assets qui ne sont pas déjà utilisés dans d'autres lignes
                for line in record.line_ids:
                    domain.append(line.asset_id.id)

            domain = [("id", "not in", domain)]

            record.asset_id_domain = json.dumps(domain)
