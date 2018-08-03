# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Verify email at signup",
    "summary": "Force uninvited users to use a good email for signup",
    "version": "10.0.2.0.0",
    "category": "Authentication",
    "website": "http://github.com/OCA/server-tools",
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    'installable': True,
    "external_dependencies": {
        "python": [
            "lxml", #Esta lib se debe instalar con pip: sudo pip install lxml
            "validate_email", #Esta lib se debe instalar con pip: sudo pip install validate_email
        ],
    },
    "depends": [
        "auth_signup",
    ],
    "data": [
        "views/signup.xml",
    ],
}
