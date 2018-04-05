# -*- coding: utf-8 -*-
# Copyright 2018 Trescloud <http://trescloud.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.logging()    
def update_date_write_password(env):
    '''
    Actualiza la fecha de password requerido para esta version. 
    '''              
    query = '''
    UPDATE 
       res_users set password_write_date = now() 
    where 
      password_write_date is null
      and active = True;
    '''
    env.cr.execute(query)
        
@openupgrade.migrate(use_env=True)
def migrate(env, version):
    update_date_write_password(env)
        