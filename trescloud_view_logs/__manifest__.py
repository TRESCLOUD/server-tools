# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Trescloud View logs",
    "version": "15.0.1.0.0",
    "author": "Trescloud Cia. Ltda., Patricio Rangles",
    "website": "www.trescloud.com",
    "license": "AGPL-3",
    "category": "Tools",
    "summary": "Visualizacion de logs de Odoo",
    "depends": ["base_setup"],
    'data': [
        #Security
        'security/ir.model.access.csv',
        #Views
        'views/res_company_view.xml',
        #Wizard
        'wizard/wizard_view_logs_view.xml',
    ],
    "demo": [],
    "installable": True,
    "external_dependencies": {
        "python": ['file_read_backwards']
    },
}
