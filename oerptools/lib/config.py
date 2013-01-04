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

#This config params loading method is inspired in OpenERP Server

#TODO: Change ConfigParser to configparser for python3 compat
import argparse, ConfigParser, logging
logger = logging.getLogger('oerptools.lib.config')

from oerptools.install import make

#This class is initialized before initialization of the loggers, beware of this.
class configParameters(object):
    def __init__(self):
        self.params = {}
        # Required default options.
        self.params['main'] = {
            'oerptools_path': '/usr/local/share/oerptools',
        }
        
        cmdline_parser, cmdline_args = self._get_cmdline_args()
        
        # config_files list has all files to read, in order of precedence
        config_files = ['/etc/oerptools/settings.conf']
        
        if 'config_file' in cmdline_args:
            config_files.append(cmdline_args.config_file)
        
        config_files_params = self._read_config_files(config_files)
        
        for section in config_files_params:
            for (key, value) in section.items():
                self.params[section][key] = value
        
        for group in cmdline_args.option_groups
        
    def __getitem__(self, item):
        return self.options[item]
        
    def __setitem__(self, key, value):
        self.options[key] = value
    
    def __contains__(self, key):
        return key in self.params
    
    def _function_not_implemented(self):
        return True
        
    def _get_cmdline_args(self):
        #Initialize argument parser
        parser = argparse.ArgumentParser(description='CLEARCORP OpenERP admin scripts.', prog='oerptools', add_help=False)
        
        arguments = {}
        
        # Main
        group = parser.add_argument_group('Main', 'Main parameters')
        arguments['main'] = {}
        parser.add_argument('--help', '-h', action='help',
                            help='Show this help message and exit.')
        parser.add_argument('--oerptools-path', '-p', dest='oerptools_path', type=str, default='/usr/local/share/oerptools',
                            help='Custom oerptools installation path.')
        
        # Logging
        group = parser.add_argument_group('Logging', 'Log parameters')
        arguments['logging'] = {}
        group.add_argument('--log-file', dest='log_file', type=argparse.FileType('a+'), default=None,
                            help='Log file.')
        group.add_argument('--log-level', '-L', dest='log_level', default='INFO', type=str,
                            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                            help='General log level.')
        group.add_argument('--stdout-log-level', dest='stdout_log_level', default='INFO', type=str,
                            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                            help='Standard out (console) log level, (overwrite general log level).')
        group.add_argument('--file-log-level', dest='file_log_level', default='INFO', type=str,
                            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                            help='File log level, (overwrite general log level).')
        
        # Commands
        subparsers = parser.add_subparsers(dest='command', title='command', description='Valid OERPTools commands',
                            help='Command to execute (for help use "command --help")')
        
        #oerptools-build
        subparser = subparsers.add_parser('oerptools-build', help='Make a OERPTools installer .tgz file.', add_help=False)
        arguments['oerptools-build'] = {}
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        arguments['oerptools-build']['main'] = {}
        group.add_argument('--help', '-h', action='help',
                            help='Show this help message and exit.')
        subparser.set_defaults(function=make.make_installer)
        
        #oerptools-update
        subparser = subparsers.add_parser('oerptools-update', help='Update the installed OERPTools.', add_help=False)
        arguments['oerptools-update'] = {}
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help',
                            help='Show this help message and exit.')
        subparser.set_defaults(function=self._function_not_implemented)
        
        #oerptools-uninstall
        subparser = subparsers.add_parser('oerptools-uninstall', help='Uninstall OERPTools.', add_help=False)
        arguments['oerptools-uninstall'] = {}
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help',
                            help='Show this help message and exit.')
        subparser.set_defaults(function=self._function_not_implemented)
        
        
        #oerp-install
        subparser = subparsers.add_parser('oerp-install', help='Install OpenERP service.', add_help=False)
        arguments['oerp-install'] = {}
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help',
                            help='Show this help message and exit.')
        subparser.set_defaults(function=self._function_not_implemented)
        
        #oerp-update
        subparser = subparsers.add_parser('oerp-update', help='Update OpenERP service.', add_help=False)
        arguments['oerp-update'] = {}
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help',
                            help='Show this help message and exit.')
        subparser.set_defaults(function=self._function_not_implemented)
        
        #oerp-uninstall
        subparser = subparsers.add_parser('oerp-uninstall', help='Uninstall OpenERP service.', add_help=False)
        arguments['oerp-uninstall'] = {}
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help',
                            help='Show this help message and exit.')
        subparser.set_defaults(function=self._function_not_implemented)
        
        
        #oerp-server-make
        subparser = subparsers.add_parser('oerp-server-make', help='Make an OpenERP instance.', add_help=False)
        arguments['oerp-server-make'] = {}
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help',
                            help='Show this help message and exit.')
        subparser.set_defaults(function=self._function_not_implemented)
        
        #oerp-server-remove
        subparser = subparsers.add_parser('oerp-server-remove', help='Remove an OpenERP instance.', add_help=False)
        arguments['oerp-server-remove'] = {}
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help',
                            help='Show this help message and exit.')
        subparser.set_defaults(function=self._function_not_implemented)
        
        #oerp-repo-make
        subparser = subparsers.add_parser('oerp-repo-make', help='Make the OpenERP bzr repository in ~/Development/openerp.', add_help=False)
        arguments['oerp-repo-make'] = {}
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help',
                            help='Show this help message and exit.')
        subparser.set_defaults(function=self._function_not_implemented)
        
        #oerp-repo-update
        subparser = subparsers.add_parser('oerp-repo-update', help='Update the OpenERP bzr repository in ~/Development/openerp.', add_help=False)
        arguments['oerp-repo-update'] = {}
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help',
                            help='Show this help message and exit.')
        subparser.set_defaults(function=self._function_not_implemented)
        
        return parser, parser.parse_args()
    
    def _read_config_files(self, file_list):
        parser = ConfigParser.ConfigParser()
        params = {}
        try:
            parser.read(file_list)
            for section in parser.sections():
                for (key, value) in parser.items(section):
                    params[section][key] = value
        except IOError:
            pass
        except ConfigParser.NoSectionError:
            pass
        return params

params = configParameters()
