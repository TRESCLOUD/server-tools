# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import odoo
from odoo import api, fields, models, modules, tools, _
from odoo.exceptions import AccessDenied, UserError


class Module(models.Model):
    _inherit = "ir.module.module"


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

        2020-07-17: Se agrega un segundo bypass basado en whitelist, de esta manera se controla
                    modulos permitidos de instalacion sin necesidad de consultarlo
        """
        white_list_module = (
            'proyectox_landed_costs',
            'trescloud_landed_costs',
            'ecua_mrp',
            'trescloud_product_history',
            'ecua_fixed_assets',
            'ecua_credit_card_reconcile',
            'ecua_account_analitic',
            'web_environment_ribbon',
            'ecua_ecommerce'
            )
        if self.name in white_list_module:
            # Esta seccion funciona en la instalacion
            # Activado Whitelist
            return False
        elif not self.name and self._context.get('active_id',False):
            # Esta seccion funciona en la desinstalacion
            # verifico si es el modulo de web_environment_ribbon pero por id
            module_browse = self.env['ir.module.module'].sudo().browse(self._context.get('active_id',False))
            if module_browse.name == 'web_environment_ribbon':
                # Activado la desinstalacion de web_environment_ribbon
                return False                
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
            'name': 'Asistente para control de instalacion de modulos',
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
        Funcion que muestra un error al tratar de instalar desde la accion del servidor
        """
        raise UserError("La instalacion de modulos debe realizarce desde el boton de la vista formulario del modulo")
