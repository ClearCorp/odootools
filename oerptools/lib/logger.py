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

import os, sys, logging, logging.handlers
import oerptools.lib.config as config

_logger = logging.getLogger('oerptools.lib.logger')

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, _NOTHING, DEFAULT = range(10)
#The background is set with 40 plus the number of the color, and the foreground with 30
#These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"
COLOR_PATTERN = "%s%s%%s%s" % (COLOR_SEQ, COLOR_SEQ, RESET_SEQ)
LEVEL_COLOR_MAPPING = {
    logging.DEBUG: (BLUE, DEFAULT),
    logging.INFO: (WHITE, GREEN),
    logging.WARNING: (YELLOW, DEFAULT),
    logging.ERROR: (RED, DEFAULT),
    logging.CRITICAL: (WHITE, RED),
}

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        fg_color, bg_color = LEVEL_COLOR_MAPPING[record.levelno]
        record.levelname = COLOR_PATTERN % (30 + fg_color, 40 + bg_color, record.levelname)
        return logging.Formatter.format(self, record)

def load_info():
    res = {}
    
    # Format for both file and stout logging
    res['file_log_format'] = '%(asctime)s %(levelname)s %(name)s: %(message)s'
    res['stdout_log_format'] = '%(levelname)s %(name)s: %(message)s'

    res['file_handler'] = False
    res['stdout_handler'] = logging.StreamHandler()
    
    # Set log file handler if needed
    if 'log_file' in config.params and config.params['log_file']:
        # LogFile Handler
        log_file = config.params['log_file']
        try:
            dirname = os.path.dirname(log_file)
            if dirname and not os.path.isdir(dirname):
                os.makedirs(dirname)
            res['file_handler'] = logging.handlers.WatchedFileHandler(log_file)
        except Exception:
            sys.stderr.write("ERROR: couldn't create the logfile directory. Logging to the standard output.\n")

    # Set formatters
    if os.isatty(res['stdout_handler'].stream.fileno()):
        res['stdout_handler'].setFormatter(ColoredFormatter(res['stdout_log_format']))
    else:
        res['stdout_handler'].setFormatter(logging.Formatter(res['stdout_log_format']))
    if res['file_handler']:
        res['file_handler'].setFormatter(logging.Formatter(res['file_log_format']))

    # Configure levels
    default_log_levels = [
        ':INFO',
    ]
    
    # Initialize pseudo log levels for easy log-level config param
    pseudo_log_levels = []
    if 'log_level' in config.params and config.params['log_level']:
        log_level = config.params['log_level']
        if log_level.lower() == 'debug':
            pseudo_log_levels = ['oerptools:DEBUG']
        elif log_level.lower() == 'info':
            pseudo_log_levels = ['oerptools:INFO']
        elif log_level.lower() == 'warning':
            pseudo_log_levels = ['oerptools:WARNING']
        elif log_level.lower() == 'error':
            pseudo_log_levels = ['oerptools:ERROR']
        elif log_level.lower() == 'critical':
            pseudo_log_levels = ['oerptools:CRITICAL']

    if 'log_handler' in config.params and config.params['log_handler']:
        log_handler = config.params['log_handler']
    else:
        log_handler = []

    res['log_hander_list'] = default_log_levels + pseudo_log_levels + log_handler
    # Force bzr:INFO if no bzr handler
    res['log_hander_list'] = ['bzr:INFO'] + res['log_hander_list']
    return res

def set_levels():
    for log_handler_item in logger_info['log_hander_list']:
        loggername, level = log_handler_item.split(':')
        level = getattr(logging, level, logging.INFO)
        item_logger = logging.getLogger(loggername)
        item_logger.handlers = []
        item_logger.setLevel(level)
        if logger_info['file_handler']:
            item_logger.addHandler(logger_info['file_handler'])
        item_logger.addHandler(logger_info['stdout_handler'])
        if loggername != '':
            item_logger.propagate = False

    for log_handler_item in logger_info['log_hander_list']:
        _logger.debug('logger level set: "%s"', log_handler_item)

logger_info = load_info()
