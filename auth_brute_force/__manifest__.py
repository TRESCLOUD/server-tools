# -*- coding: utf-8 -*-
# Copyright 2015 GRAP - Sylvain LE GAL
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Authentification - Brute-Force Filter',
    'version': '10.0.2.2.0',
    'category': 'Tools',
    'summary': "Track Authentication Attempts and Prevent Brute-force Attacks",
    'author': "GRAP, "
              "Tecnativa, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/server-tools',
    'license': 'AGPL-3',
    'depends': [
        # If we don't depend on it, it would inhibit this addon
        "auth_crypt",
        # DEPENDENCIA AGREGADA POR TRESCLOUD
        # Se neceita mejorar el mensaje cuando no se puede restablecer la
        # contraseña debido a que el usuario esta baneado
        "auth_signup",
    ],
    'data': [
        'security/ir_model_access.yml',
        'views/view.xml',
        'views/action.xml',
        'views/menu.xml',
    ],
    'installable': True,
}
