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
    
    def get_packages_distro_match(self, distro):
        match = {
            'ubuntu' = {
                'ghostscript':              'ghostscript',
                'graphviz':                 'graphviz',
                'libjs-mochikit':           'libjs-mochikit',
                'libjs-mootools':           'libjs-mootools',
                'python-beaker':            'python-beaker',
                'python-cherrypy3':         'python-cherrypy3',
                'python-dateutil':          'python-dateutil',
                'python-docutils':          'python-docutils',
                'python-egenix':            'python-egenix-mxdatetime',
                'python-feedparser':        'python-feedparser',
                'python-formencode':        'python-formencode',
                'python-gdata':             'python-gdata',
                'python-imaging':           'python-imaging',
                'python-jinja2':            'python-jinja2',
                'python-ldap':              'python-ldap',
                'python-libxslt1':          'python-libxslt1',
                'python-lxml':              'python-lxml',
                'python-mako':              'python-mako',
                'python-matplotlib':        'python-matplotlib',
                'python-mock':              'python-mock',
                'python-openid':            'python-openid',
                'python-openssl':           'python-openssl',
                'python-psutil':            'python-psutil',
                'python-psycopg2':          'python-psycopg2',
                'python-pybabel':           'python-pybabel',
                'python-pychart':           'python-pychart',
                'python-pydot':             'python-pydot',
                'python-pyparsing':         'python-pyparsing',
                'python-reportlab':         'python-reportlab',
                'python-setuptools':        'python-setuptools',
                'python-simplejson':        'python-simplejson',
                'python-tz':                'python-tz',
                'python-unittest2':         'python-unittest2',
                'python-vatnumber':         'python-vatnumber',
                'python-vobject':           'python-vobject',
                'python-webdav':            'python-webdav',
                'python-werkzeug':          'python-werkzeug',
                'python-xlwt':              'python-xlwt',
                'python-yaml':              'python-yaml',
                'python-zsi':               'python-zsi',
                'tinymce':                  'tinymce',
            },
            
            'arch' = {
                'repo' = {
                    'ghostscript':              'ghostscript',
                    'graphviz':                 'graphviz',
                    'libjs-mochikit':           None,
                    'libjs-mootools':           'pycow',
                    'python-beaker':            'python2-beaker',
                    'python-cherrypy3':         'python2-cherrypy',
                    'python-dateutil':          'python2-dateutil',
                    'python-docutils':          'python2-docutils',
                    'python-egenix':            'python2-egenix-mx-base',
                    'python-feedparser':        'python2-feedparser',
                    'python-formencode':        'python2-formencode',
                    'python-gdata':             'python2-gdata',
                    'python-imaging':           'python2-imaging',
                    'python-jinja2':            'python2-jinja',
                    'python-ldap':              'python2-ldap',
                    'python-libxslt1':          'python2-lxml',
                    'python-lxml':              'python2-lxml',
                    'python-mako':              'python2-mako',
                    'python-matplotlib':        'python2-matplotlib',
                    'python-openssl':           'python2-pyopenssl',
                    'python-psutil':            'python2-psutil',
                    'python-psycopg2':          'python2-psycopg2',
                    'python-pybabel':           'python2-babel',
                    'python-pychart':           'python2-pychart',
                    'python-pyparsing':         'python2-pyparsing',
                    'python-reportlab':         'python2-reportlab',
                    'python-setuptools':        'python2-distribute',
                    'python-simplejson':        'python2-simplejson',
                    'python-tz':                'python2-pytz', 
                    'python-vobject':           'python2-vobject',
                    'python-werkzeug':          'python2-werkzeug',
                    'python-yaml':              'python2-yaml',
                    'tinymce':                  None,
                },
                'aur' = {
                    'python-mock':              'python2-mock',
                    'python-openid':            'python2-openid',
                    'python-pydot':             'pydot',
                    'python-unittest2':         'python2-unittest2',
                    'python-vatnumber':         'python2-vatnumber',
                    'python-webdav':            'python2-pywebdav',
                    'python-xlwt':              'python2-xlwt',
                    'python-zsi':               'zsi',
                }
            }
        }
        
        if distro in match:
            return match[distro]
        else:
            return False
    
    def _install_python_libs(self, branch, os_version):
        _logger.info('Installing the required packages and python libraries for OpenERP.')
        
        packages = []
        
        # Packages need by the installer
        packages.append('python-setuptools')

        # Packages for 5.0
        if branch == '5.0':
            packages.join([
                # Server
                # Dependencies
                'python-lxml',
                'python-psycopg2',
                'python-pychart',
                'python-pydot',
                'python-reportlab',
                'python-tz',
                'python-vobject',
                'python-egenix',
                # Recomended
                'graphviz',
                'ghostscript',
                'python-imaging',
                'python-libxslt1',      #Excel spreadsheets
                'python-matplotlib',
                'python-openssl',       #Extra for ssl ports
                'python-xlwt',          #Excel spreadsheets
                'python-pyparsing',
                # Web client
                # Dependencies
                'python-formencode',
                'python-pybabel',
                'python-simplejson',
                'python-pyparsing',
                'python2-cherrypy',
                #Recommended
                'libjs-mochikit',
                'libjs-mootools',
                'python-beaker',
                'tinymce',
            ])
        
        # Packages for 6.0
        if branch == '6.0':
            packages.join([
                # Server
                # Dependencies
                'python-lxml',
                'python-psycopg2',
                'python-pychart',
                'python-pydot',
                'python-reportlab',
                'python-tz',
                'python-vobject',
                'python-dateutil',
                'python-feedparser',
                'python-mako',
                'python-pyparsing',
                'python-yaml',
                # Recomended
                'graphviz',
                'ghostscript',
                'python-imaging',
                'python-libxslt1',      #Excel spreadsheets
                'python-matplotlib',
                'python-openssl',       #Extra for ssl ports
                'python-xlwt',          #Excel spreadsheets
                'python-webdav',        #For document-webdav
                # Web client
                # Dependencies
                'python-formencode',
                'python-pybabel',
                'python-simplejson',
                'python-pyparsing',
                'python2-cherrypy',
                #Recommended
            ])
        
        # Packages for 6.1
        if branch == '6.1':
            packages.join([
                # Server
                # Dependencies
                'python-lxml',
                'python-psycopg2',
                'python-pychart',
                'python-pydot',
                'python-reportlab',
                'python-tz',
                'python-vobject',
                'python-dateutil',
                'python-feedparser',
                'python-mako',
                'python-pyparsing',
                'python-yaml',
                'python-werkzeug',
                'python-zsi',
                # Recomended
                'graphviz',
                'ghostscript',
                'python-imaging',
                'python-libxslt1',      #Excel spreadsheets
                'python-matplotlib',
                'python-openssl',       #Extra for ssl ports
                'python-xlwt',          #Excel spreadsheets
                'python-webdav',        #For document-webdav
                'python-gdata',         #Google data parser
                'python-ldap',
                'python-openid',
                'python-vatnumber',
                'python-mock',          #For testing
                'python-unittest2',     #For testing
                # Web client
                # Dependencies
                'python-formencode',
                'python-pybabel',
                'python-simplejson',
                'python-pyparsing',
                # Recommended
            ])
        
        # Packages for 7.0
        if branch == '7.0' or branch == 'trunk':
            packages.join([
                # Dependencies
                'python-dateutil',
                'python-docutils',
                'python-feedparser',
                'python-gdata',         #Google data parser
                'python-jinja2',
                'python-ldap',
                'python-libxslt1',      #Excel spreadsheets
                'python-lxml',
                'python-mako',
                'python-mock',          #For testing
                'python-openid',
                'python-psutil',
                'python-psycopg2',
                'python-pybabel',
                'python-pychart',
                'python-pydot',
                'python-pyparsing',
                'python-reportlab',
                'python-simplejson',
                'python-tz',
                'python-unittest2',     #For testing
                'python-vatnumber',
                'python-vobject',
                'python-webdav',        #For document-webdav
                'python-werkzeug',
                'python-xlwt',          #Excel spreadsheets
                'python-yaml',
                'python-zsi',
                
                # Recomended
                'graphviz',
                'ghostscript',
                'python-imaging',
                'python-matplotlib',
            ])
        
        # Test distro and call appropriate function
        if os_version and os_version['os'] == 'Linux':
            if os_version['version'][0] == 'Ubuntu':
                return _ubuntu_install_python_libs(branch, packages)
            elif os_version['version'][0] == 'arch':
                return _arch_install_python_libs(branch, packages)
        _logger.error('Can\'t install python libraries in this OS: %s. Exiting.' % os_version['version'][0])
        return False
    
    def _ubuntu_install_python_libs(self, branch, packages):
        #Initialize packages match
        distro_match_packages = get_packages_distro_match('ubuntu')
        
        #Build definitive package list
        distro_packages = []
        for package in packages:
            if package in distro_match_packages:
                if distro_match_packages[package]:
                    distro_packages.append(distro_match_packages[package])
                #No package for this distro available
                else:
                    _logger.warning('No installable package for %s in Ubuntu. Please install it manually.' % package)
            else:
                _logger.warning('Package unknown: %s. Exiting.' % package)
        
        # Install packages
        result = tools.ubuntu_install_package(distro_packages)
        return result
    
    def _arch_install_python_libs(self, branch, packages):
        #Initialize packages match
        distro_match_packages = get_packages_distro_match('arch')
        
        #Build definitive package list
        distro_packages = []
        aur_packages = []
        for package in packages:
            if package in distro_match_packages['repo']:
                if distro_match_packages['repo'][package]:
                    distro_packages.append(distro_match_packages['repo'][package])
                #No package for this distro available
                else:
                    _logger.warning('No installable package for %s in Arch. Please install it manually.' % package)
            elif package in distro_match_packages['aur']:
                if distro_match_packages['aur'][package]:
                    aur_packages.append(distro_match_packages['aur'][package])
                #No package for this distro available
                else:
                    _logger.warning('No installable package for %s in Arch. Please install it manually.' % package)
            else:
                _logger.warning('Package unknown: %s. Exiting.' % package)
        
        # Install packages
        _logger.info('Installing packages with pacman.')
        _logger.debug('Packages: %s' % str(distro_packages))
        result = tools.arch_install_repo_package(distro_packages)
        error = False
        if != result:
            _logger.warning('Failed to install some repo packages. This can render the OpenERP installation unusable.')
            error = True
        
        _logger.info('Installing packages from AUR.')
        _logger.debug('Packages: %s' % str(aur_packages))
        result = tools.arch_install_repo_package(aur_packages)
        if not result:
            _logger.warning('Failed to install some AUR packages. This can render the OpenERP installation unusable.')
            error = True
        
        return not error
    
    def _install_postgresql(self, os_version):
        _logger.info('Installing PostgreSQL.')
        # Test distro and call appropriate function
        if os_version and os_version['os'] == 'Linux':
            if os_version['version'][0] == 'Ubuntu':
                return _ubuntu_install_postgresql()
            elif os_version['version'][0] == 'arch':
                return _arch_install_postgresql()
        _logger.error('Can\'t install python libraries in this OS: %s. Exiting.' % os_version['version'][0])
        return False
    
    def _ubuntu_install_postgresql(self):
        return tools.ubuntu_install_package(['postgresql'])
        
    def _arch_install_postgresql(self):
        return tools.arch_install_package(['postgresql'])
    
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
        self._install_python_libs(branch, os_info)
        
        result = bzr.bzr_install()
        if result != 0:
            _logger.error('Failed to install bzr (Bazaar VCS). Exiting.')
            return False
        
        result = self._install_postgresql()
        if result != 0:
            _logger.error('Failed to install PostgreSQL. Exiting.')
            return False
        
        
        
        return True

oerp_server = oerpServer()
