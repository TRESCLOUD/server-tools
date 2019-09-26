# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from contextlib import contextmanager
from threading import current_thread
from odoo import api, models, SUPERUSER_ID
from odoo.exceptions import AccessDenied
from odoo.service import wsgi_server
# INICIO DEL CODIGO AGREGADO POR TRESCLOUD
from odoo.tools import safe_eval
from odoo import fields
# FIN DEL CODIGO AGREGADO POR TRESCLOUD

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    # HACK https://github.com/odoo/odoo/issues/24183
    # TODO Remove in v12, and use normal odoo.http.request to get details
    @api.model_cr
    def _register_hook(self):
        """🐒-patch XML-RPC controller to know remote address."""
        original_fn = wsgi_server.application_unproxied

        def _patch(environ, start_response):
            current_thread().environ = environ
            return original_fn(environ, start_response)

        wsgi_server.application_unproxied = _patch

    # Helpers to track authentication attempts
    @classmethod
    @contextmanager
    def _auth_attempt(cls, login):
        """Start an authentication attempt and track its state."""
        try:
            # Check if this call is nested
            attempt_id = current_thread().auth_attempt_id
        except AttributeError:
            # Not nested; create a new attempt
            attempt_id = cls._auth_attempt_new(login)
        if not attempt_id:
            # No attempt was created, so there's nothing to do here
            yield
            return
        try:
            current_thread().auth_attempt_id = attempt_id
            result = "successful"
            try:
                yield
            except AccessDenied as error:
                result = getattr(error, "reason", "failed")
                raise
            finally:
                cls._auth_attempt_update({"result": result})
        finally:
            try:
                del current_thread().auth_attempt_id
            except AttributeError:
                pass  # It was deleted already

    @classmethod
    def _auth_attempt_force_raise(cls, login, method):
        """Force a method to raise an AccessDenied on falsey return."""
        try:
            with cls._auth_attempt(login):
                result = method()
                if not result:
                    # Force exception to record auth failure
                    raise AccessDenied()
        except AccessDenied:
            pass  # `_auth_attempt()` did the hard part already
        return result

    @classmethod
    def _auth_attempt_new(cls, login):
        """Store one authentication attempt, not knowing the result."""
        # Get the right remote address
        try:
            remote_addr = current_thread().environ["REMOTE_ADDR"]
        except (KeyError, AttributeError):
            remote_addr = False
        # Exit if it doesn't make sense to store this attempt
        if not remote_addr:
            return False
        # Use a separate cursor to keep changes always
        with cls.pool.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            attempt = env["res.authentication.attempt"].create({
                "login": login,
                "remote": remote_addr,
            })
            return attempt.id

    @classmethod
    def _auth_attempt_update(cls, values):
        """Update a given auth attempt if we still ignore its result."""
        auth_id = getattr(current_thread(), "auth_attempt_id", False)
        if not auth_id:
            return {}  # No running auth attempt; nothing to do
        # Use a separate cursor to keep changes always
        with cls.pool.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            attempt = env["res.authentication.attempt"].browse(auth_id)
            # Update only on 1st call
            if not attempt.result:
                attempt.write(values)
            return attempt.copy_data()[0] if attempt else {}

    # Override all auth-related core methods
    @classmethod
    def _login(cls, db, login, password):
        return cls._auth_attempt_force_raise(
            login,
            lambda: super(ResUsers, cls)._login(db, login, password),
        )

    @classmethod
    def authenticate(cls, db, login, password, user_agent_env):
        return cls._auth_attempt_force_raise(
            login,
            lambda: super(ResUsers, cls).authenticate(
                db, login, password, user_agent_env),
        )

    @api.model
    def check_credentials(self, password):
        """This is the most important and specific auth check method.

        When we get here, it means that Odoo already checked the user exists
        in this database.

        Other auth methods usually plug here.
        """
        login = self.env.user.login
        with self._auth_attempt(login):
            # Update login, just in case we stored the UID before
            attempt = self._auth_attempt_update({"login": login})
            remote = attempt.get("remote")
            # Fail if the remote is banned
            trusted = self.env["res.authentication.attempt"]._trusted(
                remote,
                login,
            )
            if not trusted:
                error = AccessDenied()
                error.reason = "banned"
                raise error
            # Continue with other auth systems
            return super(ResUsers, self).check_credentials(password)

    # INICIO DEL CODIGO AGREGADO POR TRESCLOUD
    @api.multi
    def unblock_user(self):
        """
        Desbloquea el usuario que ha sido baneado por alcanzar el limite de
        intentos fallidos de autenticacion
        """
        self.ensure_one()
        attempt_obj = self.env['res.authentication.attempt']
        domain = [("login", "=", self.login)]
        # Find last successful login
        last_ok = attempt_obj.search(
            domain + [("result", "=", "successful")],
            order='create_date desc',
            limit=1,
        )
        if last_ok:
            domain += [("create_date", ">", last_ok.create_date)]
        # Find failures since last success, if any
        recent_failures = attempt_obj.search(
            domain + [("result", "!=", "successful")],
        )
        recent_failures.unlink()

    @api.multi
    def open_login_records(self):
        """
        Abre la vista lista del objeto
        'res.authentication.attempt' filtrado por el usuario activo
        """
        self.ensure_one()
        action_id = self.env.ref(
            'auth_brute_force.action_res_authentication_attempt'
        )
        action_dict = action_id.read([])[0]

        result_context = safe_eval(action_dict.get('context', '{}')) or {}
        result_context.update({'search_default_login': self.login})
        action_dict['context'] = str(result_context)
        return action_dict

    @api.depends()
    def _compute_is_banned(self):
        """
        Busca el ultimo intento de autenticacion del usuario para ver
        si ha sido baneado
        """
        attempts = self.env['res.authentication.attempt'].read_group([
            ('login', 'in', self.mapped('login')),
            ('result', '=', 'banned')],
            fields=['login'],
            groupby=['login']
        )
        mapping = dict(
            [(attempt['login'], attempt['login_count']) for attempt in attempts]
        )
        for user in self:
            user.is_banned = mapping.get(user.login, 0) > 0

    is_banned = fields.Boolean(
        help='Technical field to compute if user is banned by reach max'
             ' attempts of failed logins',
        compute="_compute_is_banned"
    )
    # FIN DEL CODIGO AGREGADO POR TRESCLOUD
