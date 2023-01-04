# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api
from odoo.models import AbstractModel
from odoo.addons.odoo_cloc.tools import cloc

class ClocWS(AbstractModel):
    _name = 'cloc.web.service'

    @api.model
    def get_cloc_data(self):
        msg = {
            'maintenance': {
                "version": cloc.VERSION,
                }
            }
        try:
            c = cloc.Cloc()
            c.count_env(self.env)
            if c.code:
                msg["maintenance"]["modules"] = c.code
            if c.errors:
                msg["maintenance"]["errors"] = list(c.errors.keys())
        except Exception:
            msg["maintenance"]["errors"] = ['cloc/error']
        return msg

    @api.model
    def run_cloc_report(self, database, path=False, verbose=True):
        c = cloc.Cloc()
        if database:
            c.count_database(database)
        if path:
            for i in path:
                c.count_path(i)
        c.report(verbose)