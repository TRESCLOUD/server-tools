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

            for t_field in translatable_fields:
                #Añadimos el nombre de los campos traducibles a una lista para
                #realizar la comparacion
                t_name = '%s,%s' % (t_field.model_id.model, t_field.name)

                avoid_delete_translations_domain.append(t_name)
            #Buscamos los terminos que no esten en la lista de valores
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



