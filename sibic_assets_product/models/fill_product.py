from odoo import models, fields, _
from odoo.exceptions import UserError


class FillProduct(models.Model):
    _inherit = "account.move"

    def _auto_create_asset(self):
        create_list = []
        invoice_list = []
        auto_validate = []
        for move in self:
            if not move.is_invoice():
                continue

            for move_line in move.line_ids:
                if (
                    move_line.account_id
                    and (move_line.account_id.can_create_asset)
                    and move_line.account_id.create_asset != "no"
                    and not (move_line.currency_id or move.currency_id).is_zero(
                        move_line.price_total
                    )
                    and not move_line.asset_ids
                    and not move_line.tax_line_id
                    and move_line.price_total > 0
                    and not (
                        move.move_type in ("out_invoice", "out_refund")
                        and move_line.account_id.internal_group == "asset"
                    )
                ):
                    if not move_line.name:
                        raise UserError(
                            _(
                                "Journal Items of %(account)s should have a label in order to generate an asset",
                                account=move_line.account_id.display_name,
                            )
                        )
                    if move_line.account_id.multiple_assets_per_line:
                        # decimal quantities are not supported, quantities are rounded to the lower int
                        units_quantity = max(1, int(move_line.quantity))
                    else:
                        units_quantity = 1
                    vals = {
                        "name": move_line.name,
                        "company_id": move_line.company_id.id,
                        "currency_id": move_line.company_currency_id.id,
                        "analytic_distribution": move_line.analytic_distribution,
                        "original_move_line_ids": [(6, False, move_line.ids)],
                        "state": "draft",
                        "acquisition_date": (
                            move.invoice_date
                            if not move.reversed_entry_id
                            else move.reversed_entry_id.invoice_date
                        ),
                        "product_id": move_line.product_id.id,
                    }
                    model_id = move_line.account_id.asset_model
                    if model_id:
                        vals.update(
                            {
                                "model_id": model_id.id,
                            }
                        )
                    auto_validate.extend(
                        [move_line.account_id.create_asset == "validate"]
                        * units_quantity
                    )
                    invoice_list.extend([move] * units_quantity)
                    for i in range(1, units_quantity + 1):
                        if units_quantity > 1:
                            vals["name"] = move_line.name + _(
                                " (%s of %s)", i, units_quantity
                            )
                        create_list.extend([vals.copy()])

        assets = self.env["account.asset"].with_context({}).create(create_list)
        for asset, vals, invoice, validate in zip(
            assets, create_list, invoice_list, auto_validate
        ):
            if "model_id" in vals:
                asset._onchange_model_id()
                if validate:
                    asset.validate()
            if invoice:
                asset.message_post(
                    body=_("Asset created from invoice: %s", invoice._get_html_link())
                )
                asset._post_non_deductible_tax_value()
        return assets

    # def asset_create(self):
    #     """Create function for the asset and its associated properties"""
    #     for record in self:
    #         if record.asset_category_id:
    #             vals = {
    #                 "name": record.name,
    #                 "code": record.move_id.name or False,
    #                 "category_id": record.asset_category_id.id,
    #                 "value": record.price_subtotal,
    #                 "partner_id": record.partner_id.id,
    #                 "company_id": record.move_id.company_id.id,
    #                 "currency_id": record.move_id.company_currency_id.id,
    #                 "date": record.move_id.invoice_date,
    #                 "invoice_id": record.move_id.id,
    #                 "product_id": record.product_id.id,
    #             }
    #             changed_vals = record.env["account.asset"].onchange_category_id_values(
    #                 vals["category_id"]
    #             )
    #             vals.update(changed_vals["value"])
    #             asset = record.env["account.asset"].create(vals)
    #             if record.asset_category_id.open_asset:
    #                 asset.validate()
    #     return True
