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
    use_remote_reload_nginx_script = fields.Boolean(
        string='Use Remote reload Nginx Script',
        default=False,
        help='Seleccione esta opcion si desea usar el script de reincio remoto en vez de la linea de comandos estandar'
        )
    remote_nginx_server = fields.Char(
        string='Remote IP or DNS of Nginx Server',
        help='INgrese la direccion URL o IP del servidor remoto Nginx'
        )
    nginx_reload_server_port = fields.Char(
        string='Port of reload nginx server',
        help='Ingrese el puerto de escucha del servidor de reload de neginx'
        )
