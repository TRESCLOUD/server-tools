# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# © 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import os
import logging
import urllib2
import urlparse
import subprocess
import tempfile
import socket
import json
import datetime
from odoo import _, api, models, exceptions
from odoo.tools import config, DEFAULT_SERVER_DATETIME_FORMAT

DEFAULT_KEY_LENGTH = 4096
_logger = logging.getLogger(__name__)


def get_data_dir():
    return os.path.join(config.options.get('data_dir'), 'letsencrypt')


def get_challenge_dir():
    return os.path.join(get_data_dir(), 'acme-challenge')


class Letsencrypt(models.AbstractModel):
    _name = 'letsencrypt'
    _description = 'Abstract model providing functions for letsencrypt'

    @api.model
    def call_cmdline(self, cmdline, loglevel=logging.INFO,
                     raise_on_result=True):
        process = subprocess.Popen(
            cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stderr:
            _logger.log(loglevel, stderr)
        if stdout:
            _logger.log(loglevel, stdout)
        if process.returncode:
            raise exceptions.Warning(
                _('Error calling %s: %d') % (cmdline[0], process.returncode)
            )
        return process.returncode

    @api.model
    def generate_account_key(self):
        data_dir = get_data_dir()
        if not os.path.isdir(data_dir):
            os.makedirs(data_dir)
        account_key = os.path.join(data_dir, 'account.key')
        if not os.path.isfile(account_key):
            _logger.info('generating rsa account key')
            self.call_cmdline([
                'openssl', 'genrsa', '-out', account_key,
                str(DEFAULT_KEY_LENGTH),
            ])
        assert os.path.isfile(account_key), 'failed to create rsa key'
        return account_key

    @api.model
    def generate_domain_key(self, domain):
        domain_key = os.path.join(get_data_dir(), '%s.key' % domain)
        if not os.path.isfile(domain_key):
            _logger.info('generating rsa domain key for %s', domain)
            self.call_cmdline([
                'openssl', 'genrsa', '-out', domain_key,
                str(DEFAULT_KEY_LENGTH),
            ])
        return domain_key

    @api.model
    def validate_domain(self, domain):
        local_domains = [
            'localhost', 'localhost.localdomain', 'localhost6',
            'localhost6.localdomain6'
        ]

        def _ip_is_private(address):
            import IPy
            try:
                ip = IPy.IP(address)
            except:
                return False
            return ip.iptype() == 'PRIVATE'

        if domain in local_domains or _ip_is_private(domain):
            raise exceptions.Warning(
                _("Let's encrypt doesn't work with private addresses "
                  "or local domains!"))

    @api.model
    def generate_csr(self, domain):
        domains = [domain]
        parameter_model = self.env['ir.config_parameter']
        altnames = parameter_model.search(
            [('key', 'like', 'letsencrypt.altname.')],
            order='key'
        )
        for altname in altnames:
            domains.append(altname.value)
        _logger.info('generating csr for %s', domain)
        if len(domains) > 1:
            _logger.info('with alternative subjects %s', ','.join(domains[1:]))
        config = parameter_model.get_param(
            'letsencrypt.openssl.cnf', '/etc/ssl/openssl.cnf'
        )
        csr = os.path.join(get_data_dir(), '%s.csr' % domain)
        with tempfile.NamedTemporaryFile() as cfg:
            cfg.write(open(config).read())
            if len(domains) > 1:
                cfg.write(
                    '\n[SAN]\nsubjectAltName=' +
                    ','.join(map(lambda x: 'DNS:%s' % x, domains)) + '\n')
            cfg.file.flush()
            cmdline = [
                'openssl', 'req', '-new',
                parameter_model.get_param(
                    'letsencrypt.openssl.digest', '-sha256'),
                '-key', self.generate_domain_key(domain),
                '-subj', '/CN=%s' % domain, '-config', cfg.name,
                '-out', csr,
            ]
            if len(domains) > 1:
                cmdline.extend([
                    '-reqexts', 'SAN',
                ])
            self.call_cmdline(cmdline)
        return csr

    def execute_reload_nginx(self):
        """
        Ejecuta el pedido de reload al servidor nginx centralizado
        """
        # se usara JSON para envio de datos y recepcion
        message = {
            'ID': '',
            'CODE': '',
            'RESULT': '',
            'DATA': ''    
        }
        company = self.env.user.company_id
        BUFFER_SIZE = 4096
        # El ID siempre sera el nombre de la BDD
        # Para Odoo Deployer es el ID de instancia
        message['ID'] = self.env.cr.dbname
        data_string = json.dumps(message, ensure_ascii=False).encode('utf8')
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((company.remote_nginx_server, int(company.nginx_reload_server_port)))
        s.send(data_string)
        data = s.recv(BUFFER_SIZE)
        s.close()
        message = json.loads(data)
        return message['CODE'], message['RESULT']

    @api.model
    def cron(self):
        # Agregado manejo de configuraciones en compania
        company = self.env.user.company_id
        company.last_execution_result = ''
        try:
            domain = urlparse.urlparse(
                self.env['ir.config_parameter'].get_param(
                    'web.base.url', 'localhost')).netloc
            self.validate_domain(domain)
            account_key = self.generate_account_key()
            csr = self.generate_csr(domain)
            acme_challenge = get_challenge_dir()
            if not os.path.isdir(acme_challenge):
                os.makedirs(acme_challenge)
            if self.env.context.get('letsencrypt_dry_run'):
                crt_text = 'I\'m a test text'
            else:  # pragma: no cover
                from acme_tiny import get_crt, DEFAULT_CA
                crt_text = get_crt(
                    account_key, csr, acme_challenge, log=_logger, CA=DEFAULT_CA)
            with open(os.path.join(get_data_dir(), '%s.crt' % domain), 'w')\
                    as crt:
                crt.write(crt_text)
                chain_cert = urllib2.urlopen(
                    self.env['ir.config_parameter'].get_param(
                        'letsencrypt.chain_certificate_address',
                        'https://letsencrypt.org/certs/'
                        'lets-encrypt-x3-cross-signed.pem')
                )
                crt.write(chain_cert.read())
                chain_cert.close()
                _logger.info('wrote %s', crt.name)
            # Si se llega a esta parte sin errores ya tenemos certificado
            # se setea la fecha actual + 3 meses como fecha de caducidad
            # del certificado
            date_now = datetime.datetime.now() + datetime.timedelta(3*365/12)
            company.ssl_expiration_date = date_now.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            # Verifico si en compania esta habilitado el nginx reload server
            if company.use_remote_reload_nginx_script:
                # Modo remoto, se usa los parametros para realizar el reload remoto
                code, result = self.execute_reload_nginx()
                if code!= 0:
                    raise exceptions.UserError(u'Error al recargar el servidor nginx!: %s\n%s' % (code, result))
            else:
                # Se utiliza el metodo original 
                reload_cmd = self.env['ir.config_parameter'].get_param(
                    'letsencrypt.reload_command', False)
                if reload_cmd:
                    _logger.info('reloading webserver...')
                    self.call_cmdline(['sh', '-c', reload_cmd])
                else:
                    _logger.info('no command defined for reloading webserver, please '
                                 'do it manually in order to apply new certificate')
        except Exception as e:
            company.last_execution_result = str(e)
            