#!/usr/bin/python2
# -*- coding: utf-8 -*-
########################################################################
#
#  OpenERP Tools by CLEARCORP S.A.
#  Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public
#  License along with this program.  If not, see 
#  <http://www.gnu.org/licenses/>.
#
########################################################################

#This logger method is inspired in OpenERP logger

import os, sys, logging
import config

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, _NOTHING, DEFAULT = range(10)
#The background is set with 40 plus the number of the color, and the foreground with 30
#These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"
COLOR_PATTERN = "%s%s%%s%s" % (COLOR_SEQ, COLOR_SEQ, RESET_SEQ)
LEVEL_COLOR_MAPPING = {
    logging.DEBUG: (BLUE, DEFAULT),
    logging.INFO: (GREEN, DEFAULT),
    logging.WARNING: (YELLOW, DEFAULT),
    logging.ERROR: (RED, DEFAULT),
    logging.CRITICAL: (WHITE, RED),
}

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        fg_color, bg_color = LEVEL_COLOR_MAPPING[record.levelno]
        record.levelname = COLOR_PATTERN % (30 + fg_color, 40 + bg_color, record.levelname)
        return logging.Formatter.format(self, record)


def init_logger():

    # Format for both file and stout logging
    file_log_format = '%(asctime)s %(levelname)s %(name)s: %(message)s'
    stout_log_format = '%(levelname)s %(name)s: %(message)s'

    if 'log_file' in config.params:
        # LogFile Handler
        logf = tools.config['logfile']
        try:
            dirname = os.path.dirname(logf)
            if dirname and not os.path.isdir(dirname):
                os.makedirs(dirname)
            if tools.config['logrotate'] is not False:
                handler = logging.handlers.TimedRotatingFileHandler(logf,'D',1,30)
            elif os.name == 'posix':
                handler = logging.handlers.WatchedFileHandler(logf)
            else:
                handler = logging.handlers.FileHandler(logf)
        except Exception:
            sys.stderr.write("ERROR: couldn't create the logfile directory. Logging to the standard output.\n")
            handler = logging.StreamHandler(sys.stdout)
    else:
        # Normal Handler on standard output
        handler = logging.StreamHandler(sys.stdout)

    if isinstance(handler, logging.StreamHandler) and os.isatty(handler.stream.fileno()):
        formatter = ColoredFormatter(format)
    else:
        formatter = DBFormatter(format)
    handler.setFormatter(formatter)

    # Configure handlers
    default_config = [
        'openerp.netsvc.rpc.request:INFO',
        'openerp.netsvc.rpc.response:INFO',
        'openerp.addons.web.common.http:INFO',
        'openerp.addons.web.common.openerplib:INFO',
        'openerp.sql_db:INFO',
        ':INFO',
    ]

    logconfig = tools.config['log_handler']

    for logconfig_item in default_config + pseudo_config + logconfig:
        loggername, level = logconfig_item.split(':')
        level = getattr(logging, level, logging.INFO)
        logger = logging.getLogger(loggername)
        logger.handlers = []
        logger.setLevel(level)
        logger.addHandler(handler)
        if loggername != '':
            logger.propagate = False

    for logconfig_item in default_config + pseudo_config + logconfig:
        _logger.debug('logger level set: "%s"', logconfig_item)







'''
    
    # Set log level
    if config.console_log_level:
        log_console.setLevel(getattr(logging, config.console_log_level.upper()))
    else:
        log_console.setLevel(getattr(logging, config.log_level.upper()))
        
    if config.file_log_level:
        log_file.setLevel(getattr(logging, config.file_log_level.upper()))
    else:
        log_file.setLevel(getattr(logging, config.log_level.upper()))
        
        


logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
log_file = logging.FileHandler('setup.log')
log_file.setLevel(logging.DEBUG)
# create console handler with a higher log level
log_console = logging.StreamHandler()
log_console.setLevel(logging.INFO)
# create formatter and add it to the handlers
log_file_formatter = logging.Formatter('%(asctime)s %(levelname)s - %(name)s: %(message)s')
log_console_formatter = logging.Formatter('%(levelname)s - %(name)s: %(message)s')
log_file.setFormatter(log_file_formatter)
log_console.setFormatter(log_console_formatter)
# add the handlers to the logger
logger.addHandler(log_file)
logger.addHandler(log_console)
'''
