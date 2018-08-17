# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import odoo
from odoo import api, fields, models, modules, tools, _
from odoo.exceptions import AccessDenied, UserError


class Module(models.Model):
    _inherit = "ir.module.module"

    @api.multi
    def button_immediate_install_control(self):
        """
        Funcion modificada para controlar con un wizard la manipulacion de modulos
        """
        new_context = self._context.copy()
        new_context['control_modification'] = True
        new_context['list_ids'] = self._ids
        new_context['function'] = "button_install"
        return self.with_context(new_context).button_immediate_install()    
                
    @api.multi
    def button_immediate_uninstall_control(self):
        """
        Funcion modificada para controlar con un wizard la manipulacion de modulos
        """
        new_context = self._context.copy()
        new_context['control_modification'] = True
        new_context['list_ids'] = self._ids
        new_context['function'] = "button_uninstall"
        return self.with_context(new_context).button_immediate_uninstall()    

    @api.multi
    def _button_immediate_function(self, function):
        """
        Controla con wizard la instalacion de modulos
        el wizard pide la contraseña de administracion
        si es la misma permite la instalacion del modulo
        Esta funcion centraliza la manipuilacion de modulos, es por esto
        que se ejecuta varias veces y por eso se debe controlar desde donde proviene el llamado
        """
        if self.check_control_modification():
            return self.open_wizard_window()
        return super(Module, self)._button_immediate_function(function)

    def check_control_modification(self):
        """
        Esta funcion analiza si en el contexto o en los parametros
        se ha enviado el control desde formulario para la manipulacion de modulos
        en este caso se analizara lo siguiente:
        1) El contexto asociado contenga la clave control_modification en True
        2) El bypass: si el modulo trescloud_set_database_test esta instalado permitir manipular todos los modulos
        3) El password fue correcto, debe permitir la instalacion
        """
        module_ids = self.env['ir.module.module'].sudo().search([('name','=','trescloud_set_database_test'), ('state','=','installed')])
        if module_ids:
            # Activado Bypass
            return False
        if 'control_modification' in self._context and self._context['control_modification'] == True:
            #Verificamos si el control por password fue aceptado
            if 'password_ok' in self._context and self._context['password_ok'] == True:
                return False
            return True
        # Cualquier caso retorna False, asi se permite instalar desde linea de comandos
        return False

    def open_wizard_window(self):
        obj, view_id = self.env['ir.model.data'].get_object_reference('module_installation_control', 'view_allow_module_modification_form')
        res = {
            'name': 'Wizard Allow Module Modification',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.allow.module.modification',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'domain': '[]',
            'context': self._context,
            'target': 'new',
            'nodestroy': True
        }
        return res
    
    @api.multi
    def server_action_immediate_install(self):
        """
        Funcion que abre el wizard de control directamente
        """
        new_context = self._context.copy()
        new_context['control_modification'] = True
        new_context['list_ids'] = self._ids
        new_context['function'] = "button_install"
        return self.open_wizard_window()
