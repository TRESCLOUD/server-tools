# -*- coding: utf-8 -*-
# Copyright 2018 Trescloud <http://trescloud.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.logging()    
def update_defaults_values(env):
    '''
    Actualiza los valores por defecto en las politicas de password de todas las compañias. 
    '''              
    query = '''
    UPDATE res_company set 
        password_expiration = 360,
        password_length = 6,
        password_lower = False,
        password_upper = False,
        password_numeric = True,
        password_special = False,
        password_history = 0,
        password_minimum = 0
    '''
    env.cr.execute(query)
        
@openupgrade.migrate(use_env=True)
def migrate(env, version):
    update_defaults_values(env)        