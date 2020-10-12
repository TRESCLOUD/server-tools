# -*- coding: utf-8 -*-
# Copyright 2019 Trescloud <http://www.trescloud.com>
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openupgradelib import openupgrade


@openupgrade.logging()
def update_fields(env):
    """
    Actualiza los campos creados para que sean almacenables
    """
    object_merger_id = env['ir.model'].search(
        [('model', '=', 'object.merger')],
        limit=1
    )
    field_ids = env['ir.model.fields'].search(
        [('model_id', '=', object_merger_id.id)]
    )
    if field_ids:
        sql_query = '''
            update ir_model_fields set store = true where id in %s
        '''
        openupgrade.logged_query(env.cr, sql_query, args=[
            tuple(field_ids.ids)])


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    update_fields(env)
