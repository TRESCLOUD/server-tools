# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.auth_signup.controllers.main import AuthSignupHome as Home


class HomeAuth(Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        """
        Heredamos para agregar mensaje de bloqueo de cuenta
        a partir de sobrepasar los intentos de autenticarse 
        """
        res = super(HomeAuth, self).web_login(redirect=redirect, kw=kw)
        if res.qcontext.get('login', False) and res.qcontext['login_success'] == False:
            attemp_id = request.env['res.authentication.attempt'].search([
                ('login', '=', res.qcontext['login'])], limit=1)
            if attemp_id and attemp_id.result == 'banned':
                res.qcontext['error'] = _("The maximun number of tries have been reached. "
                                          "The user has been banned. "
                                          "Please contact with the service administrator.")
        return res