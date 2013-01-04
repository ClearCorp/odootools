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

# Add the module oerptools to PYTHONPATH
# This is necesary in order to call the module without installing it
import sys, os, logging

logger = logging.getLogger('oerptools')
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

oerptools_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(oerptools_path+'/..')

from oerptools.lib import *
from oerptools.install import *

def read_args():
    import argparse
    parser = argparse.ArgumentParser(description='CLEARCORP OpenERP admin scripts.', prog='oerptools')
    
    # Logging
    parser_logging = parser.add_argument_group('Logging', 'Log parameters')
    parser_logging.add_argument('--log-level', '-L', dest='log_level', default='INFO', type=str,
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Minimun log level')
    parser_logging.add_argument('--console-log-level', dest='console_log_level', default=False, type=str,
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Minimun console log level')
    parser_logging.add_argument('--file-log-level', dest='file_log_level', default=False, type=str,
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Minimun file log level')
    
    # Commands
    subparsers = parser.add_subparsers(dest='command', title='command', description='Valid OERPTools commands',
                        help='Command to execute (for help use "command --help")')
    
    #oerptools-build
    oerptools_build_parser = subparsers.add_parser('oerptools-build', help='Make a OERPTools installer .tgz file.')
    #args go here
    #oerptools_build_parser.add_argument('arg')
    oerptools_build_parser.set_defaults(function=make.make_installer)
    
    #oerptools-update
    oerptools_update_parser = subparsers.add_parser('oerptools-update', help='Update the installed OERPTools.')
    #args go here
    #oerptools_build_parser.add_argument('arg')
    oerptools_update_parser.set_defaults(function=None)
    
    #oerptools-uninstall
    oerptools_uninstall_parser = subparsers.add_parser('oerptools-uninstall', help='Uninstall OERPTools.')
    #args go here
    #oerptools_build_parser.add_argument('arg')
    oerptools_uninstall_parser.set_defaults(function=None)
    
    
    #oerp-install
    oerp_install_parser = subparsers.add_parser('oerp-install', help='Install OpenERP service.')
    #args go here
    #oerptools_build_parser.add_argument('arg')
    oerp_install_parser.set_defaults(function=None)
    
    #oerp-update
    oerp_update_parser = subparsers.add_parser('oerp-update', help='Update OpenERP service.')
    #args go here
    #oerptools_build_parser.add_argument('arg')
    oerp_update_parser.set_defaults(function=None)
    
    #oerp-uninstall
    oerp_uninstall_parser = subparsers.add_parser('oerp-uninstall', help='Uninstall OpenERP service.')
    #args go here
    #oerptools_build_parser.add_argument('arg')
    oerp_uninstall_parser.set_defaults(function=None)
    
    
    #oerp-server-make
    oerp_server_make_parser = subparsers.add_parser('oerp-server-make', help='Make an OpenERP instance.')
    #args go here
    #oerptools_build_parser.add_argument('arg')
    oerp_server_make_parser.set_defaults(function=None)
    
    #oerp-server-remove
    oerp_server_remove_parser = subparsers.add_parser('oerp-server-remove', help='Remove an OpenERP instance.')
    #args go here
    #oerptools_build_parser.add_argument('arg')
    oerp_server_remove_parser.set_defaults(function=None)
    
    #oerp-repo-make
    oerp_repo_make_parser = subparsers.add_parser('oerp-repo-make', help='Make the OpenERP bzr repository in ~/Development/openerp.')
    #args go here
    #oerptools_build_parser.add_argument('arg')
    oerp_repo_make_parser.set_defaults(function=None)
    
    #oerp-repo-update
    oerp_repo_update_parser = subparsers.add_parser('oerp-repo-update', help='Update the OpenERP bzr repository in ~/Development/openerp.')
    #args go here
    #oerptools_build_parser.add_argument('arg')
    oerp_repo_update_parser.set_defaults(function=None)
    
    return parser.parse_args()

if __name__ == '__main__':

    if not tools.check_root():
        sys.stderr.write("This tool must be used as root. Aborting.\n")
        sys.exit(1)
    
    # Read configuration values
    config = read_args()
    
    # Set log level
    if config.console_log_level:
        log_console.setLevel(getattr(logging, config.console_log_level.upper()))
    else:
        log_console.setLevel(getattr(logging, config.log_level.upper()))
        
    if config.file_log_level:
        log_file.setLevel(getattr(logging, config.file_log_level.upper()))
    else:
        log_file.setLevel(getattr(logging, config.log_level.upper()))
    
    logger.debug('Searching the command invoked.')
    if not config.command:
        logger.debug('No command invoked, printing usage.')
        parser.print_usage()
    else:
        config.function(config)
        
