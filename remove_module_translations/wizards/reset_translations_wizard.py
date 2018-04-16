# -*- coding: utf-8 -*-
# Copyright 2018 TRESCLOUD Cia Ltda.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html

from openerp import models, fields, api
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class ResetTranslationsWizard(models.Model):
    _name = 'reset.translations.wizard'

    @api.multi
    def do_reset_translations(self):
        """
        Borra las traducciones del sistema
        Por contexto viene la clave mode si es llamado desde
        trescloud_anonymization y ejecutar el proceso
         de borrado de las traducciones
        """
        self.ensure_one()
        #Buscando las traduciones en dependencia del modo
        #o la ausencia del mismo
        translation_obj = self.env['ir.translation']
        if self.env.context.get('mode', False) and \
                self.env.context['mode'] == 'all':
            translations = translation_obj.search([])
        else:
            ir_model_fields_obj = self.env['ir.model.fields']
            # Se buscan los campos traducibles
            translatable_fields = ir_model_fields_obj.search(
                [('translate', '=', True)])
            avoid_delete_translations_domain = []

            # help_query = '''SELECT it.id
            # FROM public.ir_translation it
            # where it.res_id > 0 and it.name = '%s';'''

            for t_field in translatable_fields:
                t_name = '%s,%s' % (t_field.model_id.model, t_field.name)
                # self.env.cr.execute(help_query, (t_name,))
                # avoid_delete_translations.extend([record[0] for record in
                #                                   self.env.cr.fetchall()])
                avoid_delete_translations_domain.append(t_name)

            translations = translation_obj.search(
                [('name', 'not in', avoid_delete_translations_domain)]
            )

        #Borrando las trauducciones
        if translations:
            translations.unlink()
            #Guardando mensaje en el log
            mssg = u'Traduciones borradas por usuario %s, a fecha %s' % (
                self.env.user.name, datetime.today())
            _logger.info(mssg)



