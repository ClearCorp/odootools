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

'''
Description: Install apache
'''

import logging
_logger = logging.getLogger('oerptools.lib.apache')

import os
from oerptools.lib import tools

def apache_install():
    os_version = tools.get_os()
    if os_version['os'] == 'Linux':
        if (os_version['version'][0] == 'Ubuntu') or (os_version['version'][0] == 'LinuxMint'):
            return ubuntu_apache_install(string)
        elif os_version['version'][0] == 'arch':
            return arch_apache_install()
    return False

def ubuntu_apache_install():
    _logger.info('Installing Apache web server')
    if not tools.ubuntu_install_package(['apache2']):
        _logger.error('Failed to install apache package. Exiting.')
        return False
    _logger.info('Making SSL certificate for Apache')
    if tools.exec_command('make-ssl-cert generate-default-snakeoil', as_root=True):
        _logger.warning('Failed to make SSL certificates.')
        # Snakeoil certificate files:
        # /usr/share/ssl-cert/ssleay.cnf
        # /etc/ssl/certs/ssl-cert-snakeoil.pem
        # /etc/ssl/private/ssl-cert-snakeoil.key
    _logger.info('Enabling Apache modules and sites')
    if tools.exec_command('a2enmod ssl rewrite suexec include proxy proxy_http proxy_connect proxy_ftp headers', as_root=True):
        _logger.error('Failed to enable Apache modules. Exiting.')
        return False
    if tools.exec_command('a2ensite 000-default default-ssl', as_root=True):
        _logger.error('Failed to enable Apache sites. Exiting.')
        return False
    if tools.exec_command('/etc/init.d/apache2 restart', as_root=True):
        _logger.warning('Failed to restart apache. Exiting.')
        return False
    return True

def arch_apache_install():
    _logger.info('Installing Apache web server')
    if tools.arch_install_repo_package(['apache']):
        _logger.error('Failed to install apache package. Exiting.')
        return False
    return True
    #TODO: configuration for apache in arch

def apache_restart():
    os_version = tools.get_os()
    if os_version['os'] == 'Linux':
        if (os_version['version'][0] == 'Ubuntu') or (os_version['version'][0] == 'LinuxMint'):
            return ubuntu_apache_restart()
        elif os_version['version'][0] == 'arch':
            return arch_apache_restart()
    return False

def ubuntu_apache_restart():
    _logger.info('Restarting Apache web server')
    if tools.exec_command('/etc/init.d/apache2 restart', as_root=True):
        _logger.error('Failed to restart Apache. Exiting.')
        return False
    return True

def arch_apache_restart():
    _logger.info('Restarting Apache web server')
    if tools.exec_command('systemctl restart httpd', as_root=True):
        _logger.error('Failed to restart Apache. Exiting.')
        return False
    return True

