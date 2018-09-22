# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Module installation Control',
    'version': '1.0',
    'category': 'Reporting',
    'description': '''
        This modulo allow to control the installation of modules using the admin password:
        Autors:
            - Patricio Rangles
    ''',
    'author': 'TRESCLOUD CIA LTDA',
    'maintainer': 'TRESCLOUD CIA. LTDA.',
    'website': 'http://www.trescloud.com',
    'license': 'AGPL-3',
    'depends': [
        'base'
    ],
    'data': [
        #Views
        'views/base_module_immediate_install.xml',
        'views/module_view.xml',
        #Wizard
        'wizard/wizard_allow_module_modification_view.xml'
    ],
    'installable': True
}
