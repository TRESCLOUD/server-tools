# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Fusionador de objetos',
    'version': '1.1',
    'category': 'Tools',
    'description': '''       
        Functionality:
            This Module will give you the possibility to merge 2 or more objects:
            Example: You want to merge 2 partners, select the Partner to merge, then which one to keep.
            All SO, PO, Invoices, Pickings, products, etc. of selected partner will be add to the one to keep.
        
        Authors:
            Ing. Andres Calle
            Ing. Patricio Rangles
            Ing. José Miguel Rivero
            Ing. Santiago Orozco        
    ''',
    'author': 'TRESCLOUD CIA LTDA',
    'maintainer': 'TRESCLOUD CIA. LTDA.',
    'website': 'http://www.trescloud.com',
    'depends': [
        'base'
    ],    
    'data': [
        #Wizard
        'wizard/object_merger_view.xml',
        #Views
        'views/res_config_settings_view.xml'
    ],
    'installable': True
}
