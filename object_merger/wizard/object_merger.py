# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields as odoo_fields, models, SUPERUSER_ID
from openerp.tools import ustr
from odoo.exceptions import ValidationError


class ObjectMerger(models.TransientModel):
    _name = 'object.merger'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        '''
        '''
        res = super(ObjectMerger, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=False)
        object_ids = self.env.context.get('active_ids', [])
        active_model = self.env.context.get('active_model')
        field_name = 'x_' + (active_model and active_model.replace('.','_') or '') + '_id'
        fields = res['fields']
        if object_ids:
            view_part = """<label for='"""+field_name+"""'/>
                        <div>
                            <field name='""" + field_name +"""'
                            required="1" domain="[(\'id\', \'in\', """ + str(object_ids) + """)]"/>
                        </div>"""
            res['arch'] = res['arch'].decode('utf8').replace("""<separator string="to_replace"/>""", view_part)
            field = self.fields_get([field_name])
            fields.update(field)
            res['fields'] = fields
            res['fields'][field_name]['domain'] = [('id', 'in', object_ids)]
            res['fields'][field_name]['required'] = True
        return res

    @api.multi
    def action_merge(self):
        ''''
        Merges two or more objects
        '''
        property_ids = []
        object = {}
        active_model = self.env.context.get('active_model')
        property_obj = self.env['ir.property']
        if not active_model:
            raise ValidationError(_(u'No hay un modelo activo definido.'))
        model_pool = self.env[active_model]
        object_ids = self.env.context.get('active_ids', [])
        field_to_read = self.env.context.get('field_to_read')
        fields = field_to_read and [field_to_read] or []

        if self.env.context.get('origin', False) \
                != 'ecua_fiscal_positions_core':
            object = self.read(fields)
            object = object[0]
        else:
            fiscal_position = model_pool.browse(object_ids[1])
            object.update({'id': fiscal_position.id, fields[0]: (fiscal_position.id, fiscal_position.name)})
        if self.env.context.get('to_invoke', False):
            object.update({field_to_read: [self.env.context.get(
                'object_to_preserve_id', False)]})

        if object and fields and object[field_to_read]:
            object_id = object[field_to_read][0]
        else:
            raise ValidationError(_(u'Por favor, seleccione un valor a mantener.'))
        # For one2many fields on res.partner
        warning = []
        self.env.cr.execute("SELECT name, model FROM ir_model_fields WHERE "
                            "relation=%s and ttype not in ('many2many', 'one2many');",
                            (active_model,))
        for name, model_raw in self.env.cr.fetchall():
            try:
                hasattr(self.env[model_raw], '_auto')
            except:
                warning.append(model_raw)
        self.env.cr.execute("select name, model from ir_model_fields where "
                            "relation=%s and ttype in ('many2many');", (active_model,))
        for field, model in self.env.cr.fetchall():
            try:
                self.env[model]._fields.get(field, False) and (
                isinstance(
                    self.env[model]._fields[field], odoo_fields.Many2many) and
                (not self.env[model]._fields[field].compute and
                 self.env[model_raw]._fields[name].related or
                 self.env[model]._fields[field].store)) and \
                         self.env[model]._fields[field] or False
            except:
                warning.append(model)
        if warning:
            list = '\n'.join("'"+ w + "'," for w in warning)
            self.env.cr.execute("DELETE FROM ir_model_fields WHERE model in %s", (tuple(warning),))
        # For one2many fields on res.partner
        self.env.cr.execute("SELECT name, model FROM ir_model_fields WHERE "
                            "relation=%s and ttype not in ('many2many', 'one2many');",
                            (active_model,))
        for name, model_raw in self.env.cr.fetchall():
            if name == 'property_account_position' and \
                            model_raw == 'res.partner':
                for id in object_ids:
                    property_ids.extend(property_obj.
                                        search([('name','=','property_account_position'),
                                                ('value_reference','ilike','%s' %(id,))]))
                property_obj.write(property_ids,
                                  {'value_reference':'account.fiscal.position,'
                                                      +str(object_id)})
            if hasattr(self.env[model_raw], '_auto'):
                if not self.env[model_raw]._auto:
                    continue
            if hasattr(self.env[model_raw], '_check_time'):
                continue
            else:
                if hasattr(self.env[model_raw], '_fields'):
                    if (self.env[model_raw]._fields.get(name, False) and
                                isinstance(self.env[model_raw]._fields[name],
                                           odoo_fields.Many2one)) and \
                            (not self.env[model_raw]._fields[name].compute \
                            and self.env[model_raw]._fields[name].related or
                                 self.env[model_raw]._fields[name].store):
                        if hasattr(self.env[model_raw], '_table'):
                            model = self.env[model_raw]._table
                        else:
                            model = model_raw.replace('.', '_')
                        requete = "UPDATE "+model+" SET "+name+"="+\
                                  str(object_id)+" WHERE "+ \
                                  ustr(name) +" IN " + \
                                  str(tuple(object_ids)) + ";"
                        self.env.cr.execute(requete)
        self.env.cr.execute("select name, model from ir_model_fields where "
                            "relation=%s and ttype in ('many2many');", (active_model,))
        for field, model in self.env.cr.fetchall():
            field_data = self.env[model]._fields.get(field, False) and (
                isinstance(
                    self.env[model]._fields[field], odoo_fields.Many2many) and
                (not self.env[model]._fields[field].compute and
                 self.env[model_raw]._fields[name].related or
                 self.env[model]._fields[field].store)) and \
                         self.env[model]._fields[field] or False
            if field_data:
                model_m2m = field_data.relation
                rel2 = field_data.column2
                requete = "UPDATE "+model_m2m+" SET "+\
                          rel2+"="+str(object_id)+" WHERE "+ \
                          ustr(rel2) +" IN " + str(tuple(object_ids)) + ";"
                self.env.cr.execute(requete)
        unactive_object_ids = model_pool.search([('id', 'in', object_ids),('id', '<>', object_id)])
        context = self.env.context.copy()
        context.update({'origin': 'object_merge'})
        for unactive in unactive_object_ids:
            unactive.write({
                'active': False,
                'deprecated': True #Algunos modelos estan usando deprecated, es similar al active
            })
        if not self.env.context.get('active_model'):
            raise ValidationError(_(u'No existe un modelo activo, por favor verifique.'))
        list = []
        for id in unactive_object_ids:
            list.append(self.env.context.get('active_model')+','+str(id.id))
        self.env.cr.execute('''
                    UPDATE ir_property SET value_reference = %s 
                    WHERE value_reference IN %s''', 
                    tuple([self.env.context.get('active_model')+','+str(object_id), tuple(list)]))
        return {'type': 'ir.actions.act_window_close'}
    
    #Columns
    name = odoo_fields.Char('Name', size=16,
                            help='')

