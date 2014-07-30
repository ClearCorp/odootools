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

#This config params loading method is inspired in Odoo

#TODO: Change ConfigParser to configparser for python3 compat
import os, argparse, ConfigParser, ast
import logging

_logger = logging.getLogger('odootools.lib.config')
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
        self.params['odootools_path'] = '/usr/local/share/odootools'
        self.params['log_file'] = '/var/log/odootools/odootools.log'
        
        self.params_lists = ['config_file','log_handler']
        
        cmdline_args = self._get_cmdline_args()
        
        # config_files list has all files to read, in order of precedence
        config_files = ['/etc/odootools/settings.conf', '~/.odootools.conf']
        if 'config_file' in cmdline_args and cmdline_args.config_file:
            config_files += cmdline_args.config_file
        
        # Build list only with existing files
        self.config_files = []
        for config_file in config_files:
            if os.path.isfile(config_file):
                self.config_files.append(config_file)
        
        # Read config files from list
        config_files_params = self._read_config_files(self.config_files)
        
        # Add command config params from files to memory
        commands = []
        if 'command' in cmdline_args and cmdline_args.command:
            commands.append(cmdline_args.command)
        if 'additional_commands' in cmdline_args and cmdline_args.additional_commands:
            commands += cmdline_args.additional_commands
        
        # Add main sections and commands config params from files to memory
        for section in self.param_sections + commands:
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
        #         Also update the default-odootools.conf file.
        #WARNING: If you add or remove option groups remember to update the self.param_types dict and
        #         the self.param_setions.
        
        #Initialize argument parser
        parser = argparse.ArgumentParser(description='CLEARCORP Odoo admin scripts.', prog='odootools', add_help=False)
        
        # Main
        group = parser.add_argument_group('Main', 'Main parameters')
        self.param_sections.append('main')
        parser.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        parser.add_argument('--config-file', '-c', action="append", metavar="PATH", type=str, default=argparse.SUPPRESS,
                            help='Custom config file. This option can be repeated. The order in declared files states precedence of options.')
        parser.add_argument('--odootools-path', '-p', type=str, default=argparse.SUPPRESS,
                            help='Custom odootools installation path.')
        
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
        subparsers = parser.add_subparsers(dest='command', title='command', description='Valid Odoo Tools commands',
                            help='Command to execute (for help use "command --help")')
        
        #odootools-build
        subparser = subparsers.add_parser('odootools-build', help='Make a Odoo Tools installer .tgz file.', add_help=False)
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        group.add_argument('--target', '-t', type=str, default=argparse.SUPPRESS,
                            help='Target directory for building and writing the odootools.tgz file.')
        
        #odootools-install
        subparser = subparsers.add_parser('odootools-install', help='Install Odoo Tools.', add_help=False)
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        group.add_argument('--install-target-path', '-t', type=str, default=argparse.SUPPRESS,
                            help='Path to install Odoo Tools in (default: /usr/local/share/odootools).')
        group.add_argument('--install-config-path', type=str, default=argparse.SUPPRESS,
                            help='Path for the Odoo Tools config file in (default: /etc/odootools/settings.conf).')
        group.add_argument('--source-branch', '-s', type=str, default=argparse.SUPPRESS,
                            help='URL of the Odoo Tools branch to install from (default: https://github.com/CLEARCORP/odootools).')
        
        #odootools-update
        subparser = subparsers.add_parser('odootools-update', help='Update the installed Odoo Tools.', add_help=False)
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        group.add_argument('--source-branch', '-s', type=str, default=argparse.SUPPRESS,
                            help='URL of the Odoo Tools branch to update from (default: https://github.com/CLEARCORP/odootools).')
        
        #odootools-uninstall
        subparser = subparsers.add_parser('odootools-uninstall', help='Uninstall Odoo Tools.', add_help=False)
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        
        #odoo-install
        subparser = subparsers.add_parser('odoo-install', help='Install Odoo service.', add_help=False)
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        group.add_argument('--installation-type', '-i', choices=['dev','server'], default=argparse.SUPPRESS,
                            help='Server type (default: dev).')
        group.add_argument('--user', '-u', type=str, default=argparse.SUPPRESS,
                            help='User for development station installation.')
        group.add_argument('--branch', '-b', choices=['6.1', '7.0', '8.0', 'trunk'], default=argparse.SUPPRESS,
                            help='Odoo branch to install (default: 8.0).')
        # Addons
        group = subparser.add_argument_group('Addons', 'Addons to install')
        subgroup = group.add_mutually_exclusive_group()
        subgroup.add_argument('--odoo-clearcorp', '--clearcorp', dest='install_odoo_clearcorp', action='store_true', default=argparse.SUPPRESS,
                            help='Install odoo-clearcorp modules branch (https://github.com/CLEARCORP/odoo-clearcorp).')
        subgroup.add_argument('--no-odoo-clearcorp', '--no-clearcorp', dest='install_odoo_clearcorp', action='store_false', default=argparse.SUPPRESS,
                            help='Don\'t install odoo-clearcorp modules branch (https://github.com/CLEARCORP/odoo-clearcorp).')
        subgroup = group.add_mutually_exclusive_group()
        subgroup.add_argument('--odoo-costa-rica', '--l10n_cr', '--costa-rica', dest='install_odoo_costa_rica', action='store_true', default=argparse.SUPPRESS,
                            help='Install odoo-costa-rica modules branch (https://github.com/CLEARCORP/odoo-costa-rica).')
        subgroup.add_argument('--no-odoo-costa-rica', '--no-l10n_cr', '--no-costa-rica', dest='install_odoo_costa_rica', action='store_false', default=argparse.SUPPRESS,
                            help='Don\'t install odoo-costa-rica modules branch (https://github.com/CLEARCORP/odoo-costa-rica).')
        #Advanced
        group = subparser.add_argument_group('Advanced', 'Advanced options')
        subgroup = group.add_mutually_exclusive_group()
        subgroup.add_argument('--update-postgres-hba', '--hba', dest='update_postgres_hba', action='store_true', default=argparse.SUPPRESS,
                            help='Update PostgreSQL HBA file (default).')
        subgroup.add_argument('--no-update-postgres-hba', '--no-hba', dest='update_postgres_hba', action='store_false', default=argparse.SUPPRESS,
                            help='Don\'t update PostgreSQL HBA file.')
        subgroup = group.add_mutually_exclusive_group()
        subgroup.add_argument('--create-postgres-user', '--pg-user', dest='create_postgres_user', action='store_true', default=argparse.SUPPRESS,
                            help='Create PostgreSQL user (default).')
        subgroup.add_argument('--no-create-postgres-user', '--no-pg-user', dest='create_postgres_user', action='store_false', default=argparse.SUPPRESS,
                            help='Don\'t create PostgreSQL user.')
        subgroup.add_argument('--install-apache', '--apache', dest='install_apache', action='store_true', default=argparse.SUPPRESS,
                            help='Install Apache server (for reverse SSL proxy) (default).')
        subgroup.add_argument('--no-install-apache', '--no-apache', dest='install_apache', action='store_false', default=argparse.SUPPRESS,
                            help='Don\'t  install Apache server (for reverse SSL proxy).')
        group.add_argument('--repo-tgz', '-r', type=str, default=argparse.SUPPRESS,
                            help='Path of the Odoo Tools repo tgz file (default: None).')
        
        #odoo-update
        subparser = subparsers.add_parser('odoo-update', help='Update Odoo service.', add_help=False)
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        
        #odoo-uninstall
        subparser = subparsers.add_parser('odoo-uninstall', help='Uninstall Odoo service.', add_help=False)
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        
        
        #odoo-instance-make
        subparser = subparsers.add_parser('odoo-instance-make', help='Make an Odoo instance.', add_help=False)
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        group.add_argument('--name', '-n', type=str, required=True,
                            help='Name for the instance.')
        group.add_argument('--port', '-p', type=int, default=argparse.SUPPRESS,
                            help='Port number for the instance.')
        group.add_argument('--branch', '-b', choices=['6.1', '7.0', '8.0', 'trunk'], default=argparse.SUPPRESS,
                            help='Odoo branch to install (default: 8.0).')
        #Advanced
        group = subparser.add_argument_group('Advanced', 'Advanced options')
        subgroup = group.add_mutually_exclusive_group()
        subgroup.add_argument('--start-now', '--start', dest='start_now', action='store_true', default=argparse.SUPPRESS,
                            help='Start the instance now (default for server installation).')
        subgroup.add_argument('--no-start-now', '--no-start', dest='start_now', action='store_false', default=argparse.SUPPRESS,
                            help='Don\'t start the instance now (default for dev installation).')
        subgroup = group.add_mutually_exclusive_group()
        subgroup.add_argument('--on-boot', '--boot', dest='on_boot', action='store_true', default=argparse.SUPPRESS,
                            help='Start the instance on boot (default for server installation).')
        subgroup.add_argument('--no-on-boot', '--no-boot', dest='on_boot', action='store_false', default=argparse.SUPPRESS,
                            help='Don\'t start the instance on boot (default for dev installation).')
        group.set_defaults(additional_commands=['odoo-install'])
        
        #odoo-instance-remove
        subparser = subparsers.add_parser('odoo-instance-remove', help='Remove an Odoo instance.', add_help=False)
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        group.add_argument('--name', '-n', type=str, required=True,
                            help='Name for the instance.')
        
        #dev-repo-make
        subparser = subparsers.add_parser('dev-repo-make', help='Make the Odoo development git repository.', add_help=False)
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        group.add_argument('--repo-dir', '-d', type=str, default=argparse.SUPPRESS,
                            help='Directory for the dev repository (default: ~/Development/odoo).')
        
        #dev-repo-update
        subparser = subparsers.add_parser('dev-repo-update', help='Update the Odoo development git repository.', add_help=False)
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        group.add_argument('--repo-dir', '-d', type=str, default=argparse.SUPPRESS,
                            help='Directory for the dev repository (default: ~/Development/odoo).')
        
        #dev-repo-reset-locations
        subparser = subparsers.add_parser('dev-repo-reset-locations', help='Reset Odoo development repository branch locations.', add_help=False)
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        group.add_argument('--repo-dir', '-d', type=str, default=argparse.SUPPRESS,
                            help='Directory for the dev repository (default: ~/Development/odoo).')
        
        #dev-repo-src-make
        subparser = subparsers.add_parser('dev-repo-src-make', help='Make the Odoo development git source repository.', add_help=False)
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        group.add_argument('--repo-dir', '-d', type=str, default=argparse.SUPPRESS,
                            help='Directory for the dev repository (default: ~/Development/odoo).')
        
        #dev-repo-src-update
        subparser = subparsers.add_parser('dev-repo-src-update', help='Update the Odoo development git source repository.', add_help=False)
        # Main
        group = subparser.add_argument_group('Main', 'Main parameters')
        group.add_argument('--help', '-h', action='help', default=argparse.SUPPRESS,
                            help='Show this help message and exit.')
        group.add_argument('--repo-dir', '-d', type=str, default=argparse.SUPPRESS,
                            help='Directory for the dev repository (default: ~/Development/odoo).')
        
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
    
    #TODO review imports and methods 1 by 1
    def exec_function(self):
        if 'command' in self.params:
            command = self.params['command']
            if command == 'odootools-build':
                import odootools.install.make
                odootools.install.make.make_installer()
            elif command == 'odoo-install':
                import odootools.install.install #TODO
                odootools.install.install.install()
            elif command == 'odootools-update':
                import odootools.install.update #TODO
                odootools.install.update.update()
            elif command == 'odootools-uninstall':
                import odootools.lib.tools #TODO
                odootools.lib.tools.command_not_available()
            elif command == 'oerp-install':
                import odootools.oerp.server #TODO
                oerp_server = oerptools.oerp.server.oerpServer()
                oerp_server.install()
            elif command == 'oerp-update':
                import oerptools.lib.tools
                oerptools.lib.tools.command_not_available()
            elif command == 'oerp-uninstall':
                import oerptools.lib.tools
                oerptools.lib.tools.command_not_available()
            elif command == 'oerp-instance-make':
                import oerptools.oerp.instance
                oerp_instance = oerptools.oerp.instance.oerpInstance()
                oerp_instance.install()
            elif command == 'oerp-instance-remove':
                import oerptools.lib.tools
                oerptools.lib.tools.command_not_available()
            elif command == 'dev-repo-make':
                import oerptools.dev.repository
                repo = oerptools.dev.repository.repository()
                return repo.make()
            elif command == 'dev-repo-update':
                import oerptools.dev.repository
                repo = oerptools.dev.repository.repository()
                return repo.update()
            elif command == 'dev-repo-reset-locations':
                import oerptools.dev.repository
                repo = oerptools.dev.repository.repository()
                return repo.reset_branch_locations()
            elif command == 'dev-repo-src-make':
                import oerptools.dev.repository
                repo = oerptools.dev.repository.repository()
                return repo.src_make()
            elif command == 'dev-repo-src-update':
                import oerptools.dev.repository
                repo = oerptools.dev.repository.repository()
                return repo.src_update()
        else:
            return False
    
    def update_config_file_values(self, values, update_file=None):
        """Update the values in the specified config file.
        
        :params
        
        values dict: one key per section, each section is a dict.
        
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
        
        chmod_r = False
        try:
            config_file = open(file_path)
        except:
            try:
                import oerptools.lib.tools as tools
                tools.exec_command('chmod o+r %s' % file_path, as_root=True)
                chmod_r = True
                config_file = open(file_path)
            except:
                _logger.error('Failed to open config file for reading: %s' % file_path)
                return False
        
        new_file = ""
        section = False
        for line in config_file:
            _logger.debug('line: %s' % line)
            #Case: new section
            if re.match(r"^\[[^\s]*\]$",line):
                _logger.debug('New section: %s' % line[1:len(line)-2])
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
            _logger.debug('Some values remaining, last section: %s' % section)
            for section_key, section_value in copy_values.items():
                if section_value:
                    new_file += '\n#THE FOLLOWING SECTION WAS AUTOMATICALLY ADDED\n'
                    if not section_key == section:
                        new_file += "\n["+section_key+"]\n"
                    for key,value in section_value.items():
                        new_file += key+" = "+str(value)+'\n'
                    new_file += '\n\n'
                copy_values.pop(section_key)
        
        config_file.close()
        
        chmod_w = False
        try:
            config_file = open(file_path,'w')
            config_file.write(new_file)
            config_file.close()
        except:
            try:
                import oerptools.lib.tools as tools
                tools.exec_command('chmod o+w %s' % file_path, as_root=True)
                chmod_w = True
                config_file = open(file_path,'w')
                config_file.write(new_file)
                config_file.close()
            except:
                _logger.error('Failed to open config file for updating: %s' % file_path)
                return False
            
        #Check if chmod applied in order to restore perms
        if chmod_r == True:
            tools.exec_command('chmod o-r %s' % file_path, as_root=True)
        if chmod_w == True:
            tools.exec_command('chmod o-w %s' % file_path, as_root=True)
        
        return file_path

params = configParameters()
