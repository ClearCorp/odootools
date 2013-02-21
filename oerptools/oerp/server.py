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

import os, datetime, pwd, grp, getpass, re, tempfile

from oerptools.lib import config, bzr, tools, apache

class oerpServer(object):
    def __init__(self):
        self._os_info = tools.get_os()
        #Old Ubuntu versions have a suffix in postgresql init script
        self._postgresql_init_suffix = ''
        self._postgresql_version = ''
        if self._os_info['os'] == 'Linux' and self._os_info['version'][0] == 'Ubuntu':
            if self._os_info['version'][1] in ('10.04','10.10'):
                self._postgresql_init_suffix = '-8.4'
            if self._os_info['version'][1] < '11.10':
                self._postgresql_version = '8.4'
            else:
                self._postgresql_version = '9.1'
        
        self._branch = config.params['branch'] or '7.0'
        self._installation_type = config.params[self._branch+'_installation_type'] or config.params['installation_type'] or'dev'
        self._user = config.params[self._branch+'_user'] or config.params['user'] or None
        self._install_openobject_addons = config.params[self._branch+'_install_openobject_addons'] or config.params['install_openobject_addons'] or True
        self._install_openerp_ccorp_addons = config.params[self._branch+'_install_openerp_ccorp_addons'] or config.params['install_openerp_ccorp_addons'] or True
        self._install_openerp_costa_rica = config.params[self._branch+'_install_openerp_costa_rica'] or config.params['install_openerp_costa_rica'] or True
        self._update_postgres_hba = config.params[self._branch+'_update_postgres_hba'] or config.params['update_postgres_hba'] or True
        self._create_postgres_user = config.params[self._branch+'_create_postgres_user'] or config.params['create_postgres_user'] or True
        self._install_apache = config.params[self._branch+'_install_apache'] or config.params['install_apache'] or True
        self._admin_password = config.params[self._branch+'_admin_password'] or config.params['admin_password'] or None
        self._postgresql_password = config.params[self._branch+'_postgresql_password'] or config.params['postgresql_password'] or None
        return super(oerpServer, self).__init__()
    
    def _add_openerp_user(self):
        try:
            group = grp.getgrnam('openerp')
        except:
            _logger.info('openerp group doesn\'t exist, creating group.')
            tools.exec_command('addgroup openerp', as_root=True)
            group = False
        else:
            _logger.debug('openerp group already exists.')
        
        try:
            pw = pwd.getpwnam(self._user)
        except:
            _logger.info('Creating user: (%s)' % self._user)
            tools.exec_command('adduser --system --home /var/run/openerp --no-create-home --ingroup openerp %s' % self._user, as_root=True)
        else:
            _logger.info('User %s already exists, adding to openerp group.' % self._user)
            tools.exec_command('adduser %s openerp' % self._user, as_root=True)
        
        return True
    
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
        _logger.info('Installing the required packages and python libraries for OpenERP.')
        
        packages = []
        
        # Packages need by the installer
        packages.append('python-setuptools')
        packages.append('wget')

        # Packages for 5.0
        if self._branch == '5.0':
            packages += [
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
            ]
        
        # Packages for 6.0
        if self._branch == '6.0':
            packages += [
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
            ]
        
        # Packages for 6.1
        if self._branch == '6.1':
            packages += [
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
            ]
        
        # Packages for 7.0
        if self._branch == '7.0' or self._branch == 'trunk':
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
            ]
        
        # Test distro and call appropriate function
        if self._os_info and self._os_info['os'] == 'Linux':
            if self._os_info['version'][0] == 'Ubuntu':
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
            if self._os_info['version'][0] == 'Ubuntu':
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
            if self._os_info['version'][0] == 'Ubuntu':
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
        if tools.exec_command('/etc/init.d/postgresql%s restart' % self._postgresql_init_suffix, as_root=True):
            _logger.error('Failed to start PostgreSQL. Exiting.')
            return False
        return True
    
    def _arch_do_update_postgres_hba(self):
        #TODO: change sed command with python lib to do the change (be carefull with the user perms)
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
        if os.path.isdir('/srv/openerp'):
            if tools.exec_command('chown -R %s:openerp /srv/openerp' % self._user, as_root=True):
                _logger.warning('Failed to set /srv/openerp owner. Skipping.')
            if tools.exec_command('chmod -R g+w /srv/openerp', as_root=True):
                _logger.warning('Failed to set /srv/openerp perms. Skipping.')
        if os.path.isdir('/var/log/openerp'):
            if tools.exec_command('chown -R %s:openerp /var/log/openerp' % self._user, as_root=True):
                _logger.warning('Failed to set /var/log/openerp owner. Skipping.')
            if tools.exec_command('chmod -R g+w /var/log/openerp', as_root=True):
                _logger.warning('Failed to set /var/log/openerp perms. Skipping.')
        if os.path.isdir('/var/run/openerp'):
            if tools.exec_command('chown -R %s:openerp /var/run/openerp' % self._user, as_root=True):
                _logger.warning('Failed to set /var/run/openerp owner. Skipping.')
            if tools.exec_command('chmod -R g+w /var/run/openerp', as_root=True):
                _logger.warning('Failed to set /var/run/openerp perms. Skipping.')
        if os.path.isdir('/etc/openerp'):
            if tools.exec_command('chown -R %s:openerp /etc/openerp' % self._user, as_root=True):
                _logger.warning('Failed to set /etc/openerp owner. Skipping.')
        
        #TODO: set instances addons dirs as executable, (really necessary?)
        #Old bash code:
        #if ls /srv/openerp/$branch/instances/*/addons > /dev/null 1>&2; then
        #    for x in $(ls -d /srv/openerp/$branch/instances/*/addons); do
        #        chmod +x $x >> $INSTALL_LOG_FILE;
        #    done
        #fi
        return True
    
    def _download_openerp_repo(self):
        bzr.bzr_initialize()
        if os.path.isdir('/srv/openerp'):
            _logger.warning('/srv/openerp already exists. Not downloading repo.')
            return False
        
        _logger.info('Downloading latest OpenERP bzr repository.')
        temp_dir = tempfile.mkdtemp(suffix='-oerptools')
        if tools.exec_command('mkdir -p /usr/local/src/oerptools/oerp', as_root=True):
            _logger.error('Failed to create /usr/local/src/oerptools/oerp dir. Exiting.')
            return False
        
        cwd = os.getcwd()
        os.chdir('/usr/local/src/oerptools/oerp')
        if not os.path.isfile('openerp.tgz'):
            if tools.exec_command('wget http://code.clearcorp.co.cr/bzr/openerp/openerp-src/bin/openerp.tgz', as_root=True):
                _logger.error('Failed to download repo tgz file. Exiting.')
                return False
        else:
            _logger.info('Repo file already exists, skipping download.')
        
        os.chdir('/srv')
        if tools.exec_command('tar xzf /usr/local/src/oerptools/oerp/openerp.tgz', as_root=True):
            _logger.error('Failed to extract repo tgz file. Exiting.')
            return False
        if os.path.exists('/srv/openerp/.bzr/repository/no-working-trees'):
            os.remove('/srv/openerp/.bzr/repository/no-working-trees')
        
        os.chdir(cwd)
        return True
    
    def _download_openerp_lp_branch(self, repo_downloaded, name, lp_project, lp_branch):
        bzr.bzr_initialize()
        _logger.info('Downloading %s latest %s release.' % (name, self._branch))
        
        if tools.exec_command('mkdir -p /srv/openerp/%s/src' % self._branch):
            _logger.error('Failed to make branch directory. Exiting.')
            return False
        
        if os.path.exists('/srv/openerp/%s/src/%s' % (self._branch, name)):
            _logger.info('%s/%s exists. Updating.' % (name, self._branch))
            bzr.bzr_pull('/srv/openerp/%s/src/%s' % (self._branch, name))
        elif repo_downloaded and name in ('openobject-server', 'openerp-web', 'openobject-addons'):
            bzr.bzr_branch('lp:~clearcorp-drivers/%s/%s' % (lp_project, lp_branch), '/srv/openerp/%s/src/%s' % (self._branch, name))
        else:
            cwd = os.getcwd()
            if tools.exec_command('mkdir -p /usr/local/src/oerptools/oerp/%s' % self._branch, as_root=True):
                _logger.error('Failed to make branch download directory. Exiting.')
                return False
            if not os.path.exists('/usr/local/src/oerptools/oerp/%s/%s.tgz' % (self._branch, name)):
                if tools.exec_command('wget http://code.clearcorp.co.cr/bzr/openerp/openerp-src/bin/%s/%s.tgz' % (self._branch, name), as_root=True):
                    _logger.error('Failed to download branch. Exiting.')
                    return False
            os.chdir('/usr/local/src/oerptools/oerp')
            if tools.exec_command('tar xzf %s/%s.tgz' % (self._branch, name), as_root=True):
                _logger.error('Failed to extract branch. Exiting.')
                return False
            bzr.bzr_branch('/usr/local/src/oerptools/oerp/%s' % self._branch, '/srv/openerp/%s/src/%s' % (self._branch, name))
            bzr.bzr_set_parent('/srv/openerp/%s/src/%s' % (self._branch, name), 'http://bazaar.launchpad.net/~clearcorp-drivers/%s/%s' % (lp_project, lp_branch))
            bzr.bzr_pull('/srv/openerp/%s/src/%s' % (self._branch, name))
        return True
    
    def _download_other_lp_branch(self, name, lp_project, lp_branch):
        bzr.bzr_initialize()
        _logger.info('Downloading %s latest %s release.' % (name, self._branch))
        if tools.exec_command('mkdir -p /srv/openerp/%s/src' % self._branch):
            _logger.error('Failed to make branch directory. Exiting.')
            return False
        if os.path.exists('/srv/openerp/%s/src/%s' % (self._branch, name)):
            _logger.info('%s/%s exists. Updating.' % (name, self._branch))
            bzr.bzr_pull('/srv/openerp/%s/src/%s' % (self._branch, name))
        else:
            bzr.bzr_branch('lp:%s/%s' % (lp_project, lp_branch), '/srv/openerp/%s/src/%s' % (self._branch, name))
        return True
    
    def _download_openerp(self, modules_to_install):
        _logger.info('Downloading latest OpenERP %s release.' % self._branch)
        if os.path.isdir('/srv/openerp'):
            _logger.info('OpenERP repo already exists.')
            repo_downloaded = True
        else:
            repo_downloaded = self._download_openerp_repo()
        
        self.change_perms()
        
        self._download_openerp_lp_branch(repo_downloaded, 'openobject-server', 'openobject-server', '%s-ccorp' % self._branch)
        if self._branch in ('5.0', '6.0'):
            self._download_openerp_lp_branch(repo_downloaded, 'openobject-client-web', 'openobject-client-web', '%s-ccorp' % self._branch)
        else:
            self._download_openerp_lp_branch(repo_downloaded, 'openerp-web', 'openerp-web', '%s-ccorp' % self._branch)
        if 'openobject-addons' in modules_to_install and modules_to_install['openobject-addons']:
            self._download_openerp_lp_branch(repo_downloaded, 'openobject-addons', 'openobject-addons', '%s-ccorp' % self._branch)
        if 'openerp-ccorp-addons' in modules_to_install and modules_to_install['openerp-ccorp-addons']:
            self._download_other_lp_branch('openerp-ccorp-addons', 'openerp-ccorp-addons', '%s' % self._branch)
        if 'openerp-costa-rica' in modules_to_install and modules_to_install['openerp-costa-rica']:
            self._download_other_lp_branch('openerp-costa-rica', 'openerp-costa-rica', '%s' % self._branch)
        self.change_perms()
        return True
    
    def _config_openerp_version(self):
        _logger.info('Configuring OpenERP %s' % self._branch)
        cwd = os.getcwd()
        
        # OpenERP Server bin
        _logger.debug('Copy bin script skeleton to /etc')
        if tools.exec_command('mkdir -p /etc/openerp/%s/server/' % self._branch, as_root=True):
            _logger.error('Failed to make /etc/openerp/%s/server/ directory. Exiting.' % self._branch)
            return False
        if tools.exec_command('cp %s/oerptools/oerp/static/bin/server-bin-%s-skeleton /etc/openerp/%s/server/bin-skeleton' % (config.params['oerptools_path'], self._branch, self._branch), as_root=True):
            _logger.error('Failed to copy bin skeleton. Exiting.')
            return False
        if tools.exec_command('sed -i "s#@BRANCH@#%s#g" /etc/openerp/%s/server/bin-skeleton' % (self._branch, self._branch), as_root=True):
            _logger.error('Failed to config bin skeleton. Exiting.')
            return False
        
        # OpenERP Server init
        if tools.exec_command('cp %s/oerptools/oerp/static/init/server-init-%s-skeleton /etc/openerp/%s/server/init-skeleton' % (config.params['oerptools_path'], self._branch, self._branch), as_root=True):
            _logger.error('Failed to copy init skeleton. Exiting.')
            return False
        if tools.exec_command('sed -i "s#@PATH@#/usr/local#g" /etc/openerp/%s/server/init-skeleton' % self._branch, as_root=True):
            _logger.error('Failed to config init skeleton. Exiting.')
            return False
        if tools.exec_command('sed -i "s#@USER@#%s#g" /etc/openerp/%s/server/init-skeleton' % (self._user, self._branch), as_root=True):
            _logger.error('Failed to config init skeleton. Exiting.')
            return False
        # OpenERP Server config
        if tools.exec_command('cp %s/oerptools/oerp/static/conf/server.conf-%s-skeleton /etc/openerp/%s/server/conf-skeleton' % (config.params['oerptools_path'], self._branch, self._branch), as_root=True):
            _logger.error('Failed to copy conf skeleton. Exiting.')
            return False
        if tools.exec_command('sed -i "s#@BRANCH@#%s#g" /etc/openerp/%s/server/conf-skeleton' % (self._branch, self._branch), as_root=True):
            _logger.error('Failed to config init skeleton. Exiting.')
            return False
        if self._installation_type == 'dev':
            if tools.exec_command('sed -i "s#@INTERFACE@##g" /etc/openerp/%s/server/conf-skeleton' % (self._branch, self._branch), as_root=True):
                _logger.error('Failed to set interface in config skeleton. Exiting.')
                return False
        else:
            if tools.exec_command('sed -i "s#@INTERFACE@#localhost#g" /etc/openerp/%s/server/conf-skeleton' % (self._branch, self._branch), as_root=True):
                _logger.error('Failed to set interface in config skeleton. Exiting.')
                return False
        
        if tools.exec_command('mkdir -p /var/run/openerp', as_root=True):
            _logger.error('Failed to create /var/run/openerp. Exiting.')
            return False
        
        if self._branch in ('5.0', '6.0'):
            # Make SSL certificates
            if tools.exec_command('mkdir -p /etc/openerp/ssl/private', as_root=True):
                _logger.error('Failed to create /etc/openerp/ssl/private. Exiting.')
                return False
            if tools.exec_command('mkdir -p /etc/openerp/ssl/signedcerts', as_root=True):
                _logger.error('Failed to create /etc/openerp/ssl/signedcerts. Exiting.')
                return False
            if tools.exec_command('mkdir -p /etc/openerp/ssl/servers', as_root=True):
                _logger.error('Failed to create /etc/openerp/ssl/servers. Exiting.')
                return False
            
            os.chdir('/etc/openerp/ssl')
            
            if tools.exec_command("echo '01' > serial  && touch index.txt", as_root=True):
                _logger.error('Failed to create SSL serial and index. Exiting.')
                return False
            if tools.exec_command('cp %s/oerptools/oerp/static/ssl/ca.cnf /etc/openerp/ssl/ca.cnf' % config.params['oerptools_path'], as_root=True):
                _logger.error('Failed to copy ca.cnf. Exiting.')
                return False
            if tools.exec_command('cp %s/oerptools/oerp/static/ssl/server.cnf /etc/openerp/ssl/server.cnf-skeleton' % config.params['oerptools_path'], as_root=True):
                _logger.error('Failed to copy server.cnf. Exiting.')
                return False
            if tools.exec_command('openssl req -x509 -newkey rsa:2048 -out cacert.pem -outform PEM -days 1825 -config ca.cnf -passout pass:%s' % self._admin_password, as_root=True):
                _logger.error('Failed to generate cacert.pem key. Exiting.')
                return False
            if tools.exec_command('openssl x509 -in cacert.pem -out cacert.crt', as_root=True):
                _logger.error('Failed to generate cacert.crt. Exiting.')
                return False
            
            os.chdir(cwd)
        return True

    def _do_install_apache():
        os_version = tools.get_os()
        if os_version['os'] == 'Linux':
            if os_version['version'][0] == 'Ubuntu':
                return _ubuntu_do_install_apache()
            elif os_version['version'][0] == 'arch':
                return _arch_do_install_apache()
        return False
    
    def _ubuntu_do_install_apache(self):
        if not apache.apache_install():
            _logger.error('Failed to install Apache. Exiting.')
            return False
        _logger.info('Configuring site config files.')
        if not tools.exec_command('cp %s/oerptools/oerp/static/apache/apache-erp /etc/apache2/sites-available/erp' % config.params['oerptools_path'], as_root=True)
            _logger.warning('Failed copy Apache erp site conf file.')
        if not tools.exec_command('mkdir -p /etc/openerp/apache2/rewrites', as_root=True)
            _logger.warning('Failed make /etc/openerp/apache2/rewrites.')
        if not tools.exec_command('cp %s/oerptools/oerp/static/apache/apache-ssl-%s-skeleton /etc/openerp/apache2/ssl-%s-skeleton' % (config.params['oerptools_path'], branch, branch), as_root=True)
            _logger.warning('Failed copy Apache rewrite skeleton.')
        if not tools.exec_command('sed -i "s/ServerAdmin .*$/ServerAdmin support@clearcorp.co.cr\n\n\tInclude \/etc\/apache2\/sites-available\/erp/g" /etc/apache2/sites-available/default', as_root=True)
            _logger.warning('Failed config Apache site.')
        if not tools.exec_command('sed -i "s/ServerAdmin .*$/ServerAdmin support@clearcorp.co.cr\n\n\tInclude \/etc\/openerp\/apache2\/rewrites/g" /etc/apache2/sites-available/default-ssl', as_root=True)
            _logger.warning('Failed config Apache site.')
        if not apache.apache_restart()
            _logger.warning('Failed restart Apache.')
        return True
    
    def _arch_do_install_apache(self):
        if not apache.apache_install():
            _logger.error('Failed to install Apache. Exiting.')
            return False
        #TODO: arch configuration of sites
        _logger.info('Configuring site config files.')
        #if not tools.exec_command('cp %s/oerptools/oerp/static/apache/apache-erp /etc/apache2/sites-available/erp' % config.params['oerptools_path'], as_root=True)
        #    _logger.warning('Failed copy Apache erp site conf file.')
        if not tools.exec_command('mkdir -p /etc/openerp/apache2/rewrites', as_root=True)
            _logger.warning('Failed make /etc/openerp/apache2/rewrites.')
        if not tools.exec_command('cp %s/oerptools/oerp/static/apache/apache-ssl-%s-skeleton /etc/openerp/apache2/ssl-%s-skeleton' % (config.params['oerptools_path'], branch, branch), as_root=True)
            _logger.warning('Failed copy Apache rewrite skeleton.')
        #if not tools.exec_command('sed -i "s/ServerAdmin .*$/ServerAdmin support@clearcorp.co.cr\n\n\tInclude \/etc\/apache2\/sites-available\/erp/g" /etc/apache2/sites-available/default', as_root=True)
        #    _logger.warning('Failed config Apache site.')
        #if not tools.exec_command('sed -i "s/ServerAdmin .*$/ServerAdmin support@clearcorp.co.cr\n\n\tInclude \/etc\/openerp\/apache2\/rewrites/g" /etc/apache2/sites-available/default-ssl', as_root=True)
        #    _logger.warning('Failed config Apache site.')
        if not apache.apache_restart()
            _logger.warning('Failed restart Apache.')
        return True
    
    def _set_logrotation(self):
        if not tools.exec_command('cp %s/oerptools/oerp/static/log/openerp.logrotate /etc/logrotate.d/', as_root=True)
            _logger.error('Failed to copy logrotate. Exiting.')
            return False
        return True
    
    def install(self):
        _logger.info('OpenERP server installation started.')
        
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
        
        _logger.info('OpenERP version (branch) to install: %s' % self._branch)
        
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
            self._user = 'openerp'
        
        if not self._user:
            _logger.error('User unknown. Exiting.')
            return False
        elif pwd.getpwuid(os.getuid()).pw_name not in (self._user, 'root'):
            try:
                group = grp.getgrnam('openerp')
                if not pwd.getpwuid(os.getuid()).pw_name in group['gr_mem']:
                    _logger.error('Your user must be the user of installation (%s), root, or be part of openerp group. Exiting.')
                    return False
            except:
                _logger.error('Your user must be the user of installation (%s), root, or be part of openerp group. Exiting.')
                return False
        
        _logger.info('')
        _logger.info('Addons installation:')
        _logger.info('--------------------')
        
        if self._install_openobject_addons:
            _logger.info('Install openobject-addons: YES')
        else:
            _logger.info('Install openobject-addons: NO')
        if self._install_openerp_ccorp_addons:
            _logger.info('Install openerp-ccorp-addons: YES')
        else:
            _logger.info('Install openerp-ccorp-addons: NO')
        if self._install_openerp_costa_rica:
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
        while not self._admin_password:
            self._admin_password = getpass.getpass('Enter OpenERP admin password: ')
            if not self._admin_password == getpass.getpass('Confirm OpenERP admin password: '):
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
            'oerp-install': {
                self._branch+'_installation_type': self._installation_type,
                self._branch+'_user': self._user,
                self._branch+'_install_openobject_addons': self._install_openobject_addons,
                self._branch+'_install_openerp_ccorp_addons': self._install_openerp_ccorp_addons,
                self._branch+'_install_openerp_costa_rica': self._install_openerp_costa_rica,
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
        _logger.info('Preparing OpenERP installation')
        _logger.info('==============================')
        _logger.info('')
        
        self._add_openerp_user()
        self._install_python_libs()
        
        if not bzr.bzr_install():
            _logger.error('Failed to install bzr (Bazaar VCS). Exiting.')
            return False
        
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
            'openobject-addons': self._install_openobject_addons,
            'openerp-ccorp-addons': self._install_openerp_ccorp_addons,
            'openerp-costa-rica': self._install_openerp_costa_rica,
        }
        self._download_openerp(modules_to_install)
        
        self._config_openerp_version()
        
        self.change_perms()
        
        if self._install_apache:
            self._do_install_apache()
        
        self._set_logrotation()
        
        return True

oerp_server = oerpServer()
