# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import ValidationError
import copy


class IrModel(models.Model):
    _inherit = 'ir.model'
    
    #Columns
    object_merger_model = fields.Boolean(string='Object Merger', 
                                         help='If checked, by default the Object Merger configuration '
                                              'will get this module in the list')


class MergerConfigSettings(models.TransientModel):
    _name = 'merger.config.settings'
    _inherit = 'res.config.settings'
    
    @api.multi
    def install(self):
        '''
        Initialization of the configuration
        '''
        for vals in self.read([]):
            result = self.update_field(vals)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload'
        }
    
    @api.model
    def create(self, vals):
        '''
        '''
        vals2 = copy.deepcopy(vals)
        result = super(MergerConfigSettings, self).create(vals2)
        self.update_field(vals)
        return result
    
    @api.multi
    def update_field(self, vals):
        '''
        '''
        model_ids = []
        model_obj = self.env['ir.model']
        action_obj = self.env['ir.actions.act_window']
        value_obj = self.env['ir.values']
        field_obj = self.env['ir.model.fields']
        ## Process ##
        if not vals or not vals.get('models_ids', False):
            return False
        elif vals.get('models_ids') or model_ids[0][2]:
            model_ids = vals.get('models_ids')
            if isinstance(model_ids[0], (list)):
                model_ids = model_ids[0][2]
        # Unlink Previous Actions
        unlink_ids = action_obj.search([('res_model', '=', 'object.merger')])
        for unlink_id in unlink_ids:
            unlink_id.suspend_security().unlink()
            un_val_ids = value_obj.search([('value', '=', "ir.actions.act_window," + str(unlink_id.id))])
            un_val_ids.unlink()
        # Put all models which were selected before back to not an object_merger
        model_not_merge_ids = model_obj.search([('id', 'not in', model_ids), ('object_merger_model', '=', True)])
        #Cambio para que funcione correctamente
        #FIX: si ningun modelo ha sido marcado anteriormente, no es necesario
        #hacer lo siguiente, agregando condicion
        if model_not_merge_ids:
            modx_ids = model_not_merge_ids
            modx_ids.write({'object_merger_model': False})
        # Put all models which are selected to be an object_merger
        mod_ids = self.env['ir.model'].browse(model_ids)
        mod_ids.write({'object_merger_model': True})
        ### Create New Fields ###
        object_merger_ids = model_obj.search([('model', '=', 'object.merger')])
        read_datas = mod_ids.read(['model','name', 'object_merger_model'])
        if not read_datas:
            read_datas = mod_ids
        view_id = self.env.ref('object_merger.view_object_merge_form')
        for model in read_datas:
            field_name = 'x_' + model['model'].replace('.','_') + '_id'
            act_id = action_obj.suspend_security().create({
                'name': "%s " % model['name'] + _("Merger"),
                'type': 'ir.actions.act_window',
                'res_model': 'object.merger',
                'src_model': model['model'],
                'view_type': 'form',
                'view_id': view_id.id,
                'context': "{'field_to_read':'%s'}" % field_name,
                'view_mode': 'form',
                'target': 'new'
            })
            value_obj.suspend_security().create({
                'name': "%s " % model['name'] + _("Merger"),
                'model': model['model'],
                'key2': 'client_action_multi',
                'value': "ir.actions.act_window," + str(act_id.id)
            })
            field_name = 'x_' + model['model'].replace('.','_') + '_id'
            if not field_obj.search([('name', '=', field_name), ('model', '=', 'object.merger')]):
                field_data = {
                    'model': 'object.merger',
                    'model_id': object_merger_ids.ids and object_merger_ids[0].id or False,
                    'name': field_name,
                    'relation': model['model'],
                    'field_description': "%s " % model['name'] + _('to keep'),
                    'state': 'manual',
                    'ttype': 'many2one',
                }
                field_obj.sudo().create(field_data)
        return True
    
    @api.model
    def _get_default_object_merger_models(self):
        '''
        Devuelve los modelos que tienen disponibles para mergear
        '''
        return self.env['ir.model'].search([('object_merger_model', '=', True)])
    
    #Columns
    models_ids = fields.Many2many('ir.model', 'object_merger_settings_model_rel',
                                  'object_merger_id', 'model_id', string='Models',
                                  domain=[('transient', '=', False)],
                                  default=_get_default_object_merger_models,
                                  help='')
