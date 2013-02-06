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
import os, argparse, ConfigParser, ast

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
        
        self.params_lists = ['config_file','log_handler']
        
        cmdline_args = self._get_cmdline_args()
        
        # config_files list has all files to read, in order of precedence
        config_files = ['/etc/oerptools/settings.conf', '~/.oerptools.conf']
        if 'config_file' in cmdline_args and cmdline_args.config_file:
            config_files += cmdline_args.config_file
        
        # Build list only with existing files
        self.config_files = []
        for config_file in config_files:
            if os.path.isfile(config_file):
                self.config_files.append(config_file)
        
        # Read config files from list
        config_files_params = self._read_config_files(self.config_files)
        
        # Add main sections config params from files to memory
        for section in self.param_sections:
            if section in config_files_params:
                for key, value in config_files_params[section].items():
                    #check if value should be a list
                    if key in self.params_lists:
                        if key not in self.params:
                            self.params[key] = []
                        try:
                            parsed_value = ast.literal_eval(value)
                        except:
                            parsed_value = value
                        finally:
                            if isinstance(parsed_value, list):
                                self.params[key] += parsed_value
                            else:
                                self.params[key].append(parsed_value)
                    else:
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
        if item in self.params:
            return self.params[item]
        else:
            return None
    
    def __setitem__(self, key, value):
        self.params[key] = value
    
    def __contains__(self, key):
        return key in self.params
    
    def _get_cmdline_args(self):
        """ Reads and parses command line arguments.
        
        Return namespace: parse_args() namespace with the arguments information parsed.
        """
        #WARNING: If you add or remove options remember to update the self.param_types dict.
        #         Also update the default-oerptools.conf file.
        #WARNING: If you add or remove option groups remember to update the self.param_types dict and
        #         the self.param_setions.
        
        #Initialize argument parser
        parser = argparse.ArgumentParser(description='CLEARCORP OpenERP admin scripts.', prog='oerptools', add_help=False)
        
        # Main
        group = parser.add_argument_group('Main', 'Main parameters')
        self.param_sections.append('main')
        parser.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        parser.add_argument('--config-file', '-c', action="append", metavar="PATH", type=str, default=argparse.SUPPRESS,
                            help='Custom config file. This option can be repeated. The order in declared files states precedence of options.')
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
        group.add_argument('--target', '-t', type=str, default=argparse.SUPPRESS,
                            help='Target directory for building and writing the oerptools.tgz file.')
        
        #oerptools-install
        subparser = subparsers.add_parser('oerptools-install', help='Install OERPTools.', add_help=False)
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        group.add_argument('--install-target-path', '-t', type=str, default=argparse.SUPPRESS,
                            help='Path to install OERPTools in (default: /usr/local/share/oerptools).')
        group.add_argument('--install-config-path', type=str, default=argparse.SUPPRESS,
                            help='Path for the OERPTools config file in (default: /etc/oerptools/settings.conf).')
        group.add_argument('--source-branch', '-s', type=str, default=argparse.SUPPRESS,
                            help='URL of the OERPTools branch to install from (default: lp:oerptools).')
        
        #oerptools-update
        subparser = subparsers.add_parser('oerptools-update', help='Update the installed OERPTools.', add_help=False)
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        group.add_argument('--source-branch', '-s', type=str, default=argparse.SUPPRESS,
                            help='URL of the OERPTools branch to update from (default: lp:oerptools).')
        
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
        group.add_argument('--installation-type', '-i', choices=['dev','server'], default='dev',
                            help='Server type (default: dev).')
        group.add_argument('--user', '-u', type=str, default=argparse.SUPPRESS,
                            help='User for development station installation.')
        group.add_argument('--branch', '-b', choices=['5.0','6.0', '6.1', '7.0', 'trunk'], default=argparse.SUPPRESS,
                            help='OpenERP branch to install (default: 7.0).')
        # Addons
        group = subparser.add_argument_group('Addons', 'Addons to install')
        subgroup = group.add_mutually_exclusive_group()
        subgroup.add_argument('--openobject-addons', dest='install_openobject_addons', action='store_true',
                            help='Install openobject-addons modules branch (lp:openobject-addons).')
        subgroup.add_argument('--no-openobject-addons', dest='install_openobject_addons', action='store_false',
                            help='Don\'t install openobject-addons modules branch (lp:openobject-addons).')
        subgroup = group.add_mutually_exclusive_group()
        subgroup.add_argument('--openerp-ccorp-addons', '--ccorp', dest='install_openerp_ccorp_addons', action='store_true',
                            help='Install openerp-ccorp-addons modules branch (lp:openerp-ccorp-addons).')
        subgroup.add_argument('--no-openerp-ccorp-addons', '--no-ccorp', dest='install_openerp_ccorp_addons', action='store_false',
                            help='Don\'t install openerp-ccorp-addons modules branch (lp:openerp-ccorp-addons).')
        subgroup = group.add_mutually_exclusive_group()
        subgroup.add_argument('--openerp-costa-rica', '--l10n_cr', '--costa-rica', dest='install_openerp_costa_rica', action='store_true',
                            help='Install openerp-costa-rica modules branch (lp:openerp-costa-rica).')
        subgroup.add_argument('--no-openerp-costa-rica', '--no-l10n_cr', '--no-costa-rica', dest='install_openerp_costa_rica', action='store_false',
                            help='Don\'t install openerp-costa-rica modules branch (lp:openerp-costa-rica).')
        group.set_defaults(install_openobject_addons=True, install_openerp_ccorp_addons=True, install_openerp_costa_rica=True)
        #Advanced
        group = subparser.add_argument_group('Advanced', 'Advanced options')
        subgroup = group.add_mutually_exclusive_group()
        subgroup.add_argument('--update-postgres-hba', '--hba', dest='update_postgres_hba', action='store_true',
                            help='Update PostgreSQL HBA file (default).')
        subgroup.add_argument('--no-update-postgres-hba', '--no-hba', dest='update_postgres_hba', action='store_false',
                            help='Don\'t update PostgreSQL HBA file.')
        subgroup = group.add_mutually_exclusive_group()
        subgroup.add_argument('--create-postgres-user', '--pg-user', dest='create_postgres_user', action='store_true',
                            help='Create PostgreSQL user (default).')
        subgroup.add_argument('--no-create-postgres-user', '--no-pg-user', dest='create_postgres_user', action='store_false',
                            help='Don\'t create PostgreSQL user.')
        subgroup.add_argument('--install-apache', '--apache', dest='install_apache', action='store_true',
                            help='Install Apache server (for reverse SSL proxy) (default).')
        subgroup.add_argument('--no-install-apache', '--no-apache', dest='install_apache', action='store_false',
                            help='Don\'t  install Apache server (for reverse SSL proxy) (default).')
        group.set_defaults(update_postgres_hba=True, create_postgres_user=True, install_apache=True)
        
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
                    params[section][key.replace('-','_')] = value
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
                import oerptools.oerp.server
                oerptools.oerp.server.oerp_server.install()
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
    
    def update_config_file_values(self, values, update_file=None):
        """Update the values in the specified config file.
        
        :params
        
        values dict: one key per section, each section is a dict .
        
        file str: Config file to update.
        """
        import copy,re
        copy_values = copy.deepcopy(values)
        
        if update_file:
            file_path = update_file
        else:
            if not self.config_files:
                _logger.warning('Not saving values, config file unknown.')
                return False
            else:
                file_path = self.config_files[-1]
        
        try:
            config_file = open(file_path)
        except:
            _logger.error('Failed to open config file for reading: %s' % file_path)
            return False
        
        new_file = ""
        section = False
        for line in config_file:
            #Case: new section
            if re.match(r"^\[[^\s]*\]$",line):
                #Check to see if there is still values to update in last section
                if section and section in copy_values and copy_values[section]:
                    new_file += '\n#THE FOLLOWING VALUES WHERE AUTOMATICALLY ADDED\n'
                    for key, value in copy_values[section].items():
                        new_file += key+' = '+str(value)+'\n'
                    new_file += '\n\n'
                    copy_values.pop(section)
                #Check if section present but empty
                elif section and section in copy_values:
                    copy_values.pop(section)
                new_file += line
                section = line[1:len(line)-2]
            #Case: no new section, no actual section
            elif not section:
                new_file += line
            #Case: actual section in copy_values
            elif section and section in copy_values:
                #Case: value line
                value_match = re.match(r"^[\s]*([^\s=:;#]+)",line)
                commented_value_match = re.match(r"^[\s]*[#;]+[\s]*([^\s=:;#]+)",line)
                if value_match:
                    #Case: line value is in copy_values to update
                    if value_match.group(1).replace('-','_') in copy_values[section]:
                        new_file += value_match.group(1)+' = '+str(copy_values[section].pop(value_match.group(1)))+'\n'
                    else:
                        new_file += line
                #Case: commented value line
                elif commented_value_match:
                    #Case: line value is in copy_values to update
                    if commented_value_match.group(1).replace('-','_') in copy_values[section]:
                        new_file += commented_value_match.group(1)+' = '+str(copy_values[section].pop(commented_value_match.group(1)))+'\n'
                    else:
                        new_file += line
                #Case: other line, comments
                else:
                    new_file += line
            #Case: no actual section, no new section
            else:
                new_file += line
        
        #Check to see if all copy_values where updated
        if copy_values:
            for section_key,section in copy_values.items():
                if section:
                    new_file += '\n#THE FOLLOWING SECTION WAS AUTOMATICALLY ADDED\n'
                    new_file += "\n"+section_key+"\n"
                    for key,value in section.items():
                        new_file += key+" = "+str(value)+'\n'
                    new_file += '\n\n'
                copy_values.pop(section_key)
        
        config_file.close()
        
        try:
            config_file = open(file_path,'w')
            config_file.write(new_file)
            config_file.close()
        except:
            _logger.error('Failed to open config file for updating: %s' % file_path)
            return False
        return True
    
params = configParameters()
