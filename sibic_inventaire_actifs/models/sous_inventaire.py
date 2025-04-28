from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import json


class SousInventaire(models.Model):
    _name = "sibic.sous.inventaire.actifs"
    _description = "Sous Inventaire"

    reference = fields.Char(string="Référence", required=True, default="Nouveau")
    begin_date = fields.Date(string="Date début", required=True)
    end_date = fields.Date(string="Date fin", required=True)
    location_id = fields.Many2one("stock.location", required=True, tracking=True)
    state = fields.Selection(
        [
            ("draft", "Brouillon"),
            ("in_progress", "En Cours"),
            ("done", "Terminé"),
            ("closed", "Cloturé"),
        ],
        string="Etat",
        default="draft",
    )

    _rec_name = "reference"

    team_id = fields.Many2one("equipe.inventaire", string="Equipe", required=True)
    global_inventory_id = fields.Many2one(
        "inventaire.global.actifs", string="Inventaire globale", required=True
    )
    validation_commission = fields.Many2one(
        "equipe.inventaire", string="Commission de validation", required=True
    )

    line_ids = fields.One2many(
        "sibic.sous.inventaire.actifs.line", "sous_inventaire_id", string="Lignes"
    )

    # Les fonctions pour changer les etats des sous inventaires

    def action_start(self):
        for rec in self:
            rec.state = "in_progress"

    def action_done(self):
        for rec in self:
            rec.state = "done"

    def action_closed(self):
        for rec in self:
            rec.state = "closed"

    def action_reset(self):
        for rec in self:
            rec.state = "draft"

    # Contrainte des dates début et fin

    @api.constrains("begin_date", "end_date")
    def _check_dates(self):
        for record in self:
            if record.global_inventory_id:
                inventaire_global = record.global_inventory_id

                if (
                    record.begin_date
                    and record.begin_date < inventaire_global.begin_date
                ):
                    raise ValidationError(
                        "La date de début du sous-inventaire ne peut pas être avant la date de début de l'inventaire global."
                    )
                if record.end_date and record.end_date > inventaire_global.end_date:
                    raise ValidationError(
                        "La date de fin du sous-inventaire ne peut pas être après la date de fin de l'inventaire global."
                    )

                if (
                    record.begin_date
                    and record.end_date
                    and record.begin_date > record.end_date
                ):
                    raise ValidationError(
                        "La date de fin ne peut pas être avant la date de début."
                    )

    # La reference des sous inventaire doit etre remplis automatiquement

    @api.model
    def create(self, vals):
        if vals.get("global_inventory_id"):
            global_inv = self.env["inventaire.global.actifs"].browse(
                vals["global_inventory_id"]
            )
            if global_inv.reference:
                # Compter combien de sous-inventaires existent déjà pour cet inventaire global
                existing_count = self.search_count(
                    [("global_inventory_id", "=", global_inv.id)]
                )
                # Générer la nouvelle référence
                vals["reference"] = f"{global_inv.reference}/{existing_count + 1}"
        return super(SousInventaire, self).create(vals)

    # Controle du suppression d'un inventaire

    def unlink(self):
        for record in self:
            if record.state != "draft":
                raise UserError(
                    "Vous ne pouvez supprimer un inventaire que s'il est en brouillon (Draft)."
                )
            if record.line_ids:
                raise UserError(
                    "Impossible de supprimer : l'inventaire contient des lignes d'actifs."
                )
        return super(SousInventaire, self).unlink()
