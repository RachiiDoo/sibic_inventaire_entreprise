from odoo import models, fields, api


class RelocateAssetsWizard(models.TransientModel):
    _name = "relocate.assets.wizard"
    _description = "Assistant de relocalisation des actifs"

    new_location_id = fields.Many2one(
        "stock.location",
        string="Nouvel Emplaçement",
        required=True,
        domain=[("usage", "=", "internal")],
    )
    line_ids = fields.Many2many(
        "sibic.sous.inventaire.actifs.line", string="Lignes Selectionnées"
    )

    def action_apply_relocation(self):
        for line in self.line_ids:
            line.location_id = self.new_location_id
            line._compute_location_error()

        remaining_errors = self.line_ids.filtered(lambda l: l.has_location_error)

        if not remaining_errors:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Félicitations 🎉",
                    "message": "Vous avez corrigé toutes les erreurs d'emplacement.",
                    "type": "success",
                    "sticky": False,
                    "next": {"type": "ir.actions.act_window_close"},
                },
            }

        return {"type": "ir.actions.act_window_close"}
