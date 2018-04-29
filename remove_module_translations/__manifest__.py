# -*- coding: utf-8 -*-
# Copyright 2018 TRESCLOUD Cia Ltda.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html
{
    'name': "Remove Translations",
    'version': '1.0',
    'depends': ['base'],
    'author': "TRESCLOUD Cia Ltda.",
    'category': 'Technical',
    'description': """
    Provides a wizard to force the removal of translations created by Odoo modules (example menu's translations), after 
    removing the translations you can upgrade the 'base' module to update all translation terms.
    
    This is usefull as sometimes Odoo gets stuck on upgrading the translation terms.
    """,
    'data': [
        'wizards/reset_translations_wizard_view.xml'
    ],
}