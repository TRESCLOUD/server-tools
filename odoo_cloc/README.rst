==============
Odoo Cloc
==============

Para instalar la dependencia en python es recomendable usar el siguiente comando:

pip install pathlib --index-url https://pypi.python.org/simple/

Extraccion de datos:
====================

Es recomendable usar un Web Service para su extraccion, el modulo es pensando para ser lo menos invasivo posible (sin vistas que modificar)

En el ejemplo se debe copiar el texto que entrega el sistema y guardarlo manualmente en un archivo de texto

Para usarlo requiere instalar erppeek:

pip install erppeek --index-url https://pypi.python.org/simple/

Ejemplo de WS (cloc.py):
------------------------

import erppeek


OE_HOST_origen = 'http://127.0.0.1:9069'

OE_DB_origen = 'TEST91'

OE_LOGIN_origen = 'admin'

OE_PASS_origen = 'admin'


client = erppeek.Client(OE_HOST_origen, OE_DB_origen, OE_LOGIN_origen, OE_PASS_origen, verbose=True)

result_code = client.execute('cloc.web.service', 'run_cloc_report', OE_DB_origen, False, False, 120)

print(result_code['result'])

