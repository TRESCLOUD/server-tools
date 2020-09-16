# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Let's encrypt",
    "version": "14.0.1.0.0",
    "author": "Therp BV,"
              "Tecnativa,"
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Hidden/Dependency",
    "summary": "Request SSL certificates from letsencrypt.org",
    "depends": [
        'base',
    ],
    "data": [
        "data/ir_config_parameter.xml",
        # TODO: Revisar problema al insertar data a ir.cron
        # en base de datos limpia
        #"data/ir_cron.xml",
        #"demo/ir_cron.xml",
        # Views
        "views/res_company_view.xml",
    ],
    "post_init_hook": 'post_init_hook',
    'installable': True,
    "external_dependencies": {
        'bin': [
            'openssl',
        ],
        'python': [
            'acme_tiny',
            'IPy',
        ],
    },
}
