# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Odoo Cloc',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'Backport of native cloc tool for version 10.0 from Odoo version 16.0',
    'description': """

This module allow to count the line of extra module the same way odoo cloc do it in version > 12.0 and send the information in update_msg

- Allow get this information and submit to other analysis tool using web services

- Add categorization using repository and module level. If a module is not categorized automatically is set to "Personalizado" category
  
  Repositories not categorized in csv file:
  -- Repo-Venezuela (Client modules)
  -- enterprise (Odoo)
  -- odoo (Odoo)
  -- odoo-clientes-especificos (Client modules)
  -- odoo-modulos-comunidad (Client modules)


Authors:
    Ing. Andres Calle
    Ing. Patricio Rangles

""",
    'author': 'TRESCLOUD CIA LTDA',
    'maintainer': 'TRESCLOUD CIA. LTDA.',
    'website': 'http://www.trescloud.com',
    'depends': ['mail'],
    'external_dependencies': {
        'python': ['pathlib'],
    },
    'data': [],
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
    'cloc_exclude' : ['**/*'],
}
