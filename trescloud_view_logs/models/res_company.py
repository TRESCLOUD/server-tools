# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class Company(models.Model):
    _inherit = 'res.company'

    def action_wizard_view_odoo_log(self):
        '''
        Levanta el wizard de visualizacion de logs
        '''
        #self.message_post(body=u'La clave fue consultada')
        view = self.env.ref('trescloud_view_logs.wizard_view_logs_form')
        return {
            #'name': u'Modificar clave ...',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view.id or False,
            'res_model': 'view.logs',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new'
        }
