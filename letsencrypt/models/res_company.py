# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class Company(models.Model):
    _inherit = 'res.company'
    
    #Columns
    last_execution_result = fields.Text(
        string='Last execution result',
        help='Muestra el estado de la ultima ejecucion de actualizacion del certificado SSL'
        )
    ssl_expiration_date = fields.Datetime(
        string='SSL expiration date',
        help='Muestra la fecha y hora de expiracion del ultimo certificado obtenido'
        )