{
    "name": "Sibic Product Assets",
    "version": "1.0",
    "summary": 'Ajouter un nouveau onglet "Actifs" dans la form produit',
    "author": "Rachid Benrabia",
    "depends": [
        "base",
        "product",
        "account_asset",
        # "base_accounting_kit",
        "sibic_inventaire_actifs",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_template_view.xml",
        "views/account_asset_view.xml",
        "views/sous_inventaire_resultats_views.xml",
        "views/sous_inventaire_view.xml",
        # "views/transfert_location.xml",
        "views/relocate_assets_wizard_view.xml",
    ],
    "installable": True,
    "application": True,
}
