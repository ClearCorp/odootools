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

import os, datetime, pwd, grp, getpass, re, tempfile
import logging
from odootools.lib import config, git_lib, tools, apache, phppgadmin

_logger = logging.getLogger('odootools.odoo.server')

class odooServer(object):
    
    def __init__(self, instance=None):
        self._os_info = tools.get_os()
        self._postgresql_version = ''
        if self._os_info['os'] == 'Linux' and self._os_info['version'][0] == 'Ubuntu':
            #Support for previous LTS
            if self._os_info['version'][1] == '12.04':
                self._postgresql_version = '9.1'
            #Support for versions between both LTS version
            elif self._os_info['version'][1] < '14.04':
                self._postgresql_version = '9.1'
            #Support for current LTS
            elif self._os_info['version'][1] == '14.04':
                self._postgresql_version = '9.3'
            else:
                self._postgresql_version = '9.3' #This should fail unsupported version
        # TODO check versions for Linux Mint and Arch Linux
        elif self._os_info['os'] == 'Linux' and self._os_info['version'][0] == 'LinuxMint':
            #Support for previous LTS
            if self._os_info['version'][1] == '13':
                self._postgresql_version = '9.1'
            #Support for versions between both LTS version
            elif self._os_info['version'][1] < '17':
                self._postgresql_version = '9.1'
            #Support for current LTS
            elif self._os_info['version'][1] == '17':
                self._postgresql_version = '9.3'
            else:
                self._postgresql_version = '9.3' #This should fail unsupported version
        elif self._os_info['os'] == 'Linux' and self._os_info['version'][0] == 'arch':
            self._postgresql_version = '9.1'

        if instance:
            _logger.debug('Server initialized with instance: %s' % instance)
            _logger.debug('Branch: %s' % instance._branch)
            self._branch = instance._branch
        else:
            _logger.debug('Server initialized without instance: %s' % instance)
            self._branch = config.params['branch'] or '8.0'
        
        self._installation_type = config.params[self._branch+'_installation_type'] or config.params['installation_type'] or 'dev'
        self._user = config.params[self._branch+'_user'] or config.params['user'] or None

        if 'install_odoo_clearcorp' in config.params:
            self._install_odoo_clearcorp = config.params['install_odoo_clearcorp']
        elif self._branch+'_install_odoo_clearcorp' in config.params:
            self._install_odoo_clearcorp = config.params[self._branch+'_install_odoo_clearcorp']
        else:
            self._install_odoo_clearcorp = True

        if 'install_odoo_costa_rica' in config.params:
            self._install_odoo_costa_rica = config.params['install_odoo_costa_rica']
        elif self._branch+'_install_odoo_costa_rica' in config.params:
            self._install_odoo_costa_rica = config.params[self._branch+'_install_odoo_costa_rica']
        else:
            self._install_odoo_costa_rica = True

        if self._branch+'_update_postgres_hba' in config.params:
            self._update_postgres_hba = config.params[self._branch+'_update_postgres_hba']
        elif 'update_postgres_hba' in config.params:
            self._update_postgres_hba = config.params['update_postgres_hba']
        else:
            self._update_postgres_hba = True

        if self._branch+'_create_postgres_user' in config.params:
            self._create_postgres_user = config.params[self._branch+'_create_postgres_user']
        elif 'create_postgres_user' in config.params:
            self._create_postgres_user = config.params['create_postgres_user']
        else:
            self._create_postgres_user = True

        if self._branch+'_install_apache' in config.params:
            self._install_apache = config.params[self._branch+'_install_apache']
        elif 'install_apache' in config.params:
            self._install_apache = config.params['install_apache']
        else:
            self._install_apache = True

        self._admin_password = config.params[self._branch+'_admin_password'] or config.params['admin_password'] or None
        self._postgresql_password = config.params[self._branch+'_postgresql_password'] or config.params['postgresql_password'] or None
        return super(odooServer, self).__init__()

    def _add_odoo_user(self):
        try:
            group = grp.getgrnam('odoo')
        except:
            _logger.info('odoo group doesn\'t exist, creating group.')
            # TODO: no addgroup in arch
            tools.exec_command('addgroup odoo', as_root=True)
            group = False
        else:
            _logger.debug('odoo group already exists.')

        try:
            pw = pwd.getpwnam(self._user)
        except:
            _logger.info('Creating user: (%s)' % self._user)
            tools.exec_command('adduser --system --home /var/run/odoo --no-create-home --ingroup odoo %s' % self._user, as_root=True)
        else:
            _logger.info('User %s already exists, adding to odoo group.' % self._user)
            tools.exec_command('adduser %s odoo' % self._user, as_root=True)

        return True

    #Todo check packages
    def get_packages_distro_match(self, distro):
        match = {
            'ubuntu': {
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
                'wget':                     'wget',
                'poppler-utils':            'poppler-utils'
            },

            'arch': {
                'repo': {
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
                    'wget':                     'wget',
                    'poppler-utils':            'poppler-utils' # Needs review on arch
                },
                'aur': {
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

    def _install_python_libs(self):
        _logger.info('Installing the required packages and python libraries for Odoo.')

        packages = []

        # Packages need by the installer
        packages.append('python-setuptools')
        packages.append('wget')

        # Packages for 7.0
        if self._branch == '7.0':
            packages += [
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
                'poppler-utils',
            ]
            
            # Packages for 8.0
        if self._branch == '8.0' or self._branch == 'trunk':
            packages += [
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
                'poppler-utils',
            ]

        # Test distro and call appropriate function
        if self._os_info and self._os_info['os'] == 'Linux':
            if (self._os_info['version'][0] == 'Ubuntu') or (self._os_info['version'][0] == 'LinuxMint'):
                return self._ubuntu_install_python_libs(packages)
            elif self._os_info['version'][0] == 'arch':
                return self._arch_install_python_libs(packages)
        _logger.error('Can\'t install python libraries in this OS: %s. Exiting.' % self._os_info['version'][0])
        return False

    def _ubuntu_install_python_libs(self, packages):
        #Initialize packages match
        distro_match_packages = self.get_packages_distro_match('ubuntu')

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
        return tools.ubuntu_install_package(distro_packages)

    def _arch_install_python_libs(self, packages):
        #Initialize packages match
        distro_match_packages = self.get_packages_distro_match('arch')

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
        error = False
        if not tools.arch_install_repo_package(distro_packages):
            _logger.warning('Failed to install some repo packages. This can render the OpenERP installation unusable.')
            error = True

        _logger.info('Installing packages from AUR.')
        _logger.debug('Packages: %s' % str(aur_packages))
        if not tools.arch_install_repo_package(aur_packages):
            _logger.warning('Failed to install some AUR packages. This can render the OpenERP installation unusable.')
            error = True

        return not error

    def _install_postgresql(self):
        _logger.info('Installing PostgreSQL.')
        # Test distro and call appropriate function
        if self._os_info and self._os_info['os'] == 'Linux':
            if (self._os_info['version'][0] == 'Ubuntu') or (self._os_info['version'][0] == 'LinuxMint'):
                return self._ubuntu_install_postgresql()
            elif self._os_info['version'][0] == 'arch':
                return self._arch_install_postgresql()
        _logger.error('Can\'t install python libraries in this OS: %s. Exiting.' % self._os_info['version'][0])
        return False

    def _ubuntu_install_postgresql(self):
        return tools.ubuntu_install_package(['postgresql'])

    def _arch_install_postgresql(self):
        #TODO: change some of this calls with a python way to do it (because of perms)
        if os.path.isdir('/var/lib/postgres/data'):
            _logger.info('PostgreSQL appears to be already configured. Skipping.')
            return False

        if tools.arch_install_package(['postgresql']):
            _logger.error('Failed to install PostgreSQL. Exiting.')
            return False
        if tools.exec_command('systemd-tmpfiles --create postgresql.conf', as_root=True):
            _logger.error('Failed to configure PostgreSQL systemd script. Exiting.')
            return False
        if tools.exec_command('mkdir /var/lib/postgres/data', as_root=True):
            _logger.error('Failed to create PostgreSQL data directory. Exiting.')
            return False
        if tools.exec_command('chown -c postgres:postgres /var/lib/postgres/data', as_root=True):
            _logger.error('Failed to set PostgreSQL data directory permisions. Exiting.')
            return False
        if tools.exec_command('sudo -i -u postgres initdb -D \'/var/lib/postgres/data\''):
            _logger.error('Failed to init PostgreSQL database. Exiting.')
            return False
        if tools.exec_command('systemctl enable postgresql', as_root=True):
            _logger.error('Failed to enable PostgreSQL init script. Exiting.')
            return False
        if tools.exec_command('systemctl start postgresql', as_root=True):
            _logger.error('Failed to start PostgreSQL. Exiting.')
            return False
        return True

    def _do_update_postgres_hba(self):
        _logger.info('Updating PostgreSQL pg_hba.conf file.')
        # Test distro and call appropriate function
        if self._os_info and self._os_info['os'] == 'Linux':
            if (self._os_info['version'][0] == 'Ubuntu') or (self._os_info['version'][0] == 'LinuxMint'):
                return self._ubuntu_do_update_postgres_hba()
            elif self._os_info['version'][0] == 'arch':
                return self._arch_do_update_postgres_hba()
        _logger.error('Can\'t update PostgreSQL pg_hba.conf in this OS: %s. Exiting.' % self._os_info['version'][0])
        return False

    def _ubuntu_do_update_postgres_hba(self):
        #TODO: change sed command with python lib to do the change (be carefull with the user perms)
        if tools.exec_command("sed -i 's/\(local[[:space:]]*all[[:space:]]*all[[:space:]]*\)\(ident[[:space:]]*sameuser\)/\1md5/g' /etc/postgresql/%s/main/pg_hba.conf" % self._postgresql_version, as_root=True):
            _logger.error('Failed to set PostgreSQL pg_hba.conf file. Exiting.')
            return False
        if tools.exec_command('service postgresql restart', as_root=True):
            _logger.error('Failed to start PostgreSQL. Exiting.')
            return False
        return True

    def _arch_do_update_postgres_hba(self):
        #TODO: lp:1133383 change sed command with python lib to do the change (be carefull with the user perms)
        #if tools.exec_command("sed -i 's/\(local[[:space:]]*all[[:space:]]*all[[:space:]]*\)\(ident[[:space:]]*sameuser\)/\1md5/g' /etc/postgresql/%s/main/pg_hba.conf" % self._postgresql_version, as_root=True):
        #    _logger.error('Failed to set PostgreSQL pg_hba.conf file. Exiting.')
        #    return False
        #if tools.exec_command('/etc/init.d/postgresql%s restart' % self._postgresql_init_suffix, as_root=True)
        #    _logger.error('Failed to start PostgreSQL. Exiting.')
        #    return False
        return True

    def _add_postgresql_user(self):
        _logger.info('Adding PostgreSQL user: %s.' % self._user)
        if tools.exec_command('sudo -u postgres createuser %s --superuser --createdb --no-createrole' % self._user):
            _logger.error('Failed to add PostgreSQL user. Exiting.')
            return False
        if tools.exec_command('sudo -u postgres psql template1 -U postgres -c "alter user \\"%s\\" with password \'%s\'"' % (self._user, self._admin_password)):
            _logger.error('Failed to set PostgreSQL user password. Exiting.')
            return False
        return True

    def _change_postgresql_admin_password(self):
        _logger.info('Changing PostgreSQL admin password.')
        if tools.exec_command('sudo -u postgres psql template1 -U postgres -c "alter user postgres with password \'%s\'"' % self._postgresql_password):
            _logger.error('Failed to set PostgreSQL admin password. Exiting.')
            return False
        return True

    def change_perms(self):
        _logger.debug('User: %s' % self._user)
        if os.path.isdir('/srv/odoo'):
            if tools.exec_command('chown -R %s:odoo /srv/odoo' % self._user, as_root=True):
                _logger.warning('Failed to set /srv/odoo owner. Skipping.')
            if tools.exec_command('chmod -R g+w /srv/odoo', as_root=True):
                _logger.warning('Failed to set /srv/odoo perms. Skipping.')
        if os.path.isdir('/var/log/odoo'):
            if tools.exec_command('chown -R %s:odoo /var/log/odoo' % self._user, as_root=True):
                _logger.warning('Failed to set /var/log/odoo owner. Skipping.')
            if tools.exec_command('chmod -R g+w /var/log/odoo', as_root=True):
                _logger.warning('Failed to set /var/log/odoo perms. Skipping.')
        if os.path.isdir('/var/run/odoo'):
            if tools.exec_command('chown -R %s:odoo /var/run/odoo' % self._user, as_root=True):
                _logger.warning('Failed to set /var/run/odoo owner. Skipping.')
            if tools.exec_command('chmod -R g+w /var/run/odoo', as_root=True):
                _logger.warning('Failed to set /var/run/odoo perms. Skipping.')
        if os.path.isdir('/etc/odoo'):
            if tools.exec_command('chown -R %s:odoo /etc/odoo' % self._user, as_root=True):
                _logger.warning('Failed to set /etc/odoo owner. Skipping.')

        return True

    def _download_odoo_repo(self):
        if os.path.isdir('/srv/odoo'):
            _logger.warning('/srv/odoo already exists. Not downloading repo.')
            return False

        _logger.info('Creating the directory structure.')
        if tools.exec_command('mkdir -p /srv/odoo/%s/instances' % self._branch, as_root=True):
            _logger.error('Failed to create the odoo directory structure. Exiting.')
            return False
        if tools.exec_command('mkdir -p /srv/odoo/%s/src' % self._branch, as_root=True):
            _logger.error('Failed to create the odoo src directory structure. Exiting.')
            return False
        cwd = os.getcwd()
        os.chdir('/srv/odoo/%s/src/' % self._branch)
        _logger.info('Cloning the latest Odoo git repository from https://github.com/CLEARCORP/odoo.git latest %s branch.' % self._branch)
        repo = git_lib.git_clone('https://github.com/CLEARCORP/odoo.git', 'odoo', branch=self._branch)
        os.chdir(cwd)
        _logger.info('Cloning finished.')
        return True

    def _download_git_repo(self, source, name):
        if not os.path.isdir('/srv/odoo/%s/src/' % self._branch):
            _logger.warning('/srv/odoo/%s/src/ do not exists. Not cloning repo.' % self._branch)
            return False
        cwd = os.getcwd()
        os.chdir('/srv/odoo/%s/src/' % self._branch)
        _logger.info('Cloning from %s latest %s branch.' % (source, self._branch))
        repo = git_lib.git_clone(source, name, branch=self._branch)
        os.chdir(cwd)
        _logger.info('Cloning finished.')
        return True

    def _download_odoo(self, modules_to_install):
        _logger.info('Downloading latest Odoo %s release.' % self._branch)
        if os.path.isdir('/srv/odoo'):
            _logger.info('Odoo repo already exists.')
            repo_downloaded = True
        else:
            repo_downloaded = self._download_odoo_repo()

        self.change_perms()

        if 'odoo-clearcorp' in modules_to_install and modules_to_install['odoo-clearcorp']:
            self._download_git_repo('https://github.com/CLEARCORP/odoo-clearcorp.git', 'odoo-clearcorp')
        if 'odoo-costa-rica' in modules_to_install and modules_to_install['odoo-costa-rica']:
            self._download_git_repo('https://github.com/CLEARCORP/odoo-costa-rica.git', 'odoo-costa-rica')
        self.change_perms()
        return True

    def _config_odoo_version(self):
        _logger.info('Configuring Odoo %s' % self._branch)
        cwd = os.getcwd()

        # Odoo Server bin
        _logger.debug('Copy bin script skeleton to /etc')
        if tools.exec_command('mkdir -p /etc/odoo/%s/server/' % self._branch, as_root=True):
            _logger.error('Failed to make /etc/odoo/%s/server/ directory. Exiting.' % self._branch)
            return False
        if tools.exec_command('cp %s/odootools/odoo/static/bin/server-bin-%s-skeleton /etc/odoo/%s/server/bin-skeleton' % (config.params['odootools_path'], self._branch, self._branch), as_root=True):
            _logger.error('Failed to copy bin skeleton. Exiting.')
            return False
        if tools.exec_command('sed -i "s#@BRANCH@#%s#g" /etc/odoo/%s/server/bin-skeleton' % (self._branch, self._branch), as_root=True): # TODO: check sed command
            _logger.error('Failed to config bin skeleton. Exiting.')
            return False

        # Odoo Server init
        if tools.exec_command('cp %s/odootools/odoo/static/init/server-init-%s-skeleton /etc/odoo/%s/server/init-skeleton' % (config.params['odootools_path'], self._branch, self._branch), as_root=True):
            _logger.error('Failed to copy init skeleton. Exiting.')
            return False
        if tools.exec_command('sed -i "s#@PATH@#/usr/local#g" /etc/odoo/%s/server/init-skeleton' % self._branch, as_root=True):
            _logger.error('Failed to config init skeleton. Exiting.')
            return False
        if tools.exec_command('sed -i "s#@BRANCH@#%s#g" /etc/odoo/%s/server/init-skeleton' % (self._branch, self._branch), as_root=True):
            _logger.error('Failed to config init skeleton. Exiting.')
            return False
        if self._installation_type == 'dev':
            if tools.exec_command('sed -i "s#@USER@#%s#g" /etc/odoo/%s/server/init-skeleton' % (self._user, self._branch), as_root=True):
                _logger.error('Failed to config init skeleton. Exiting.')
                return False
            if tools.exec_command('sed -i "s#@DBFILTER@#\${SERVERNAME}_.*#g" /etc/odoo/%s/server/init-skeleton' % self._branch, as_root=True):
                _logger.error('Failed to config init skeleton. Exiting.')
                return False
        else:
            if tools.exec_command('sed -i "s#@DBFILTER@#.*#g" /etc/odoo/%s/server/init-skeleton' % self._branch, as_root=True):
                _logger.error('Failed to config init skeleton. Exiting.')
                return False
        # Odoo Server config
        if tools.exec_command('cp %s/odootools/odoo/static/conf/server.conf-%s-skeleton /etc/odoo/%s/server/conf-skeleton' % (config.params['odootools_path'], self._branch, self._branch), as_root=True):
            _logger.error('Failed to copy conf skeleton. Exiting.')
            return False
        if tools.exec_command('sed -i "s#@BRANCH@#%s#g" /etc/odoo/%s/server/conf-skeleton' % (self._branch, self._branch), as_root=True):
            _logger.error('Failed to config init skeleton. Exiting.')
            return False
        if self._installation_type == 'dev':
            if tools.exec_command('sed -i "s#@INTERFACE@##g" /etc/odoo/%s/server/conf-skeleton' % self._branch, as_root=True):
                _logger.error('Failed to set interface in config skeleton. Exiting.')
                return False
        else:
            if tools.exec_command('sed -i "s#@INTERFACE@#localhost#g" /etc/odoo/%s/server/conf-skeleton' % self._branch, as_root=True):
                _logger.error('Failed to set interface in config skeleton. Exiting.')
                return False

        if tools.exec_command('mkdir -p /var/run/odoo', as_root=True):
            _logger.error('Failed to create /var/run/odoo. Exiting.')
            return False

        return True

    def _do_install_apache(self):
        os_version = tools.get_os()
        if os_version['os'] == 'Linux':
            if (os_version['version'][0] == 'Ubuntu') or (os_version['version'][0] == 'LinuxMint'):
                return self._ubuntu_do_install_apache()
            elif os_version['version'][0] == 'arch':
                return self._arch_do_install_apache()
        return False

    def _ubuntu_do_install_apache(self):
        if not apache.apache_install():
            _logger.error('Failed to install Apache. Exiting.')
            return False
        _logger.info('Configuring site config files.')
        if tools.exec_command('cp %s/odootools/odoo/static/apache/apache-odoo /etc/apache2/sites-available/odoo' % config.params['odootools_path'], as_root=True):
            _logger.warning('Failed copy Apache odoo site conf file.')
        if tools.exec_command('mkdir -p /etc/odoo/apache2/rewrites', as_root=True):
            _logger.warning('Failed make /etc/odoo/apache2/rewrites.')
        if tools.exec_command('cp %s/odootools/odoo/static/apache/apache-ssl-%s-skeleton /etc/odoo/apache2/ssl-%s-skeleton' % (config.params['odootools_path'], self._branch, self._branch), as_root=True):
            _logger.warning('Failed copy Apache rewrite skeleton.')
        if tools.exec_command('sed -i "s#ServerAdmin .*\\$#ServerAdmin support@clearcorp.co.cr\\n\\n\\tInclude /etc/apache2/sites-available/odoo#g" /etc/apache2/sites-available/000-default.conf', as_root=True):
            _logger.warning('Failed config Apache site.')
        if tools.exec_command('sed -i "s#ServerAdmin .*\\$#ServerAdmin support@clearcorp.co.cr\\n\\n\\tInclude /etc/odoo/apache2/rewrites#g" /etc/apache2/sites-available/default-ssl.conf', as_root=True):
            _logger.warning('Failed config Apache site.')
        if not apache.apache_restart():
            _logger.warning('Failed restart Apache.')
        return True

    def _arch_do_install_apache(self):
        if not apache.apache_install():
            _logger.error('Failed to install Apache. Exiting.')
            return False
        #TODO: lp:1133385 arch configuration of sites
        _logger.info('Configuring site config files.')
        #if tools.exec_command('cp %s/oerptools/oerp/static/apache/apache-erp /etc/apache2/sites-available/erp' % config.params['oerptools_path'], as_root=True):
        #    _logger.warning('Failed copy Apache erp site conf file.')
        if tools.exec_command('mkdir -p /etc/odoo/apache2/rewrites', as_root=True):
            _logger.warning('Failed make /etc/odoo/apache2/rewrites.')
        if tools.exec_command('cp %s/odootools/odoo/static/apache/apache-ssl-%s-skeleton /etc/odoo/apache2/ssl-%s-skeleton' % (config.params['odootools_path'], branch, branch), as_root=True):
            _logger.warning('Failed copy Apache rewrite skeleton.')
        #if tools.exec_command('sed -i "s/ServerAdmin .*$/ServerAdmin support@clearcorp.co.cr\n\n\tInclude \/etc\/apache2\/sites-available\/erp/g" /etc/apache2/sites-available/default', as_root=True):
        #    _logger.warning('Failed config Apache site.')
        #if tools.exec_command('sed -i "s/ServerAdmin .*$/ServerAdmin support@clearcorp.co.cr\n\n\tInclude \/etc\/openerp\/apache2\/rewrites/g" /etc/apache2/sites-available/default-ssl', as_root=True):
        #    _logger.warning('Failed config Apache site.')
        if apache.apache_restart():
            _logger.warning('Failed restart Apache.')
        return True

    def _set_logrotation(self):
        if tools.exec_command('cp %s/odootools/odoo/static/log/odoo.logrotate /etc/logrotate.d/' % config.params['odootools_path'], as_root=True):
            _logger.error('Failed to copy logrotate. Exiting.')
            return False
        return True

    def install(self):
        _logger.info('Odoo server installation started.')

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
        #TODO: lp:1133388 list installed and default locale

        _logger.info('')
        _logger.info('Installation info')
        _logger.info('-----------------')

        _logger.info('Odoo version (branch) to install: %s' % self._branch)

        if self._installation_type == 'dev':
            _logger.info('Installation type: development station')
        elif self._installation_type == 'server':
            _logger.info('Installation type: production server')
        else:
            _logger.error('Installation type unknown: %s' % self._installation_type)
            return False

        if self._installation_type == 'dev':
            if not self._user:
                self._user = pwd.getpwuid(os.getuid()).pw_name
                if self._user == 'root':
                    _logger.error('No user specified for dev intallation, current user is root, can\'t install with root. Exiting.')
                    return False
                else:
                    _logger.warning('No user specified for dev intallation, using current user: %s' % self._user)
            else:
                try:
                    pw = pwd.getpwnam(self._user)
                except:
                    _logger.error('User unknown (%s). Exiting.' % self._user)
                    return False
                else:
                    _logger.info('User: %s' % self._user)

        elif not self._user and self._installation_type == 'server':
            self._user = 'odoo'

        if not self._user:
            _logger.error('User unknown. Exiting.')
            return False
        elif pwd.getpwuid(os.getuid()).pw_name not in (self._user, 'root'):
            try:
                group = grp.getgrnam('odoo')
                if not pwd.getpwuid(os.getuid()).pw_name in group['gr_mem']:
                    _logger.error('Your user must be the user of installation (%s), root, or be part of odoo group. Exiting.')
                    return False
            except:
                _logger.error('Your user must be the user of installation (%s), root, or be part of odoo group. Exiting.')
                return False

        _logger.info('')
        _logger.info('Addons installation:')
        _logger.info('--------------------')

        if self._install_odoo_clearcorp:
            _logger.info('Install odoo-clearcorp: YES')
        else:
            _logger.info('Install odoo-clearcorp: NO')
        if self._install_odoo_costa_rica:
            _logger.info('Install odoo-costa-rica: YES')
        else:
            _logger.info('Install odoo-costa-rica: NO')

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

        _logger.info('Setting the Odoo admin password.')
        # Get admin password
        while not self._admin_password:
            self._admin_password = getpass.getpass('Enter Odoo admin password: ')
            if not self._admin_password == getpass.getpass('Confirm Odoo admin password: '):
                _logger.error('Passwords don\'t match. Try again.')
                self._admin_password = False

        _logger.info('Setting the PostgreSQL admin password.')
        # Set postgres admin password
        if not self._postgresql_password and self._installation_type == 'dev':
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
                while not self._postgresql_password:
                    self._postgresql_password = getpass.getpass('Enter PostgreSQL\'s admin password: ')
                    if not self._postgresql_password == getpass.getpass('Confirm PostgreSQL\'s admin password: '):
                        _logger.error('Passwords don\'t match. Try again.')
                        self._postgresql_password  = False

        #Update config file with new values
        values = {
            'odoo-install': {
                self._branch+'_installation_type': self._installation_type,
                self._branch+'_user': self._user,
                self._branch+'_install_odoo_clearcorp': self._install_odoo_clearcorp,
                self._branch+'_install_odoo_costa_rica': self._install_odoo_costa_rica,
                self._branch+'_admin_password': self._admin_password,
                self._branch+'_postgresql_password': self._postgresql_password,
            },
        }

        config_file_path = config.params.update_config_file_values(values)
        if config_file_path:
            _logger.info('Updated config file with installation values: %s' % config_file_path)
        else:
            _logger.warning('Failed to update config file with installation values.')


        # Preparing installation
        _logger.info('')
        _logger.info('Preparing Odoo installation')
        _logger.info('==============================')
        _logger.info('')

        self._add_odoo_user()
        self._install_python_libs()

        if not self._install_postgresql():
            _logger.error('Failed to install PostgreSQL. Exiting.')
            return False

        if self._update_postgres_hba:
            self._do_update_postgres_hba()

        if self._create_postgres_user:
            self._add_postgresql_user()

        if self._postgresql_password:
            self._change_postgresql_admin_password()

        modules_to_install = {
            'odoo-clearcorp': self._install_odoo_clearcorp,
            'odoo-costa-rica': self._install_odoo_costa_rica,
        }
        self._download_odoo(modules_to_install)

        self._config_odoo_version()

        self.change_perms()

        if self._install_apache:
            self._do_install_apache()
            phppgadmin.phppgadmin_install()

        self._set_logrotation()
        return True
