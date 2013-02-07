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

import os, datetime, pwd, grp, getpass, re

from oerptools.lib import config, bzr, tools

class oerpServer(object):
    
    def _add_openerp_user(self, user):
        try:
            group = grp.getgrnam('openerp')
        except:
            _logger.info('openerp group doesn\'t exist, creating group.')
            tools.exec_command('addgroup openerp', as_root=True)
            group = False
        else:
            _logger.debug('openerp group already exists.')
        
        try:
            pw = pwd.getpwnam(user)
        except:
            _logger.info('Creating user: (%s)' % user)
            tools.exec_command('adduser --system --home /var/run/openerp --no-create-home --ingroup openerp %s' % user, as_root=True)
        else:
            _logger.info('User %s already exists, adding to openerp group.' % user)
            tools.exec_command('adduser %s openerp' % user, as_root=True)
        
        return True
    
    def _install_python_libs(self, branch):
        
        Depends: adduser, python, postgresql-client, python-dateutil, python-docutils, python-feedparser, python-gdata, python-jinja2, python-ldap, python-libxslt1, python-lxml, python-mako, python-mock, python-openid, python-psutil, python-psycopg2, python-pybabel, python-pychart, python-pydot, python-pyparsing, python-reportlab, python-simplejson, python-tz, python-unittest2, python-vatnumber, python-vobject, python-webdav, python-werkzeug, python-xlwt, python-yaml, python-zsi
Recommends: graphviz, ghostscript, postgresql, python-imaging, python-matplotlib

        
        
        
    
    def install(self):
        _logger.info('OpenERP server installation started.')
        
        os_info = tools.get_os()
        #Old Ubuntu versions have a suffix in postgresql init script
        posgresql_init_suffix = ''
        if os_info['os'] == 'Linux' and os_info['version'][0] == 'Ubuntu':
            if os_info['version'][1] in ('10.04','10.10'):
                postgresql_init_suffix = '-8.4'
        
        branch = config.params['branch'] or '7.0'
        installation_type = config.params[branch+'_installation_type'] or 'dev'
        user = config.params[branch+'_user']
        install_openobject_addons = config.params[branch+'_install_openobject_addons'] or True
        install_openerp_ccorp_addons = config.params[branch+'_install_openerp_ccorp_addons'] or True
        install_openerp_costa_rica = config.params[branch+'_install_openerp_costa_rica'] or True
        
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
        
        _logger.info('OpenERP version (branch) to install: %s' % branch)
        
        if installation_type == 'dev':
            _logger.info('Installation type: development station')
        elif installation_type == 'server':
            _logger.info('Installation type: production server')
        else:
            _logger.error('Installation type unknown: %s' % installation_type)
            return False
        
        if installation_type == 'dev':
            if not user:
                user = pwd.getpwuid(os.getuid()).pw_name
                if user == 'root':
                    _logger.error('No user specified for dev intallation, current user is root, can\'t install with root. Exiting.')
                    return False
                else:
                    _logger.warning('No user specified for dev intallation, using current user: %s' % user)
            else:
                try:
                    pw = pwd.getpwnam(user)
                except:
                    _logger.error('User unknown (%s). Exiting.' % user)
                    return False
                else:
                    _logger.info('User: %s' % config.params['user'])
                
        elif not user and installation_type == 'server':
            user = 'openerp'
        
        if not user:
            _logger.error('User unknown. Exiting.')
            return False
        
        _logger.info('')
        _logger.info('Addons installation:')
        _logger.info('--------------------')
        
        if install_openobject_addons:
            _logger.info('Install openobject-addons: YES')
        else:
            _logger.info('Install openobject-addons: NO')
        if install_openerp_ccorp_addons:
            _logger.info('Install openerp-ccorp-addons: YES')
        else:
            _logger.info('Install openerp-ccorp-addons: NO')
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
        values = {
            'oerp-install': {
                branch+'_installation_type': installation_type,
                branch+'_user': user,
                branch+'_install_openobject_addons': install_openobject_addons,
                branch+'_install_openerp_ccorp_addons': install_openerp_ccorp_addons,
                branch+'_install_openerp_costa_rica': install_openerp_costa_rica,
                branch+'_admin_password': admin_password,
                branch+'_postgres_password': postgres_password,
            },
        }
        
        config_file_path = config.params.update_config_file_values(values)
        if config_file_path:
            _logger.info('Updated config file with installation values: %s' % config_file_path)
        else:
            _logger.warning('Failed to update config file with installation values.')
        
        
        # Preparing installation
        _logger.info('')
        _logger.info('Preparing OpenERP installation')
        _logger.info('==============================')
        _logger.info('')
        
        self._add_openerp_user(user)
        
    
        return True

oerp_server = oerpServer()
