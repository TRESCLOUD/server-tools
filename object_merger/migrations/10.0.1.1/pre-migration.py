# -*- coding: utf-8 -*-
# Copyright 2019 Trescloud <http://www.trescloud.com>
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openupgradelib import openupgrade
import logging

_logger = logging.getLogger(__name__)


@openupgrade.logging()
def object_merger_update(env):
    '''
    Realiza una limpieza sobre la tabla relacional entre el object merge y
    los modelos a mezclar, para evitar el error relacionado con
    la migracion del modulo a v10
    '''
    object_merger_module = env['ir.module.module'].search(
        [
            ('name', '=', 'object_merger'),
            ('state', 'in', ['installed', 'to upgrade'])
        ], limit=1
    )
    if object_merger_module:
        # Se elimina la relacion principal
        sql_query = '''
                drop table object_merger_settings_model_rel
            '''
        openupgrade.logged_query(env.cr, sql_query, args=None)



@openupgrade.migrate(use_env=True)
def migrate(env, version):
    object_merger_update(env)