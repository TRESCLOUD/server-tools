# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api
from odoo.models import AbstractModel
from odoo.addons.odoo_cloc.tools import cloc
import logging


_logger = logging.getLogger(__name__)

class ClocWS(AbstractModel):
    _name = 'cloc.web.service'

    @api.model
    def get_cloc_data(self):
        """
        Web Service que envia los datos procesados de cloc similiar a lo que 
        se envia a Odoo
        """
        _logger.info('WS consultado: get_cloc_data')
        msg = {
            'maintenance': {
                "version": cloc.VERSION,
                }
            }
        try:
            c = cloc.Cloc()
            c.allow_alternate_count = True
            c.count_env(self.env)
            if c.code:
                msg["maintenance"]["modules"] = c.code
            if c.errors:
                msg["maintenance"]["errors"] = list(c.errors.keys())
        except Exception:
            msg["maintenance"]["errors"] = ['cloc/error']
        return msg

    @api.model
    def run_cloc_report(self, database, path=False, verbose=False):
        """
        Web Service que envia los datos procesados por cloc
        Requiere el envio de los parametros solicitados, para su control se agrega logs
        """
        _logger.info('WS consultado: run_cloc_report, parametros entregados:\ndatabase=%s\npath=%s\nverbose=%s' % (database, path, verbose))
        c = cloc.Cloc()
        c.allow_alternate_count = True
        if database:
            c.count_database(database)
        if path:
            for i in path:
                c.count_path(i)
        return c.report(verbose, width=160, ws=True)