# -*- coding: utf-8 -*-

from openerp import models, fields, api
from odoo.exceptions import UserError, ValidationError
from openerp.tools.translate import _
from datetime import datetime, date

class ResetTranslationsWizard(models.Model):
    _name = 'reset.translations.wizard'


