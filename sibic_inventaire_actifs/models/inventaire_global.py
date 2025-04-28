from odoo import models, fields, api
from datetime import date
from odoo.exceptions import UserError, ValidationError


class InventaireGlobal(models.Model):
    _name = "inventaire.global.actifs"
    _description = "Inventaire global"

    reference = fields.Char(string="Référence", required=True, default="Nouveau")
    begin_date = fields.Date(string="Date début")
    end_date = fields.Date(string="Date fin")
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
    line_ids = fields.One2many(
        "sibic.sous.inventaire.actifs", "global_inventory_id", string="Sous inventaire"
    )

    _rec_name = "reference"

    # Les fonctions pour changer les etats des sous inventaires

    def action_start(self):
        for rec in self:
            rec.state = "in_progress"
            if not rec.begin_date:
                rec.begin_date = date.today()

    def action_done(self):
        for rec in self:
            rec.state = "done"
            if not rec.end_date:
                rec.end_date = date.today()

    def action_closed(self):
        for rec in self:
            rec.state = "closed"

    def action_reset(self):
        for rec in self:
            rec.state = "draft"
            rec.begin_date = False
            rec.end_date = False

    # Cette fonction utilise les sequences d'odoo pour creer la reference du l'inventaire globale automatiquement

    @api.model
    def create(self, vals):
        if "reference" not in vals or not vals["reference"]:
            vals["reference"] = (
                self.env["ir.sequence"].next_by_code("inventaire.global.actifs") or "/"
            )
        return super(InventaireGlobal, self).create(vals)

    # Controle de suppression des inventaires

    def unlink(self):
        for record in self:
            if record.state != "draft":
                raise UserError(
                    "Vous ne pouvez supprimer un inventaire que s'il est en brouillon (Draft)."
                )

            if record.line_ids:
                raise UserError(
                    "Impossible de supprimer : l'inventaire contient des sous inventaire."
                )
        return super(InventaireGlobal, self).unlink()
