from odoo import models, fields


class EquipeInventaire(models.Model):
    _name = "equipe.inventaire"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    _description = "Team"  # Optional: Description of the model

    # Define the fields
    name = fields.Char(string="Nom", required=True)  # Team name

    chef_d_equipe = fields.Many2one("res.users", string="Chef d'équipe", required=True)

    membres = fields.Many2many(
        "res.users",
        string="Membres",
        required=True,
        domain=lambda self: [
            (
                "groups_id",
                "in",
                [
                    self.env.ref("sibic_inventaire_actifs.group_inventaire_admin").id,
                    self.env.ref("sibic_inventaire_actifs.group_inventaire_user").id,
                ],
            )
        ],
    )

    note = fields.Html(string="Note")  # HTML field for notes

    team_type = fields.Selection(
        [
            ("consolidation", "Consolidation"),
            ("comptage", "Comptage"),
            ("validation", "Validation"),
        ]
    )
