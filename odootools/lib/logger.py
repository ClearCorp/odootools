#!/usr/bin/python2
# -*- coding: utf-8 -*-
########################################################################
#
#  Odoo Tools by CLEARCORP S.A.
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

#This logger method is inspired in Odoo logger

import os, sys, logging, logging.handlers
import odootools.lib.config as config
import odootools.lib.tools as tools #TODO

_logger = logging.getLogger('odootools.lib.logger')
# create console handler with a higher log level
log_console = logging.StreamHandler()
log_console.setLevel(logging.WARNING)
# create formatter and add it to the handlers
log_console_formatter = logging.Formatter('%(levelname)s %(name)s: %(message)s')
log_console.setFormatter(log_console_formatter)
# add the handlers to the logger
_logger.addHandler(log_console)

class consoleColors (object):
    #Attributes
    RESET      = "0"
    BOLD       = "1"
    DIM        = "2"
    UNDERSCORE = "4"
    BLINK      = "5"
    REVERSE    = "7"
    HIDDEN     = "8"
    STROKE     = "9"

    #Foreground colors
    FG_BLACK   = "30"
    FG_RED     = "31"
    FG_GREEN   = "32"
    FG_YELLOW  = "33"
    FG_BLUE    = "34"
    FG_MAGENTA = "35"
    FG_CYAN    = "36"
    FG_WHITE   = "37"
    FG_DEFAULT = "39"
    #Light foreground colors
    FG_L_BLACK   = "90"
    FG_L_RED     = "91"
    FG_L_GREEN   = "92"
    FG_L_YELLOW  = "93"
    FG_L_BLUE    = "94"
    FG_L_MAGENTA = "95"
    FG_L_CYAN    = "96"
    FG_L_WHITE   = "97"
    FG_L_DEFAULT = "99"

    #Background colors
    BG_BLACK   = "40"
    BG_RED     = "41"
    BG_GREEN   = "42"
    BG_YELLOW  = "43"
    BG_BLUE    = "44"
    BG_MAGENTA = "45"
    BG_CYAN    = "46"
    BG_WHITE   = "47"
    BG_DEFAULT = "49"
    #Light background colors
    BG_L_BLACK   = "100"
    BG_L_RED     = "101"
    BG_L_GREEN   = "102"
    BG_L_YELLOW  = "103"
    BG_L_BLUE    = "104"
    BG_L_MAGENTA = "105"
    BG_L_CYAN    = "106"
    BG_L_WHITE   = "107"
    BG_L_DEFAULT = "109"
    
    def get_escape(self, codes):
        """Returns the escape secuence for the provided codes (list)."""
        seq = "\033["
        for code in codes:
            seq += code+";"
        #Replace last ; with an m
        return seq[:len(seq)-1] + "m"
    
    def get_reset(self):
        return "\033[0m"

_colors = consoleColors()

LEVEL_COLOR_MAPPING = {
    logging.DEBUG:      [_colors.FG_BLACK,    _colors.BG_WHITE],
    logging.INFO:       [_colors.FG_BLACK,  _colors.BG_L_GREEN],
    logging.WARNING:    [_colors.FG_BLACK,    _colors.BG_L_YELLOW],
    logging.ERROR:      [_colors.FG_L_WHITE,  _colors.BG_RED, _colors.BOLD],
    logging.CRITICAL:   [_colors.FG_L_WHITE,  _colors.BG_RED, _colors.BOLD],
}

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        record.levelname = _colors.get_escape(LEVEL_COLOR_MAPPING[record.levelno]) + record.levelname + _colors.get_reset()
        record.name = _colors.get_escape([_colors.FG_L_BLUE]) + record.name + _colors.get_reset()
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
        dirname = os.path.dirname(log_file)
        dir_exists = True
        if dirname and not os.path.isdir(dirname):
            dir_exists = False
            try:
                os.makedirs(dirname)
                dir_exists = True
            except:
                try:
                    tools.exec_command('mkdir %s' % dirname, as_root=True)
                    tools.exec_command('chmod a+rwx %s' % dirname, as_root=True)
                    dir_exists = True
                except:
                    _logger.error("Couldn't create the log file directory. Logging to the standard output.")
        
        if dir_exists:
            try:
                res['file_handler'] = logging.handlers.WatchedFileHandler(log_file)
            except:
                if dirname:
                    try:
                        tools.exec_command('chmod a+rwx %s' % dirname, as_root=True)
                        if os.path.isfile(log_file):
                            tools.exec_command('chmod a+rw %s' % log_file, as_root=True)
                        res['file_handler'] = logging.handlers.WatchedFileHandler(log_file)
                    except:
                        _logger.error("Couldn't create the log file. Logging to the standard output.")
                else:
                    _logger.error("Couldn't create the log file. Logging to the standard output.")

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
            pseudo_log_levels = ['odootools:DEBUG']
        elif log_level.lower() == 'info':
            pseudo_log_levels = ['odootools:INFO']
        elif log_level.lower() == 'warning':
            pseudo_log_levels = ['odootools:WARNING']
        elif log_level.lower() == 'error':
            pseudo_log_levels = ['odootools:ERROR']
        elif log_level.lower() == 'critical':
            pseudo_log_levels = ['odootools:CRITICAL']

    if 'log_handler' in config.params and config.params['log_handler']:
        log_handler = config.params['log_handler']
    else:
        log_handler = []

    res['log_hander_list'] = default_log_levels + pseudo_log_levels + log_handler
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
    
    #Force odootools.lib.config to reset handlers
    if not 'odootools.lib.config' in logger_info['log_hander_list']:
        logging.getLogger('odootools.lib.config').handlers = []
    #Force odootools.lib.logger to reset handlers
    if not 'odootools.lib.logger' in logger_info['log_hander_list']:
        logging.getLogger('odootools.lib.logger').handlers = []

logger_info = load_info()
