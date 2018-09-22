# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools
from odoo.exceptions import UserError


class WizardAllowModuleModification(models.TransientModel):
    _name = 'wizard.allow.module.modification'
    
    
    @api.model
    def action_check(self, fields):
        '''
        Este metodo verifica si el password introducido es el mismo que el de sistema
        si es asi retorna True permitiendo la modificacion del modulo
        '''
        new_context = self._context.copy()
        wiz = self.browse(fields[0])
        admin_pass = tools.config['admin_passwd']
        if not wiz.password_control == admin_pass:
            raise UserError("La contraseña es incorrecta")
        new_context['password_ok'] = True
        # La contraseña es correcta, ahora se requiere ejecutar la modificacion solicitada
        list_ids = self._context['active_ids']
        module_list = self.env['ir.module.module'].with_context(new_context).browse(list_ids)
        #ejecutamos la funcion solicitada
        if self._context['function'] == 'button_install':
            return module_list.button_immediate_install()
        elif self._context['function'] == 'button_uninstall':
            return module_list.button_immediate_uninstall()
        return False
        
    password_control = fields.Char(string="Escriba la contraseña de gestion de base de datos")

