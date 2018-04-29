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
        if self.env.context.get('mode', False) and self.env.context.get('mode') == 'all':
            #caso excepcional, forzamos el borrado de TODAS Las traducciones
            #para apoyar el proceso de anonimizar la base de datos
            delete_translations_domain = []
            translations = self.env['ir.translation'].search([])
            translations.unlink()
            return
        #Borramos explicitamente terminos que se reinstalarán la siguiente vez
        #por ejemplo los menus, los formularios
        models_fields_to_delete = [
            ('ir.actions.act_url','name'),
            ('ir.actions.act_url','help'),
            ('ir.actions.act_window','help'),
            ('ir.actions.act_window','name'),
            ('ir.actions.act_window_close','help'),
            ('ir.actions.actions','help'),
            ('ir.actions.client','help'),
            ('ir.actions.client','name'),
            ('ir.actions.report.xml','help'),
            ('ir.actions.report.xml','name'),
            ('ir.actions.server','help'),
            ('ir.actions.server','name'),
            ('ir.actions.server','body_html'),
            ('ir.actions.server','subject'),
            ('ir.actions.todo','note'),
            ('ir.filters','name'),
            ('ir.model','name'),
            ('ir.model.fields','help'),
            ('ir.model.fields','field_description'),
            ('ir.module.category','description'),
            ('ir.module.category','name'),
            ('ir.module.module','description'),
            ('ir.module.module','summary'),
            ('ir.module.module','shortdesc'),
            ('ir.ui.menu','name'),
            ('ir.ui.view','website_meta_title'),
            ('ir.ui.view','website_meta_description'),
            ('ir.ui.view','website_meta_keywords'),
            ('ir.ui.view','arch_db'),
            ('ir.ui.view.security','name'),
            ]
        for model, field in models_fields_to_delete:
            #excluimos la data creada por el usuario *ejemplo una traduccion de un menu creado a mano 
            non_user_ir_model_data = self.env['ir.model.data'].search([
                ('model','=',model),
                ('module','not in',['__export__',False]), #los datos exportados por el usuario tienen como modulo __export__
                ])
            non_user_user_res_ids = non_user_ir_model_data.mapped('res_id')
            translations = self.env['ir.translation'].search([
                ('name', '=', ",".join((model,field))),
                ('res_id', 'in', non_user_user_res_ids)
                ])
            translations.unlink()
        mssg = u'Traduciones borradas por usuario %s, a fecha %s' % (self.env.user.name, datetime.today())
        _logger.info(mssg)
        