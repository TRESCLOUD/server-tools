# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api
from odoo.exceptions import UserError, ValidationError
from openerp.tools.translate import _
from datetime import datetime, date

class TrescloudAnonymizationWizard(models.Model):
    _name = 'trescloud.anonymization.wizard'

    @api.multi
    def do_anonymizate(self):
        '''
        Las operaciones que realizaremos:
        - Remover traducciones
        - Remover datos emails(tanto mail.message como mail.mail)
        - Remover datos de hr_applicant
        - Ejecutar funcion de remocion de campos (database_cleanup)
        - Remover adjuntos
        - Anonimizar otros campos de sale.order, crm.lead, res.partner, res.partner.bank,
        sale.layout_category, sale.quote.template, product.template, purchase.order,
        account.invoice, sri.authorizations, algunos campos de Nomina y Proyectos
        '''
        self.ensure_one()
        #Remover traducciones
        translator_reset = self.env['reset.translations.wizard'].create({})
        translator_reset.with_context({
            'mode': self.translation_mode,
        }).do_reset_translations()

        #Remover datos email
        self.env.cr.execute("DELETE FROM public.mail_message")
        self.env.cr.execute("DELETE FROM public.mail_mail")

        #Remover datos de hr_applicant
        #Buscamos si esta instalado hr_recruitment
        module = self.env['ir.module.module'].search([('name', '=', 'hr_recruitment'),
                                                      ('state', '=', 'installed')])
        if module:
            self.env.cr.execute("DELETE FROM public.hr_applicant")

        #Eecutando funcion de database_cleanup
        #Segun la indicacion solo lo hago a los campos
        purge_colums_wizard = self.env['cleanup.purge.wizard.column'].create({})
        purge_colums_wizard.purge_all()

        #Removiendo adjuntos
        self.env.cr.execute("DELETE FROM public.ir_attachment")

    #Columns
    translation_mode = fields.Selection([('all', 'All'),
                                         ('user', 'Users translations')],
                                        'Translation anonymization mode', required=True)
