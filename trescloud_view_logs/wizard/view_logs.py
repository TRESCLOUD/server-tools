# -*- coding: utf-8 -*-
from file_read_backwards import FileReadBackwards
from datetime import datetime, timedelta

from odoo import models, fields
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class ViewLogs(models.TransientModel):
    _name = "view.logs"
    _description = "Abstract model providing functions for view.logs"

    """
    Clase creada para leer logs en reversa desde python

    basado en este analisis
    https://code.activestate.com/recipes/439045-read-a-text-file-backwards-yet-another-implementat/
    """

    # def _reverseReadFile(self, file, BLKSIZE = 4096):
    #     """Read a file line by line, backwards"""
    #     if( not file.seekable() ):
    #         return

    #     buf = ""
    #     file.seek(0, 2)
    #     lastchar = file.read(1)
    #     trailing_newline = (lastchar == "\n")

    #     while 1:
    #         newline_pos = buf.rfind("\n")
    #         pos = file.tell()
    #         if newline_pos != -1:
    #             # Found a newline
    #             line = buf[newline_pos+1:]
    #             buf = buf[:newline_pos]
    #             if pos or newline_pos or trailing_newline:
    #                 line += "\n"
    #             yield line
    #         elif pos:
    #             # Need to fill buffer
    #             toread = min(BLKSIZE, pos)
    #             file.seek(pos-toread, 0)
    #             buf = file.read(toread) + buf
    #             file.seek(pos-toread, 0)
    #             if pos == toread:
    #                 buf = "\n" + buf
    #         else:
    #             # Start-of-file
    #             return

    def _compare_date_time_on_log_line(self, date1, log_line):
        """
        Compara la fecha de la linea de log con la fecha entregada
        indicando si cumple la condicion de ser mayor la fecha del log
        que la fecha enviada por referencia

        log actual:

        Apr 21 17:42:25 ip-172-31-53-98 odoo-15-trescloud[671]: 2023-04-21 17:42:25,278 101421 INFO ...

        """
        # extraigo la fecha y le agrego el año actual
        date_line = str(date1.year) + " " + log_line[:15]
        # convierto a objeto
        log_date = datetime.strptime(date_line, '%Y %b %d %H:%M:%S')
        _logger.info(u'fechas a comparar, log_date %s, date1 %s' % (log_date, date1))
        return log_date > date1

    def _get_latest_n_minutes_odoo_log(self, minutes):
        """
        Extrae el log desde este momento hacia atras, los minutos inidicados
        Solo lee el log actual, no lee logs rotados
        """
        data_extract = []
        log_file = "/var_log/odoo.log"
        until_date = datetime.now() - timedelta(minutes=minutes)
        db_name = self._cr.dbname
        _logger.info(u'Base a buscar: %s, fecha tope: %s'  % (db_name, until_date))
        #for line in self._reverseReadFile(open(log_file)):
        with FileReadBackwards(log_file, encoding="utf-8") as frb:
            for line in frb:
                _logger.info(u'Linea a analizar: %s' % line)
                # filtrado del log en caso multiples instancias
                # lo filtramos por nombre de la base de datos
                if not line:
                    # linea vacia, no la tomo en cuenta
                    pass
                if db_name in line:
                    _logger.info(u'Linea tiene el nombre de labse de datos: %s' % db_name)
                    if self._compare_date_time_on_log_line(until_date, line):
                        data_extract.append(line)
                        _logger.info(u'Linea agregada: %s' % line)
                    else:
                        # esta parte del log ya no se requiere
                        break
        return data_extract

    def _get_log_from_to_especific_date(self, start_datetime, stop_datetime):
        """
        Extrae desde el log de Odoo los datos desde la fecha solicitada hasta la fecha final
        si es que hay datos que puedan ser mostrados
        """
        return False

    def _create_file_to_dowload_from_log(self, data_extract):
        """
        Crea un archivo descargable via wizard
        """
        return False

    def execute_read_log(self):
        """
        Funcion que ejecuta la carga del log para mostrarlo en campo tipo texto
        """
        log_data = '\n'.join(self._get_latest_n_minutes_odoo_log(int(self.tiempo)))
        _logger.info(u'Numero de lineas obtenidas: %s' % len(log_data))
        self.log_detail = log_data
        return True


    # Tiempos estandarizados para revision de logs
    _TIEMPO = [
        ('5',u'5 minutos'),
        ('10',u'10 minutos'),
        ('30',u'30 minutos'),
        ('60',u'1 hora'),
        ('180',u'3 horas'),
        ('360',u'6 horas'),
        ('720',u'12 horas'),
        ('1440',u'24 horas'),
    ]

    #Columns
    tiempo = fields.Selection(
        _TIEMPO,
        string=u'Tiempo de extraccion',
        help=u'El tiempo que se extraera del log para ser presentado'
        )
    log_detail = fields.Text(
        string=u'Log',
        help=u'Detalle del log del tiempo seleccionado'
        )
