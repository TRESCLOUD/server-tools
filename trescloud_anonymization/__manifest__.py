# -*- coding: utf-8 -*-

{
    'name': "Trescloud Anonymizate",
    'version': '1.0',
    'depends': ['base', 'anonymization', 'remove_module_translations', 'database_cleanup'],#me falta agregar el “remove_module_translations”, tengo que descargarlo
    'author': "Trescloud, OpenConsulting Cia. Ltda.",
    'category': 'Technical',
    'description': """
    Proceso de anonimizacion para Trescloud.
    """,
    'data': [
        'data/ir.model.fields.anonymization.csv',
        'wizards/anonymization_process_wizard_view.xml'
    ],
}