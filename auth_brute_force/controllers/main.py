# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.tools.translate import _
from odoo.addons.auth_signup.controllers.main import AuthSignupHome as Home


class HomeAuth(Home):

    @http.route()
    def web_login(self, *args, **kw):
        """
        Heredamos para agregar mensaje de bloqueo de cuenta
        a partir de sobrepasar los intentos de autenticarse
        """
        res = super(HomeAuth, self).web_login(*args, **kw)
        if res.qcontext.get('login', False) and res.qcontext['login_success'] == False:
            attemp_id = request.env['res.authentication.attempt'].search([
                ('login', '=', res.qcontext['login'])], limit=1)
            if attemp_id and attemp_id.result == 'banned':
                res.qcontext['error'] = _(
                    "The maximun number of tries have been reached. "
                    "The %s has been banned. Please contact with the "
                    "service administrator.") % _(attemp_id.error_metadata)
        return res

    @http.route('/web/reset_password', type='http', auth='public',
                website=True)
    def web_auth_reset_password(self, *args, **kw):
        """
        Herencia para mejorar el mensaje cuando no se puede restablecer la
        contraseña si es que el usuario esta bloqueado
        """
        result = super(HomeAuth, self).web_auth_reset_password(*args, **kw)
        if 'error' in result.qcontext and \
            request.httprequest.method == 'POST' and \
                result.qcontext.get('login', False):
                attemp_id = request.env['res.authentication.attempt'].search([
                    ('login', '=', result.qcontext['login'])], limit=1)
                if attemp_id and attemp_id.result == 'banned':
                    result.qcontext['error'] = _(
                        "Could not reset your password. "
                        "The user has been banned. Please contact with the "
                        "service administrator.")
        return result