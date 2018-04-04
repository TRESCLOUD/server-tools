# -*- coding: utf-8 -*-

from openerp import models, fields, api
from odoo.exceptions import UserError, ValidationError
from openerp.tools.translate import _
from datetime import datetime, date
import logging

_logger = logging.getLogger(__name__)

class ResetTranslationsWizard(models.Model):
    _name = 'reset.translations.wizard'

    @api.multi
    def do_reset_translations(self):
        '''
        Borra las traducciones del sistema
        Por contexto viene la clave mode si es llamado desde trescloud_anonymization
        y ejecutar el proceso de borrado de las traducciones
        '''
        self.ensure_one()
        #Buscando las traduciones en dependencia del modo
        #o la ausencia del mismo
        translation_obj = self.env['ir.translation']
        if self.env.context.get('mode', False):
            if self.env.context['mode'] == 'all':
                translations = translation_obj.search([])
            else:
                translations = translation_obj.search([('type', 'not in', ['model'])])
        else:
            translations = translation_obj.search([])

        #Borrando las trauducciones
        if translations:
            translations.unlink()
            #Guardando mensaje en el log
            mssg = u'Traduciones borradas por usuario %s, a fecha %s' % (self.env.user.name,
                                                                         datetime.today())
            _logger.info(mssg)



