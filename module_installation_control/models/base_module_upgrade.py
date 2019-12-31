# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import odoo
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class BaseModuleUpgrade(models.TransientModel):
    _inherit = "base.module.upgrade"

    @api.multi
    def upgrade_module(self):
        """
        Controla con wizard la actualizacion de modulos
        el wizard pide la contraseña de administracion
        si es la misma permite la modificacion de modulos
        Esta funcion centraliza la eliminacion y actualizacion de modulos
        """
        Module = self.env['ir.module.module']
        if Module.check_control_modification():
            return Module.open_wizard_window()
        return super(BaseModuleUpgrade, self).upgrade_module()
