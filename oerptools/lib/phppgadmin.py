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
Description: Install phppgadmin
'''

import logging
_logger = logging.getLogger('oerptools.lib.phppgadmin')

import os
from oerptools.lib import tools

def phppgadmin_install():
    os_version = tools.get_os()
    if os_version['os'] == 'Linux':
        if os_version['version'][0] == 'Ubuntu':
            return ubuntu_phppgadmin_install()
        elif os_version['version'][0] == 'arch':
            return arch_phppgadmin_install()
    return False

def ubuntu_phppgadmin_install():
    _logger.info('Installing PostgreSQL Web administration interface (phppgadmin)')
    if tools.ubuntu_install_package(['phppgadmin']):
        _logger.error('Failed to install phppgadmin package. Exiting.')
        return False
    if tools.exec_command('sed -i "s/#\?[[:space:]]*\(deny from all.*\)/# deny from all/g" /etc/phppgadmin/apache.conf', as_root=True):
        _logger.error('Failed to configure phppgadmin apache file. Exiting.')
        return False
    if tools.exec_command('sed -i "s/[[:space:]]*allow from \(.*\)/# allow from \1/g" /etc/phppgadmin/apache.conf', as_root=True):
        _logger.error('Failed to configure phppgadmin apache file. Exiting.')
        return False
    if tools.exec_command('sed -i "s/#\?[[:space:]]*\(allow from all.*\)/allow from all/g" /etc/phppgadmin/apache.conf', as_root=True):
        _logger.error('Failed to configure phppgadmin apache file. Exiting.')
        return False
    if tools.exec_command('sed -i "s/#\?[[:space:]]*\(allow from all.*\)/allow from all/g" /etc/phppgadmin/apache.conf', as_root=True):
        _logger.error('Failed to configure phppgadmin apache file. Exiting.')
        return False
    if tools.exec_command('/etc/init.d/apache2 restart', as_root=True):
        _logger.warning('Failed to restart apache. Exiting.')
        return False
    return

def arch_phppgadmin_install():
    _logger.info('Installing PostgreSQL Web administration interface (phppgadmin)')
    if tools.arch_install_repo_package(['phppgadmin']):
        _logger.error('Failed to install phppgadmin package. Exiting.')
        return False
    #TODO: lp:1133345 configuration for phppgadmin in arch

