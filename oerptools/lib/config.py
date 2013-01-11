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
import argparse, ConfigParser, ast

import logging
_logger = logging.getLogger('oerptools.lib.config')
# create console handler with a higher log level
log_console = logging.StreamHandler()
log_console.setLevel(logging.WARNING)
# create formatter and add it to the handlers
log_console_formatter = logging.Formatter('%(levelname)s %(name)s: %(message)s')
log_console.setFormatter(log_console_formatter)
# add the handlers to the logger
_logger.addHandler(log_console)

#This class is initialized before initialization of the loggers, beware of this.
class configParameters(object):
    def __init__(self):
        self.params = {}
        self.param_sections = []
        # Required default options.
        self.params['oerptools_path'] = '/usr/local/share/oerptools'
        self.params['log_file'] = '/var/log/oerptools/oerptools.log'
        
        cmdline_args = self._get_cmdline_args()
        
        # config_files list has all files to read, in order of precedence
        config_files = ['/etc/oerptools/settings.conf', '~/.oerptools.conf']
        if 'config_file' in cmdline_args and cmdline_args.config_file:
            config_files.append(cmdline_args.config_file)
        
        # Read config files from list
        config_files_params = self._read_config_files(config_files)
        
        # Add main sections config params from files to memory
        for section in self.param_sections:
            if section in config_files_params:
                for key, value in config_files_params[section].items():
                    try:
                        self.params[key] = ast.literal_eval(value)
                    except:
                        self.params[key] = value
        # Add command config params from files to memory
        if 'command' in cmdline_args and cmdline_args.command and cmdline_args.command in config_files_params:
            for key, value in config_files_params[cmdline_args.command]:
                self.params[key] = value
        
        # Read params from command line (overwrite params from files)
        for key, arg in cmdline_args.__dict__.iteritems():
            self.params[key] = arg
        
        
    def __getitem__(self, item):
        return self.params[item]
        
    def __setitem__(self, key, value):
        self.params[key] = value
    
    def __contains__(self, key):
        return key in self.params
        
    def _get_cmdline_args(self):
        """ Reads and parses command line arguments.
        
        Return namespace: parse_args() namespace with the arguments information parsed.
        """
        #WARNING: If you add or remove options remember to update the self.param_types dict.
        #WARNING: If you add or remove option groups remember to update the self.param_types dict and
        #         the self.param_setions.
        
        #Initialize argument parser
        parser = argparse.ArgumentParser(description='CLEARCORP OpenERP admin scripts.', prog='oerptools', add_help=False)
        
        # Main
        group = parser.add_argument_group('Main', 'Main parameters')
        self.param_sections.append('main')
        parser.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        parser.add_argument('--config-file', '-c', type=str, default=argparse.SUPPRESS,
                            help='Custom config file.')
        parser.add_argument('--oerptools-path', '-p', type=str, default=argparse.SUPPRESS,
                            help='Custom oerptools installation path.')
        
        # Logging
        group = parser.add_argument_group('Logging', 'Log parameters')
        self.param_sections.append('logging')
        group.add_argument('--log-file', type=str, default=argparse.SUPPRESS,
                            help='Log file.')
        group.add_argument('--log-level', '-L', type=str, default=argparse.SUPPRESS,
                            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                            help='General log level.')
        group.add_argument('--stdout-log-level', type=str, default=argparse.SUPPRESS,
                            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                            help='Standard out (console) log level, (overwrite general log level).')
        group.add_argument('--file-log-level', type=str, default=argparse.SUPPRESS,
                            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                            help='File log level, (overwrite general log level).')
        group.add_argument('--log-handler', action="append", metavar="PREFIX:LEVEL", default=argparse.SUPPRESS,
                            help='Setup a handler at LEVEL for a given PREFIX. An empty PREFIX indicates the root logger. This option can be repeated. Example: "oerptools.install.make:DEBUG" or "oerptools.oerp.install:CRITICAL" (default: ":INFO")')

        
        
        
        # Commands
        subparsers = parser.add_subparsers(dest='command', title='command', description='Valid OERPTools commands',
                            help='Command to execute (for help use "command --help")')
        
        #oerptools-build
        subparser = subparsers.add_parser('oerptools-build', help='Make a OERPTools installer .tgz file.', add_help=False)
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        group.add_argument('--target', '-t', type=str, required=True,
                            help='Target directory for building and writing the oerptools.tgz file.')
        
        #oerptools-install
        subparser = subparsers.add_parser('oerptools-install', help='Install OERPTools.', add_help=False)
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        group.add_argument('--oerptools-path', '-p', type=str, default=argparse.SUPPRESS,
                            help='Path to install OERPTools in (default: /usr/local/share/oerptools).')
        
        #oerptools-update
        subparser = subparsers.add_parser('oerptools-update', help='Update the installed OERPTools.', add_help=False)
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        
        #oerptools-uninstall
        subparser = subparsers.add_parser('oerptools-uninstall', help='Uninstall OERPTools.', add_help=False)
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        
        
        #oerp-install
        subparser = subparsers.add_parser('oerp-install', help='Install OpenERP service.', add_help=False)
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        
        #oerp-update
        subparser = subparsers.add_parser('oerp-update', help='Update OpenERP service.', add_help=False)
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        
        #oerp-uninstall
        subparser = subparsers.add_parser('oerp-uninstall', help='Uninstall OpenERP service.', add_help=False)
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        
        
        #oerp-server-make
        subparser = subparsers.add_parser('oerp-server-make', help='Make an OpenERP instance.', add_help=False)
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        
        #oerp-server-remove
        subparser = subparsers.add_parser('oerp-server-remove', help='Remove an OpenERP instance.', add_help=False)
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        
        #oerp-repo-make
        subparser = subparsers.add_parser('oerp-repo-make', help='Make the OpenERP bzr repository in ~/Development/openerp.', add_help=False)
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        
        #oerp-repo-update
        subparser = subparsers.add_parser('oerp-repo-update', help='Update the OpenERP bzr repository in ~/Development/openerp.', add_help=False)
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        
        return parser.parse_args()
    
    def _read_config_files(self, file_list):
        parser = ConfigParser.ConfigParser()
        params = {}
        try:
            parser.read(file_list)
            for section in parser.sections():
                if not section in params:
                    params[section] = {}
                for (key, value) in parser.items(section):
                    params[section][key] = value
        except IOError:
            pass
        except ConfigParser.NoSectionError:
            pass
        return params
    
    def exec_function(self):
        if 'command' in self.params:
            command = self.params['command']
            if command == 'oerptools-build':
                import oerptools.install.make
                oerptools.install.make.make_installer()
            elif command == 'oerptools-install':
                import oerptools.install.install
                oerptools.install.install.install()
            elif command == 'oerptools-update':
                import oerptools.install.update
                oerptools.install.update.update()
            elif command == 'oerptools-uninstall':
                import oerptools.lib.tools
                oerptools.lib.tools.command_not_available()
            elif command == 'oerp-install':
                import oerptools.lib.tools
                oerptools.lib.tools.command_not_available()
            elif command == 'oerp-update':
                import oerptools.lib.tools
                oerptools.lib.tools.command_not_available()
            elif command == 'oerp-uninstall':
                import oerptools.lib.tools
                oerptools.lib.tools.command_not_available()
            elif command == 'oerp-server-make':
                import oerptools.lib.tools
                oerptools.lib.tools.command_not_available()
            elif command == 'oerp-server-remove':
                import oerptools.lib.tools
                oerptools.lib.tools.command_not_available()
            elif command == 'oerp-repo-make':
                import oerptools.lib.tools
                oerptools.lib.tools.command_not_available()
            elif command == 'oerp-repo-update':
                import oerptools.lib.tools
                oerptools.lib.tools.command_not_available()
        else:
            return False

params = configParameters()
