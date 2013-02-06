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

import logging
_logger = logging.getLogger('oerptools.oerp.install')

import os, datetime, pwd, getpass, re

from oerptools.lib import config, bzr, tools

class oerpServer(object):
    
    def install(self):
        _logger.info('OpenERP server installation started.')
        
        _logger.debug('Checking if user is root')
        tools.exit_if_not_root('oerptools-install')
        
        os_info = tools.get_os()
        #Old Ubuntu versions have a suffix in postgresql init script
        posgresql_init_suffix = ''
        if os_info['os'] == 'Linux' and os_info['version'][0] == 'Ubuntu':
            if os_info['version'][1] in ('10.04','10.10'):
                postgresql_init_suffix = '-8.4'
        
        
        _logger.info('')
        _logger.info('Please check the following information before continuing.')
        _logger.info('=========================================================')
        
        _logger.info('')
        _logger.info('System info')
        _logger.info('-----------')
        #Check system variables
        hostname = tools.get_hostname()
        _logger.info('Hostname: %s' % hostname[0])
        if not hostname[1]:
            _logger.warning('FQDN unknown, he hostname may not be properly set.')
        else:
            _logger.info('FQDN: %s' % hostname[1])
        
        _logger.info('Time and date: %s' % datetime.datetime.today().strftime('%Y/%m/%d %H:%M:%S'))
        #TODO: list installed and default locale
        
        _logger.info('')
        _logger.info('Installation info')
        _logger.info('-----------------')
        
        installation_type = config.params['installation_type']
        if installation_type == 'dev':
            _logger.info('Installation type: development station')
            if not 'user' in config.params:
                user = pwd.getpwuid(os.getuid()).pw_name
                if user == 'root':
                    _logger.error('No user specified for dev intallation, current user is root, can\'t install with root. Exiting.')
                    return False
                else:
                    _logger.warning('No user specified for dev intallation, using current user: %s' % user)
            else:
                user = config.params['user']
                try:
                    pw = pwd.getpwnam(user)
                except:
                    _logger.error('User unknown (%s). Exiting.' % user)
                    return False
                else:
                    _logger.info('User: %s' % config.params['user'])
                
        elif installation_type == 'server':
            _logger.info('Installation type: production server')
            user = 'openerp'
        else:
            _logger.error('Installation type unknown: %s' % installation_type)
            return False
        
        _logger.info('')
        _logger.info('Addons installation:')
        _logger.info('--------------------')
        
        install_openobject_addons = config.params['install_openobject_addons']
        if install_openobject_addons:
            _logger.info('Install openobject-addons: YES')
        else:
            _logger.info('Install openobject-addons: NO')
        install_openerp_ccorp_addons = config.params['install_openerp_ccorp_addons']
        if install_openerp_ccorp_addons:
            _logger.info('Install openerp-ccorp-addons: YES')
        else:
            _logger.info('Install openerp-ccorp-addons: NO')
        install_openerp_costa_rica = config.params['install_openerp_costa_rica']
        if install_openerp_costa_rica:
            _logger.info('Install openerp-costa-rica: YES')
        else:
            _logger.info('Install openerp-costa-rica: NO')
        
        _logger.info('')
        _logger.info('Please review the values above and confirm accordingly.')
        answer = False
        while not answer:
            answer = raw_input('Are the configuration values correct (y/n)? ')
            if re.match(r'^y$|^yes$', answer, flags=re.IGNORECASE):
                answer = 'y'
            elif re.match(r'^n$|^no$', answer, flags=re.IGNORECASE):
                answer = 'n'
                _logger.error('The configuration values are incorrect. Please correct any configuration error and run the script again.')
                return False
            else:
                answer = False
        
        _logger.info('Setting the OpenERP admin password.')
        # Get admin password
        admin_password = False
        while not admin_password:
            admin_password = getpass.getpass('Enter OpenERP admin password: ')
            if not admin_password == getpass.getpass('Confirm OpenERP admin password: '):
                _logger.error('Passwords don\'t match. Try again.')
                admin_password = False
        
        _logger.info('Setting the PostgreSQL admin password.')
        # Set postgres admin password
        postgres_password = False
        if installation_type == 'dev':
            answer = False
            while not answer:
                answer = raw_input('Do you want to change PostgreSQL admin password (Y/n)? ')
                if answer == '':
                    answer = 'y'
                elif re.match(r'^y$|^yes$', answer, flags=re.IGNORECASE):
                    answer = 'y'
                elif re.match(r'^n$|^no$', answer, flags=re.IGNORECASE):
                    answer = 'n'
                else:
                    answer = False
            if answer == 'y':
                while not postgres_password:
                    postgres_password = getpass.getpass('Enter PostgreSQL\'s admin password: ')
                    if not postgres_password == getpass.getpass('Confirm PostgreSQL\'s admin password: '):
                        _logger.error('Passwords don\'t match. Try again.')
                        postgres_password  = False
        
        #Update config file with new values
        
        print config.params.params
        
        
    
        return True

oerp_server = oerpServer()
