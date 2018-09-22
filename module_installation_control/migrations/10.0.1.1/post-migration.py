# -*- coding: utf-8 -*-
# © 2017 Therp BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.logging()
def update_language_espanish(env):
    '''
    Metodo que actualiza el lenguaje español estandar reescribiendolo en la base de datos
    '''
    translate = env['base.language.install'].create({
        'lang': 'es_ES',
        'overwrite': True,
        })
    translate.lang_install()

@openupgrade.migrate(use_env=True)
def migrate(env, version):
    update_language_espanish(env)