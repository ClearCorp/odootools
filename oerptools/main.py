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
import sys, os

global _oerptools_path
_oerptools_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(_oerptools_path+'/..')

from oerptools.lib import *
from oerptools.install import *

def print_commands ():
    print('''
    
OERPTools command list:
  oerptools-build
  oerptools-install
  oerptools-update
  oerptools-uninstall
  
  oerp-install
  oerp-update
  oerp-uninstall
  
  oerp-server-make
  oerp-server-remove
  
  oerp-repo-make
  oerp-repo-update
''')

if __name__ == '__main__':

    if not tools.check_root():
        sys.stderr.write("This tool must be used as root. Aborting.\n")
        sys.exit(1)
    
    import argparse
    parser = argparse.ArgumentParser(description='CLEARCORP OpenERP admin scripts.', prog='oerptools')
    parser.add_argument('command', metavar='COMMAND', nargs='?',
                        help='Command to execute (see --help-commands)')
    parser.add_argument('--help-commands', dest='help_commands', action='store_true', default=False,
                        help='List available commands')
    parser.add_argument('command_args', metavar='args', nargs=argparse.REMAINDER,
                        help=argparse.SUPPRESS)
                   
    args = parser.parse_args()
    if args.help_commands:
        print_commands()
        sys.exit(0)
    elif args.command == 'oerptools-build':
        make.make_installer()
    else:
        parser.print_usage()
        
